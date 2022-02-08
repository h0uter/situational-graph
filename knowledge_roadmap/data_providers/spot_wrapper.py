import os
import time
import subprocess
import numpy as np
import cv2
# from cv_bridge import CvBridge

from bosdyn.geometry import EulerZXY
from bosdyn.client import (
    power,
    create_standard_sdk,
    ResponseError,
    RpcError,
)
from bosdyn.client.async_tasks import AsyncPeriodicQuery, AsyncTasks
from bosdyn.client.frame_helpers import (
    BODY_FRAME_NAME,
    VISION_FRAME_NAME,
    ODOM_FRAME_NAME,
    get_odom_tform_body,
    get_vision_tform_body,
    add_edge_to_tree,
    get_a_tform_b,
)
import bosdyn.client.math_helpers as math_helpers
from bosdyn.client.robot_state import RobotStateClient
from bosdyn.client.robot_command import RobotCommandClient, RobotCommandBuilder
from bosdyn.client.power import PowerClient
from bosdyn.client.lease import LeaseClient, LeaseKeepAlive
from bosdyn.client.image import ImageClient, build_image_request
from bosdyn.client.graph_nav import GraphNavClient
from bosdyn.client.local_grid import LocalGridClient
from bosdyn.client.payload import PayloadClient
from bosdyn.client.payload_registration import PayloadRegistrationClient, PayloadRegistrationKeepAlive


from bosdyn.client.world_object import WorldObjectClient
from bosdyn.client.world_object import (
    make_add_world_object_req,
    make_change_world_object_req,
    make_delete_world_object_req,
)
from bosdyn.client.estop import EstopClient, EstopEndpoint, EstopKeepAlive
from bosdyn.api import (
    image_pb2,
    geometry_pb2,
    trajectory_pb2,
)
from bosdyn.api import basic_command_pb2
from bosdyn.api.spot import robot_command_pb2 as spot_command_pb2
from bosdyn.api import robot_command_pb2
from bosdyn.api.geometry_pb2 import SE2Velocity, SE2VelocityLimit, Vec2
from bosdyn.api.trajectory_pb2 import SE2Trajectory
import bosdyn.api.robot_state_pb2 as robot_state_proto
import bosdyn.api.payload_pb2 as payload_protos
import bosdyn.api.full_body_command_pb2 as full_body_command_proto
import bosdyn.api.payload_estimation_pb2 as payload_estimation_proto
from bosdyn.util import now_timestamp

from google.protobuf.timestamp_pb2 import Timestamp

"""List of image sources for periodic query"""
front_image_sources = [
    'frontleft_fisheye_image',
    'frontright_fisheye_image',
    'frontleft_depth',
    'frontright_depth',
]
side_image_sources = [
    'left_fisheye_image',
    'right_fisheye_image',
    'left_depth',
    'right_depth',
]
rear_image_sources = ['back_fisheye_image', 'back_depth']

OBSTACLE_BASE_PADDING = 0.5  # m
VELOCITY_BASE_SPEED = 0.5  # m/s
VELOCITY_BASE_ANGULAR = 0.8  # rad/sec
VELOCITY_CMD_DURATION = 0.6  # seconds
TRAJECTORY_CMD_DURATION = 30  # seconds
BASE_FRAME_NAME = ODOM_FRAME_NAME


class ASyncDataPoller(AsyncPeriodicQuery):
    """Class to get robot data at regular intervals."""

    def __init__(self,
                 name,
                 client,
                 logger,
                 rate,
                 callback,
                 client_method,
                 query_arguments={}):
        super(ASyncDataPoller, self).__init__(
            query_name=name,
            client=client,
            logger=logger,
            period_sec=1.0/max(rate, 1.0),
        )

        self._client_method = client_method
        self._query_arguments = query_arguments
        self._callback = None
        if rate > 0.0:
            self._callback = callback

    def _start_query(self):
        if self._callback is not None:
            callback_future = self._client_method(**self._query_arguments)
            callback_future.add_done_callback(self._callback)
            return callback_future


class AsyncIdle(AsyncPeriodicQuery):
    """
    Class to check if the robot is moving,
    and if not, command a stand with the set mobility parameters

    Attributes:
        client: The Client to a service on the robot
        logger: Logger object
        rate: Rate (Hz) to trigger the query
        spot_wrapper: A handle to the wrapper library
    """

    def __init__(self, client, logger, rate, spot_wrapper):
        super(AsyncIdle, self).__init__('idle', client, logger,
                                        period_sec=1.0/rate)
        self._spot_wrapper = spot_wrapper

    def _start_query(self):
        if self._spot_wrapper._last_command is None:
            return

        command_type, command_id = self._spot_wrapper._last_command

        if command_type == 'stand':
            self._spot_wrapper._is_sitting = False
            self._spot_wrapper._is_standing = False
            self._spot_wrapper._is_moving = False
            response = self._client.robot_command_feedback(command_id)
            if (response.feedback.synchronized_feedback.mobility_command_feedback.stand_feedback.status ==
                    basic_command_pb2.StandCommand.Feedback.STATUS_IS_STANDING):
                self._spot_wrapper._is_standing = True
                self._spot_wrapper._last_command = None
        elif command_type == 'sit':
            self._spot_wrapper._is_sitting = False
            self._spot_wrapper._is_standing = False
            self._spot_wrapper._is_moving = False
            response = self._client.robot_command_feedback(command_id)
            if (response.feedback.synchronized_feedback.mobility_command_feedback.sit_feedback.status ==
                    basic_command_pb2.SitCommand.Feedback.STATUS_IS_SITTING):
                self._spot_wrapper._is_sitting = True
                self._spot_wrapper._is_standing = False
                self._spot_wrapper._is_moving = False
                self._spot_wrapper._last_command = None
        elif command_type == 'motion':
            self._spot_wrapper._is_sitting = False
            self._spot_wrapper._is_standing = False
            self._spot_wrapper._is_moving = True
            response = self._client.robot_command_feedback(command_id)
            if (response.feedback.synchronized_feedback.mobility_command_feedback.se2_trajectory_feedback.status ==
                    basic_command_pb2.SE2TrajectoryCommand.Feedback.STATUS_AT_GOAL):
                self._spot_wrapper._is_sitting = False
                self._spot_wrapper._is_standing = True
                self._spot_wrapper._is_moving = False
                self._spot_wrapper._last_command = None
        elif command_type == 'payload':
            self._spot_wrapper._is_moving = True
            response = self._client.robot_command_feedback(command_id)

            status = response.feedback.full_body_feedback.payload_estimation_feedback.status
            if (status == payload_estimation_proto.PayloadEstimationCommand.Feedback.STATUS_IN_PROGRESS):
                self._logger.info(
                    'Estimating payload...', throttle_duration_sec=5)
            elif (status == payload_estimation_proto.PayloadEstimationCommand.Feedback.STATUS_COMPLETED):
                self._logger.info('Estimating payload completed!')
                self._spot_wrapper._payload = response.feedback.full_body_feedback.payload_estimation_feedback.estimated_payload
                # print(self._spot_wrapper._payload)
                self._spot_wrapper._is_moving = False
                self._spot_wrapper._last_command = None
            elif (status == payload_estimation_proto.PayloadEstimationCommand.Feedback.STATUS_ERROR):
                self._logger.error('Error during Estimation!')
                self._spot_wrapper._payload = None
                # print(self._spot_wrapper._payload)
                self._spot_wrapper._is_moving = False
                self._spot_wrapper._last_command = None
            elif (status == payload_estimation_proto.PayloadEstimationCommand.Feedback.STATUS_SMALL_MASS):
                self._logger.warning(
                    'No mass detected, no payload is registered!')
                self._spot_wrapper._payload = None
                # print(self._spot_wrapper._payload)
                self._spot_wrapper._is_moving = False
                self._spot_wrapper._last_command = None


def create_mobility_params(body_height=0.0,
                           footprint_R_body=EulerZXY(),
                           locomotion_hint=spot_command_pb2.HINT_AUTO,
                           stair_hint=False,
                           external_force_params=None,
                           obstacle_padding=None,
                           speed_limit_x=None,
                           speed_limit_y=None,
                           speed_limit_angular=None):
    """ Functionality of 'RobotCommandBuilder.mobility_params' with added
        obstacle padding and velocity limit.
    """
    if obstacle_padding is None:
        obstacle_padding = OBSTACLE_BASE_PADDING

    if speed_limit_x is None:
        speed_limit_x = VELOCITY_BASE_SPEED
    if speed_limit_y is None:
        speed_limit_y = VELOCITY_BASE_SPEED
    if speed_limit_angular is None:
        speed_limit_angular = VELOCITY_BASE_ANGULAR

    obstacles = spot_command_pb2.ObstacleParams(
        disable_vision_body_obstacle_avoidance=False,
        disable_vision_foot_obstacle_avoidance=False,
        disable_vision_foot_constraint_avoidance=False,
        obstacle_avoidance_padding=obstacle_padding,
    )

    vel_limit = SE2VelocityLimit(
        max_vel=SE2Velocity(
            linear=Vec2(x=speed_limit_x,
                        y=speed_limit_y),
            angular=speed_limit_angular),
        min_vel=SE2Velocity(
            linear=Vec2(x=-speed_limit_x,
                        y=-speed_limit_y),
            angular=-speed_limit_angular),
    )

    # Simplified body control params
    position = geometry_pb2.Vec3(z=body_height)
    rotation = footprint_R_body.to_quaternion()
    pose = geometry_pb2.SE3Pose(position=position, rotation=rotation)
    point = trajectory_pb2.SE3TrajectoryPoint(pose=pose)
    traj = trajectory_pb2.SE3Trajectory(points=[point])
    body_control = spot_command_pb2.BodyControlParams(
        base_offset_rt_footprint=traj)
    return spot_command_pb2.MobilityParams(
        body_control=body_control,
        locomotion_hint=locomotion_hint,
        stair_hint=stair_hint,
        external_force_params=external_force_params,
        vel_limit=vel_limit,
        obstacle_params=obstacles)


class SpotWrapper():
    """
    Generic wrapper class to encompass release 2.3 API features 
    as well as maintaining leases automatically
    """

    _frame_transforms = {}
    _callbacks = {}
    _rates = {}

    _keep_alive = True
    _valid = False

    _is_standing = False
    _is_sitting = True
    _is_moving = False

    _last_command = None

    _estop_endpoint = None
    _robot_id = None
    _lease = None

    _payload = None

    def __init__(self,
                 username,
                 password,
                 hostname,
                 logger,
                 rates=None,
                 callbacks=None,
                 offline=False):
        self._username = username
        self._password = password
        self._hostname = hostname
        self._logger = logger
        if rates is not None:
            self._rates = rates
        if callbacks is not None:
            self._callbacks = callbacks

        # Blocking until connection is made
        if offline:
            self._robot = None
        else:
            try:
                self._connect_to_spot()
            except RuntimeError as e:
                self._logger.error(f'Could not connect to Spot: {e}')

        if self._robot:
            # Note: ordering matters of the following methods
            self._image_requests = self._create_image_requests()
            self._clients = self._create_clients()
            self._tasks, self._async_tasks = self._create_tasks()
            self.set_mobility_params()

    def _connect_to_spot(self):
        """Create a connection with Spot (blocking function)"""
        creating_sdk = True
        while creating_sdk:
            try:
                self._sdk = create_standard_sdk('ros_spot')
                creating_sdk = False
            except Exception as e:
                self._logger.error(f'Error creating SDK object: {e}')
                time.sleep(2.0)

        self._robot = self._sdk.create_robot(self._hostname)

        authenticating = True
        while authenticating:
            try:
                self._robot.authenticate(self._username, self._password)
                self._robot.start_time_sync()
                authenticating = False
            except RpcError as err:
                self._logger.warning(
                    f'Failed to communicate with robot: {err}')
                time.sleep(2.0)

        self._valid = True

    def _create_tasks(self):

        tasks = {}

        tasks['robot_graph_nav'] = ASyncDataPoller(
            name='graph_nav',
            client=self._clients['robot_graph_nav'],
            logger=self._logger,
            rate=max(0.0, self._rates.get('graph_nav', 0.0)),
            callback=self._callbacks.get('graph_nav', lambda x: None),
            client_method=self._clients['robot_graph_nav'].get_localization_state_async,
            query_arguments={'request_live_point_cloud': True},
        )

        tasks['robot_local_grid'] = ASyncDataPoller(
            name='local_grid',
            client=self._clients['robot_local_grid'],
            logger=self._logger,
            rate=max(0.0, self._rates.get('local_grid', 0.0)),
            callback=self._callbacks.get('local_grid', lambda x: None),
            client_method=self._clients['robot_local_grid'].get_local_grids_async,
            query_arguments={
                'local_grid_type_names': [
                    'terrain',
                    # 'intensity',
                    # 'terrain_valid',
                    # 'no_step',
                    # 'obstacle_distance',
                ],
            },
        )

        tasks['robot_state'] = ASyncDataPoller(
            name='robot_state',
            client=self._clients['robot_state'],
            logger=self._logger,
            rate=max(0.0, self._rates.get('robot_state', 0.0)),
            callback=self._callbacks.get('robot_state', lambda x: None),
            client_method=self._clients['robot_state'].get_robot_state_async,
            query_arguments={},
        )

        tasks['robot_metrics'] = ASyncDataPoller(
            name='metrics',
            client=self._clients['robot_state'],
            logger=self._logger,
            rate=max(0.0, self._rates.get('metrics', 0.0)),
            callback=self._callbacks.get('metrics', lambda x: None),
            client_method=self._clients['robot_state'].get_robot_metrics_async,
            query_arguments={},
        )

        tasks['lease'] = ASyncDataPoller(
            name='lease',
            client=self._clients['lease'],
            logger=self._logger,
            rate=max(0.0, self._rates.get('lease', 0.0)),
            callback=self._callbacks.get('lease', lambda x: None),
            client_method=self._clients['lease'].list_leases_async,
            query_arguments={},
        )

        tasks['front_image'] = ASyncDataPoller(
            name='front_image',
            client=self._clients['image'],
            logger=self._logger,
            rate=max(0.0, self._rates.get('front_image', 0.0)),
            callback=self._callbacks.get('front_image', lambda x: None),
            client_method=self._clients['image'].get_image_async,
            query_arguments={'image_requests': self._image_requests['front']},
        )

        tasks['side_image'] = ASyncDataPoller(
            name='side_image',
            client=self._clients['image'],
            logger=self._logger,
            rate=max(0.0, self._rates.get('side_image', 0.0)),
            callback=self._callbacks.get('side_image', lambda x: None),
            client_method=self._clients['image'].get_image_async,
            query_arguments={'image_requests': self._image_requests['side']},
        )

        tasks['rear_image'] = ASyncDataPoller(
            name='rear_image',
            client=self._clients['image'],
            logger=self._logger,
            rate=max(0.0, self._rates.get('rear_image', 0.0)),
            callback=self._callbacks.get('rear_image', lambda x: None),
            client_method=self._clients['image'].get_image_async,
            query_arguments={'image_requests': self._image_requests['rear']},
        )

        tasks['idle'] = AsyncIdle(
            client=self._clients['robot_command'],
            logger=self._logger,
            rate=10.0,
            spot_wrapper=self,
        )

        async_tasks = AsyncTasks(list(tasks.values()))
        return tasks, async_tasks

    def _create_clients(self):
        try:
            clients = {}
            clients['world_object'] = self._robot.ensure_client(
                WorldObjectClient.default_service_name)
            clients['robot_graph_nav'] = self._robot.ensure_client(
                GraphNavClient.default_service_name)
            clients['robot_local_grid'] = self._robot.ensure_client(
                LocalGridClient.default_service_name)
            clients['robot_state'] = self._robot.ensure_client(
                RobotStateClient.default_service_name)
            clients['robot_command'] = self._robot.ensure_client(
                RobotCommandClient.default_service_name)
            clients['power'] = self._robot.ensure_client(
                PowerClient.default_service_name)
            clients['lease'] = self._robot.ensure_client(
                LeaseClient.default_service_name)
            clients['image'] = self._robot.ensure_client(
                ImageClient.default_service_name)
            clients['estop'] = self._robot.ensure_client(
                EstopClient.default_service_name)
            clients['payload'] = self._robot.ensure_client(
                PayloadClient.default_service_name)
            clients['payload_registration'] = self._robot.ensure_client(
                PayloadRegistrationClient.default_service_name)
        except Exception as e:
            error_string = f'Unable to create client service: {e}'
            self._valid = False
            self._logger.error(error_string)
            raise RuntimeError(error_string)
        return clients

    def _build_image_requests_list(self, image_sources):
        return [
            build_image_request(
                source,
                image_format=image_pb2.Image.Format.Value('FORMAT_RAW'))
            for source in image_sources
        ]

    def _create_image_requests(self):
        image_requests = {}
        image_requests['front'] = self._build_image_requests_list(
            front_image_sources)
        image_requests['side'] = self._build_image_requests_list(
            side_image_sources)
        image_requests['rear'] = self._build_image_requests_list(
            rear_image_sources)
        return image_requests

    @ property
    def is_valid(self):
        return self._valid

    @ property
    def id(self):
        return self._robot_id

    def _get_task_proto(self, name):
        task = self._tasks.get(name)
        return None if task is None else task.proto

    @ property
    def graph_nav(self):
        return self._get_task_proto('robot_graph_nav')

    @ property
    def local_grid(self):
        return self._get_task_proto('robot_local_grid')

    @ property
    def robot_state(self):
        return self._get_task_proto('robot_state')

    @ property
    def metrics(self):
        return self._get_task_proto('robot_metrics')

    @ property
    def lease(self):
        return self._get_task_proto('lease')

    @ property
    def front_images(self):
        return self._get_task_proto('front_image')

    @ property
    def side_images(self):
        return self._get_task_proto('side_image')

    @ property
    def rear_images(self):
        return self._get_task_proto('rear_image')

    @ property
    def is_standing(self):
        return self._is_standing

    @ property
    def is_sitting(self):
        return self._is_sitting

    @ property
    def is_moving(self):
        return self._is_moving

    @ property
    def time_skew(self):
        """Return the time skew between local and spot time."""
        return self._robot.time_sync.endpoint.clock_skew

    @property
    def payload(self):
        return self._payload

    def robotToLocalTime(self, timestamp):
        """Takes a timestamp and an estimated skew and return seconds and nano seconds.

        Args:
            timestamp: google.protobuf.Timestamp
        Returns:
            google.protobuf.Timestamp
        """
        rtime = Timestamp()
        rtime.seconds = timestamp.seconds - self.time_skew.seconds
        rtime.nanos = timestamp.nanos - self.time_skew.nanos
        if rtime.nanos < 0:
            rtime.nanos = rtime.nanos + 1000000000
            rtime.seconds = rtime.seconds - 1

        return rtime

    def claim(self):
        """Get a lease for the robot, a handle on the estop endpoint, and the ID of the robot."""
        try:
            self._robot_id = self._robot.get_id()
            self.getLease()
            self.resetEStop()
            return True, 'Success'
        except (ResponseError, RpcError) as err:
            self._logger.error(
                f'Failed to initialize robot communication: {err}')
            return False, str(err)

    def updateTasks(self):
        """Loop through all periodic tasks and update their data if needed."""
        self._async_tasks.update()

    def resetEStop(self):
        """Get keepalive for eStop"""
        self._estop_endpoint = EstopEndpoint(
            self._clients['estop'], 'ros', 9.0)
        # Set this endpoint as the robot's sole estop.
        self._estop_endpoint.force_simple_setup()
        self._estop_keepalive = EstopKeepAlive(self._estop_endpoint)

    def assertEStop(self, severe=True):
        """Forces the robot into eStop state.

        Args:
            severe: Default True - If true, will cut motor power immediately.  
            If false, will try to settle the robot on the ground first
        """
        try:
            if severe:
                self._estop_endpoint.stop()
            else:
                self._estop_endpoint.settle_then_cut()

            return True, 'Success'
        except:
            return False, 'Error'

    def releaseEStop(self):
        """Stop eStop keepalive"""
        if self._estop_keepalive:
            self._estop_keepalive.stop()
            self._estop_keepalive = None
            self._estop_endpoint = None

    def getLease(self, force=True):
        """Get a lease for the robot and keep the lease alive automatically."""
        if force:
            self._lease = self._clients['lease'].take()
        else:
            self._lease = self._clients['lease'].acquire()
        self._lease_keepalive = LeaseKeepAlive(self._clients['lease'])

    def releaseLease(self):
        """Return the lease on the body."""
        if self._lease:
            self._clients['lease'].return_lease(self._lease)
            self._lease = None

    def release(self):
        """Return the lease on the body and the eStop handle."""
        try:
            self.releaseLease()
            self.releaseEStop()
            return True, 'Success'
        except Exception as e:
            return False, str(e)

    def disconnect(self):
        """Release control of robot as gracefully as possible."""
        if self._robot.time_sync:
            self._robot.time_sync.stop()
        self.releaseLease()
        self.releaseEStop()

    def _update_last_command(self, command_type, command_id):
        self._last_command = (command_type, command_id)

    def _robot_command(self, command_proto, end_time_secs=None):
        """Generic blocking function for sending commands to robots.

        Args:
            command_proto: robot_command_pb2 object to send to the robot.
                Usually made with RobotCommandBuilder
            end_time_secs: (optional) Time-to-live for the command in seconds
        """
        try:
            id = self._clients['robot_command'].robot_command(
                command=command_proto,
                end_time_secs=end_time_secs,
                timesync_endpoint=None,
                lease=None,
            )
            return True, 'Success', id
        except Exception as e:
            return False, str(e), None

    def stop(self):
        """Stop the robot's motion."""
        response = self._robot_command(RobotCommandBuilder.stop_command())
        return response[0], response[1]

    def self_right(self):
        """Have the robot self-right itself."""
        response = self._robot_command(RobotCommandBuilder.selfright_command())
        return response[0], response[1]

    def orient(self, roll, pitch, yaw, height, duration):
        orientation = EulerZXY(yaw, roll, pitch)
        end_time = time.time() + duration
        response = self._robot_command(
            RobotCommandBuilder.synchro_stand_command(
                body_height=height,
                footprint_R_body=orientation),
            end_time_secs=end_time,
        )
        time.sleep(duration)
        self.stand()
        return response[0], response[1]

    def sit(self):
        """Stop the robot's motion and sit down if able."""
        response = self._robot_command(
            RobotCommandBuilder.synchro_sit_command())
        self._update_last_command(command_type='sit',
                                  command_id=response[2])
        return response[0], response[1]

    def stand(self, monitor_command=True):
        """
        If the e-stop is enabled, and the motor power is enabled, 
        stand the robot up.
        """
        response = self._robot_command(
            RobotCommandBuilder.synchro_stand_command(
                params=self._mobility_params))
        if monitor_command:
            self._update_last_command(command_type='stand',
                                      command_id=response[2])
        return response[0], response[1]

    def safe_power_off(self):
        """
        Stop the robot's motion and sit if possible.
        Once sitting, disable motor power.
        """
        response = self._robot_command(
            RobotCommandBuilder.safe_power_off_command())
        return response[0], response[1]

    def power_on(self):
        """Enble the motor power if e-stop is enabled."""
        try:
            power.power_on(self._clients['power'])
            return True, 'Success'
        except:
            return False, 'Error'

    def estimate_payload(self):
        """Estimate the payload on the back of the robot"""
        # Run payload estimation command
        full_body_command = full_body_command_proto.FullBodyCommand.Request(
            payload_estimation_request=payload_estimation_proto.PayloadEstimationCommand.Request())
        command = robot_command_pb2.RobotCommand(
            full_body_command=full_body_command)

        response = self._robot_command(command)
        self._update_last_command(command_type='payload',
                                  command_id=response[2])

        return True, 'Success'

        # Store the payload

        # payloads = self._clients['payload'].list_payloads()
        # print('\n\nPayload Listing\n' + '-' * 40)
        # print(payloads)
        # return True, 'Success'

    def register_estimated_payload(self):
        """Register the payload that has been estimated"""
        if self.payload is None:
            self._logger.error(
                'Cannot register payload, no payload has been estimated yet.')
            return False, 'Error: No payload has been estimated'

        # Register the payload
        self._clients['payload_registration'].register_payload(
            self.payload, 'ibase')

        payloads = self._clients['payload'].list_payloads()
        print('\n\nPayload Listing\n' + '-' * 40)

        for payload in payloads:
            print(payload.name)
            print(f'\tGUID: {payload.GUID}')
            print(f'\tbody_tform_payload: {payload.body_tform_payload}')
            print(
                f'\tmass_volume_properties: {payload.mass_volume_properties}')
        # print(payloads)

        return True, 'Success'

    def set_mobility_params(self,
                            body_height=0,
                            footprint_R_body=EulerZXY(),
                            locomotion_hint=1,
                            stair_hint=False,
                            external_force_params=None,
                            obstacle_padding=None,
                            speed_limit_x=None,
                            speed_limit_y=None,
                            speed_limit_angular=None):
        """Define body, locomotion, and stair parameters.

        Args:
            body_height: Body height in meters
            footprint_R_body: (EulerZXY) – The orientation of the body frame 
                with respect to the footprint frame 
                (gravity aligned framed with yaw computed from the stance feet)
            locomotion_hint: Locomotion hint
            stair_hint: Boolean to define stair motion
            obstacle_padding: padding in meters for the obstacle avoidance
            speed_limit: velocity limit in meter per second
        """
        if obstacle_padding is None:
            obstacle_padding = OBSTACLE_BASE_PADDING
        if speed_limit_x is None:
            speed_limit_x = VELOCITY_BASE_SPEED
        if speed_limit_y is None:
            speed_limit_y = VELOCITY_BASE_SPEED
        if speed_limit_angular is None:
            speed_limit_angular = VELOCITY_BASE_ANGULAR

        self._mobility_params = create_mobility_params(
            body_height=body_height,
            footprint_R_body=footprint_R_body,
            locomotion_hint=locomotion_hint,
            stair_hint=stair_hint,
            external_force_params=external_force_params,
            obstacle_padding=obstacle_padding,
            speed_limit_x=speed_limit_x,
            speed_limit_y=speed_limit_y,
            speed_limit_angular=speed_limit_angular)

    def velocity_cmd(self, v_x, v_y, v_rot, cmd_duration=None):
        """Send a velocity motion command to the robot.

        Args:
            v_x: Velocity in the X direction in meters
            v_y: Velocity in the Y direction in meters
            v_rot: Angular velocity around the Z axis in radians
            cmd_duration: (optional) Time-to-live for the command in seconds.  
                Default is 125ms (assuming 10Hz command rate).
        """
        if cmd_duration is None:
            cmd_duration = VELOCITY_CMD_DURATION

        end_time = time.time() + cmd_duration
        response = self._robot_command(
            RobotCommandBuilder.synchro_velocity_command(
                v_x=v_x,
                v_y=v_y,
                v_rot=v_rot,
                params=self._mobility_params,
            ),
            end_time_secs=end_time,
        )
        self._update_last_command(command_type='motion',
                                  command_id=response[2])

    def trajectory_cmd(self,
                       goal_x,
                       goal_y,
                       goal_heading,
                       cmd_duration=None,
                       frame_name=None):
        """Send a trajectory motion command to the robot.

        Args:
            goal_x: Position X coordinate.
            goal_y: Position Y coordinate.
            goal_heading: Pose heading in radians.
            cmd_duration: (optional) Time-to-live for the command in seconds. 
                Default is 125ms (assuming 10Hz command rate).
        """
        if frame_name is None:
            frame_name = BASE_FRAME_NAME
        if cmd_duration is None:
            cmd_duration = TRAJECTORY_CMD_DURATION

        end_time = time.time() + cmd_duration
        response = self._robot_command(
            RobotCommandBuilder.synchro_se2_trajectory_point_command(
                goal_x=goal_x,
                goal_y=goal_y,
                goal_heading=goal_heading,
                frame_name=frame_name,
                params=self._mobility_params,
            ),
            end_time_secs=end_time,
        )
        self._update_last_command(command_type='motion',
                                  command_id=response[2])

    def get_base_transform(self, base_frame=None):
        if base_frame is None:
            base_frame = BASE_FRAME_NAME

        if base_frame == ODOM_FRAME_NAME:
            base_tform_body = self.get_odom_transform()
        elif base_frame == VISION_FRAME_NAME:
            base_tform_body = self.get_vision_transform()
        else:
            return None
        return base_tform_body

    def get_odom_transform(self):
        robot_state = self._clients['robot_state'].get_robot_state()
        odom_tform_body = get_odom_tform_body(
            robot_state.kinematic_state.transforms_snapshot
        )
        return odom_tform_body

    def get_vision_transform(self):
        robot_state = self._clients['robot_state'].get_robot_state()
        vision_tform_body = get_vision_tform_body(
            robot_state.kinematic_state.transforms_snapshot
        )
        return vision_tform_body

    def get_frame_transform(self, frame_name, base_frame=None):
        if base_frame is None:
            base_frame = BASE_FRAME_NAME

        base_tform_body = self.get_base_transform(base_frame)
        base_tform_frame = self.get_transform_between(
            base_frame,
            frame_name,
        )
        if base_tform_frame is None:
            return None

        frame_tform_body = base_tform_frame.inverse() * base_tform_body
        return frame_tform_body

    def create_frame(self,
                     frame_name,
                     position_x=0.0,
                     position_y=0.0,
                     heading=0.0,
                     base_frame=None):
        """
        Creates a new frame with respect to the base frame
        via a body to frame transform.

        The positions (pose_x, pos_y) define the translation of
        the (current) body position to the frame.
        The pose_yaw is 'applied' after the translation.

        In other words:
        The pose_x, pose_y and pose_yaw are to be defined as
        if Spot would walk towards the origin of the frame
        and then rotate to match its 'zero-angle'.
        """
        if base_frame is None:
            base_frame = BASE_FRAME_NAME

        base_tform_body = self.get_base_transform(base_frame)
        pose_x, pose_y, pose_yaw = self._calculate_frame_translation(
            position_x, position_y, np.deg2rad(heading),
        )

        body_tform_frame = self.create_SE3Pose(
            x=pose_x,
            y=pose_y,
            z=0.0,
            yaw=pose_yaw,
        )

        self._frame_transforms[frame_name] = {
            'base_frame': base_frame,
            'transform': base_tform_body * body_tform_frame,
        }

    def _calculate_frame_translation(self, x, y, yaw):
        distance = np.sqrt(x**2 + y**2)
        angle = np.arctan2(y, x)

        dx = -distance * np.cos(yaw - angle)
        dy = distance * np.sin(yaw - angle)
        dyaw = -yaw

        return dx, dy, dyaw

    def get_transform_between(self,
                              frame_from,
                              frame_to,
                              world_name='world_obj'):
        if frame_to not in self._frame_transforms:
            return None

        if not frame_from == self._frame_transforms[frame_to]['base_frame']:
            return None

        return self._frame_transforms[frame_to]['transform']

    def create_SE3Pose(self, x=0.0, y=0.0, z=0.0, yaw=0.0):
        return math_helpers.SE3Pose(
            x=x,
            y=y,
            z=z,
            rot=math_helpers.Quat.from_yaw(yaw),
        )

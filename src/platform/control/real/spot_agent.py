import logging
import time

import numpy.typing as npt
from bosdyn.api import basic_command_pb2, world_object_pb2
from bosdyn.api.geometry_pb2 import Quaternion
from bosdyn.api.spot import robot_command_pb2 as spot_command_pb2
from bosdyn.client import ResponseError, RpcError
from bosdyn.client.frame_helpers import (ODOM_FRAME_NAME, VISION_FRAME_NAME,
                                         get_a_tform_b, get_vision_tform_body)
from bosdyn.client.lease import Error as LeaseBaseError
from bosdyn.client.robot_command import RobotCommandBuilder

from src.platform.control.abstract_agent import AbstractAgent
from src.platform.control.real.utils.fiducial_2_world_object_labels import \
    create_wo_from_fiducial
from src.platform.control.real.utils.get_login_config import get_login_config
from src.platform.control.real.utils.local_grid_formatting import \
    get_local_grid
from src.platform.control.real.utils.spot_wrapper import SpotWrapper


class SpotAgent(AbstractAgent):
    def __post_init__(self):
        """
        Main function for the SpotROS class.
        Gets config from ROS and initializes the wrapper.
        Holds lease from wrapper and updates all async tasks at the ROS rate
        """

        # self._logger = logging.getLogger(__name__)
        # self._logger = util.get_logger()
        # self._log = logging.getLogger(__name__)
        # logging.basicConfig(level=logging.INFO)

        # self._logger.setLevel(level=logging.WARNING)
        # self._log.setLevel(level=logging.INFO)
        self._log.setLevel(level=logging.DEBUG)

        self.mobility_parameters = {
            "obstacle_padding": 0.1,  # [m]
            # "speed_limit_x": 0.7,  # [m/s]
            "speed_limit_x": 1.5,  # [m/s]
            # "speed_limit_x": 1,  # [m/s]
            # "speed_limit_y": 0.7,  # [m/s]
            # "speed_limit_y": 1,  # [m/s]
            "speed_limit_y": 1.5,  # [m/s]
            "speed_limit_angular": 1,  # [rad/s]
            # "body_height": 0.0,  # [m]
            "body_height": 0.1,  # [m]
            # "body_height": 0.5,  # [m]
            # "body_height": 1.0,  # [m]
            "gait": spot_command_pb2.HINT_AUTO,
        }

        self.auto_claim = True
        self.auto_power_on = True
        self.auto_stand = True
        self.timer_period = 0.1  # [second]

        credentials = get_login_config()

        self.spot_wrapper = SpotWrapper(
            username=credentials.username,
            password=credentials.password,
            hostname=credentials.wifi_hostname,
            logger=self._log,
        )

        if self.spot_wrapper.is_valid:
            self._log.info("Spot wrapper is valid")

            self._apply_mobility_parameters()

            if self.auto_claim:
                claim_status = self.spot_wrapper.claim()
                self._log.info(f"claim_status: {claim_status}")
                if self.auto_power_on:
                    power_on_status = self.spot_wrapper.power_on()
                    self._log.info(f"power_on_status: {power_on_status}")
                    if self.auto_stand:
                        stand_status = self.spot_wrapper.stand()
                        self._log.info(f"stand_status: {stand_status}")

        else:
            self._log.warning("Spot wrapper is not valid!")

        time.sleep(10)

        self.pos = self.get_localization()
        # self.pos = start_pos
        self.already_detected_fiducial_tag_ids = []

    def _move_to_pos_implementation(self, target_pos: tuple, target_heading: float):
        self.blocking_move_vision_frame(target_pos, target_heading)

    def _get_local_grid_img(self) -> npt.NDArray:
        return get_local_grid(self.spot_wrapper)

    def get_localization(self) -> tuple:
        # print("state: ", self.spot_wrapper._clients['robot_state'].get_robot_state())
        state = self.spot_wrapper._clients["robot_graph_nav"].get_localization_state()
        # print(f"loc state = {state.localization}")
        # tform_body = get_odom_tform_body(state.robot_kinematics.transforms_snapshot)
        tform_body = get_vision_tform_body(state.robot_kinematics.transforms_snapshot)
        # print('Got robot state in kinematic odometry frame: \n%s' % str(odom_tform_body))

        # return odom_tform_body.position.x, odom_tform_body.position.y, odom_tform_body.position.z
        # pos = self.pos
        pos = tform_body.position.x, tform_body.position.y
        # print(f"tform_body.position = {pos}")

        return pos

    def look_for_world_objects_in_perception_scene(self):
        max_attempts = 10
        attempts = 0
        wos = []
        while attempts <= max_attempts:
            detected_fiducial = False
            fiducial_rt_world = None
            # Get the first fiducial object Spot detects with the world object service.
            fiducials = self.get_fiducial_objects()
            if not fiducials:
                return []
            for fiducial in fiducials:
                if fiducial is not None:
                    vision_tform_fiducial = get_a_tform_b(
                        fiducial.transforms_snapshot,
                        VISION_FRAME_NAME,
                        fiducial.apriltag_properties.frame_name_fiducial,
                    ).to_proto()
                    if vision_tform_fiducial is not None:
                        detected_fiducial = True
                        fiducial_rt_world = vision_tform_fiducial.position

                if (
                    detected_fiducial
                    and fiducial.apriltag_properties.tag_id
                    not in self.already_detected_fiducial_tag_ids
                ):
                    # Go to the tag and stop within a certain distance
                    # self.go_to_tag(fiducial_rt_world)
                    # print(f"fiducial_rt_world = {fiducial_rt_world}")

                    # wo = WorldObject((fiducial_rt_world.x, fiducial_rt_world.y), "YO SOY PABLO")
                    wo = create_wo_from_fiducial(
                        (fiducial_rt_world.x, fiducial_rt_world.y),
                        fiducial.apriltag_properties.tag_id,
                    )
                    self.already_detected_fiducial_tag_ids.append(
                        fiducial.apriltag_properties.tag_id
                    )

                else:
                    self._log.debug(f"no fiducial detected")
                    continue

                if wo:
                    wos.append(wo)
                else:
                    self._log.debug(
                        f"unknown fiducial detected {fiducial.apriltag_properties.tag_id}"
                    )
            if wos:
                self._log.debug(f"detected wos are {wos}")
                return wos

            else:
                # print("No fiducials found")
                pass

            attempts += 1  # increment attempts at finding a fiducial

    def get_fiducial_objects(self):
        """Get all fiducials that Spot detects with its perception system."""
        # Get all fiducial objects (an object of a specific type).
        request_fiducials = [world_object_pb2.WORLD_OBJECT_APRILTAG]
        # fiducial_objects = self._world_object_client.list_world_objects(
        fiducial_objects = (
            self.spot_wrapper._clients["world_object"]
            .list_world_objects(
                object_type=request_fiducials,
                time_start_point=time.time() - 1.0,  # not sure if this is correct time
            )
            .world_objects
        )
        if len(fiducial_objects) > 0:
            # Return the first detected fiducial.
            return fiducial_objects
        # Return none if no fiducials are found.
        return None

    def _apply_mobility_parameters(self, quaternion=None):
        if quaternion is None:
            # Unit Quaternion
            quaternion = Quaternion()
            quaternion.x = 0.0
            quaternion.y = 0.0
            quaternion.z = 0.0
            quaternion.w = 1.0

        footprint_R_body = quaternion.to_euler_zxy()
        self.spot_wrapper.set_mobility_params(
            body_height=self.mobility_parameters["body_height"],
            footprint_R_body=footprint_R_body,
            obstacle_padding=self.mobility_parameters["obstacle_padding"],
            speed_limit_x=self.mobility_parameters["speed_limit_x"],
            speed_limit_y=self.mobility_parameters["speed_limit_y"],
            speed_limit_angular=self.mobility_parameters["speed_limit_angular"],
            locomotion_hint=self.mobility_parameters["gait"],
        )

    def _try_grpc(self, desc, thunk):
        try:
            return thunk()
        except (ResponseError, RpcError, LeaseBaseError) as err:
            self.add_message("Failed {}: {}".format(desc, err))
            return None

    def _start_robot_command(self, desc, command_proto, end_time_secs=None):
        def _start_command():
            # self._robot_command_client.robot_command(lease=None, command=command_proto,
            self.spot_wrapper._clients["robot_command"].robot_command(
                lease=None, command=command_proto, end_time_secs=end_time_secs
            )

        self._try_grpc(desc, _start_command)

    def blocking_move_vision_frame(self, pos, goal_heading=0.0):
        # goal_heading = heading
        frame_name = VISION_FRAME_NAME

        cmd = RobotCommandBuilder.synchro_se2_trajectory_point_command(
            goal_x=pos[0],
            goal_y=pos[1],
            goal_heading=goal_heading,
            frame_name=frame_name,
            params=self.spot_wrapper._mobility_params,
        )

        cmd_duration = 30
        end_time = time.time() + cmd_duration
        cmd_id = self.spot_wrapper._clients["robot_command"].robot_command(
            cmd, end_time_secs=end_time
        )

        self._log.info("Robot standing twisted.")
        start_time = time.time()
        end_time = start_time + 15.0  # timeout is 5 seconds
        while time.time() < end_time:

            cmd_status = (
                self.spot_wrapper._clients["robot_command"]
                .robot_command_feedback_async(cmd_id)
                .result()
                .feedback.synchronized_feedback.mobility_command_feedback.se2_trajectory_feedback.status
            )
            if (
                cmd_status
                == basic_command_pb2.SE2TrajectoryCommand.Feedback.STATUS_AT_GOAL
            ):
                self._log.info("Arrived at goal")
                break
            time.sleep(0.01)  # wait 100ms before the next check
        else:
            self._log.info("Timeout!")

    # do this instead of the wait timer
    # https://khssnv.medium.com/spot-sdk-blocking-robot-commands-3d6902cfb403

    def move_vision_frame(self, pos: tuple, heading=0.0):
        """ROS service handler"""
        self._log.info("Executing move_vision action")

        try:
            self.spot_wrapper.trajectory_cmd(
                pos[0],
                pos[1],
                heading,
                frame_name=VISION_FRAME_NAME,
                cmd_duration=30,
                # frame_name=BODY_FRAME_NAME,
                # frame_name=ODOM_FRAME_NAME
            )
        except Exception as e:
            self._log.error(f"Move vision frame action error: {e}")
            # goal_handle.abort()
            # return result

    def move_odom_frame(self, pos: tuple, heading=0.0):
        """ROS service handler"""
        self._log.info("Executing move_vision action")

        try:
            self.spot_wrapper.trajectory_cmd(
                pos[0], pos[1], heading, cmd_duration=30, frame_name=ODOM_FRAME_NAME
            )
        except Exception as e:
            self._log.error(f"Move vision frame action error: {e}")
            # goal_handle.abort()
            # return result

    def move_body_frame(self, pos: tuple, heading=0.0):
        frame_tree = self.spot_wrapper._robot.get_frame_tree_snapshot()
        # print("FRAMETREE: ", frame_tree)
        self._start_robot_command(
            "move fwd x meter",
            RobotCommandBuilder.synchro_trajectory_command_in_body_frame(
                pos[0],
                pos[1],
                heading,
                self.spot_wrapper._robot.get_frame_tree_snapshot(),
            ),
            end_time_secs=time.time() + 30,
        )


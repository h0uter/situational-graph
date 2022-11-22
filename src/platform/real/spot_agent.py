import time

from matplotlib import pyplot as plt
import numpy as np
import logging
import numpy.typing as npt
from bosdyn.client.robot_command import RobotCommandClient, RobotCommandBuilder
from bosdyn.client import create_standard_sdk, ResponseError, RpcError
from bosdyn.client.lease import Error as LeaseBaseError
from bosdyn.api.spot import robot_command_pb2 as spot_command_pb2
from bosdyn.api import world_object_pb2, basic_command_pb2, local_grid_pb2
from bosdyn.api.geometry_pb2 import Quaternion
from bosdyn.client import util
from bosdyn.client.frame_helpers import *
from bosdyn.client.frame_helpers import (
    BODY_FRAME_NAME,
    VISION_FRAME_NAME,
    ODOM_FRAME_NAME,
    get_odom_tform_body,
    get_a_tform_b,
    get_vision_tform_body,
)
from src.shared.capabilities import Capabilities

from src.platform.real.utils.fiducial_2_world_object_labels import create_wo_from_fiducial
from src.platform.real.utils.spot_wrapper import SpotWrapper
from src.platform.abstract_agent import AbstractAgent
from src.shared.local_grid import LocalGrid
from src.platform.real.utils.get_login_config import get_login_config
from src.shared.capabilities import Capabilities

# from src.entities.world_object import WorldObject


class SpotAgent(AbstractAgent):
    def __init__(self, capabilities: set[Capabilities]):
        """
        Main function for the SpotROS class.
        Gets config from ROS and initializes the wrapper.
        Holds lease from wrapper and updates all async tasks at the ROS rate
        """
        super().__init__(capabilities)

        # self._logger = logging.getLogger(__name__)
        # self._logger = util.get_logger()
        # self._log = logging.getLogger(__name__)
        # logging.basicConfig(level=logging.INFO)

        # self._logger.setLevel(level=logging.WARNING)
        self._log.setLevel(level=logging.INFO)
        # self._log.setLevel(level=logging.DEBUG)

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

    # def move_to_pos(self, pos: tuple, heading=None):
    #     # self.move_vision_frame(pos)
    #     # time.sleep(5)
    #     # if not heading:
    #     #     target_heading = self.calc_heading_to_target(pos)
    #     # else:
    #     #     target_heading = heading

    #     self.move_to_pos_implementation(pos, target_heading)

    #     # self.previous_pos = self.pos
    #     self.pos = self.get_localization()
    #     self.heading = target_heading
    #     self.steps_taken += 1

    #     # TODO: this should return a succes/ failure bool

    def _get_local_grid_img(self) -> npt.NDArray:
        return get_local_grid(self)

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

                if detected_fiducial and fiducial.apriltag_properties.tag_id not in self.already_detected_fiducial_tag_ids:
                    # Go to the tag and stop within a certain distance
                    # self.go_to_tag(fiducial_rt_world)
                    # print(f"fiducial_rt_world = {fiducial_rt_world}")

                    # wo = WorldObject((fiducial_rt_world.x, fiducial_rt_world.y), "YO SOY PABLO")
                    wo = create_wo_from_fiducial(
                        (fiducial_rt_world.x, fiducial_rt_world.y),
                        fiducial.apriltag_properties.tag_id,
                    )
                    self.already_detected_fiducial_tag_ids.append(fiducial.apriltag_properties.tag_id)

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


# Local Grid stuff
def get_numpy_data_type(local_grid_proto):
    """Convert the cell format of the local grid proto to a numpy data type."""
    if local_grid_proto.cell_format == local_grid_pb2.LocalGrid.CELL_FORMAT_UINT16:
        return np.uint16
    elif local_grid_proto.cell_format == local_grid_pb2.LocalGrid.CELL_FORMAT_INT16:
        return np.int16
    elif local_grid_proto.cell_format == local_grid_pb2.LocalGrid.CELL_FORMAT_UINT8:
        return np.uint8
    elif local_grid_proto.cell_format == local_grid_pb2.LocalGrid.CELL_FORMAT_INT8:
        return np.int8
    elif local_grid_proto.cell_format == local_grid_pb2.LocalGrid.CELL_FORMAT_FLOAT64:
        return np.float64
    elif local_grid_proto.cell_format == local_grid_pb2.LocalGrid.CELL_FORMAT_FLOAT32:
        return np.float32
    else:
        return None


def expand_data_by_rle_count(local_grid_proto, data_type=np.int16):
    """Expand local grid data to full bytes data using the RLE count."""
    cells_pz = np.frombuffer(local_grid_proto.local_grid.data, dtype=data_type)
    cells_pz_full = []
    # For each value of rle_counts, we expand the cell data at the matching index
    # to have that many repeated, consecutive values.
    for i in range(0, len(local_grid_proto.local_grid.rle_counts)):
        for j in range(0, local_grid_proto.local_grid.rle_counts[i]):
            cells_pz_full.append(cells_pz[i])
    return np.array(cells_pz_full)


def unpack_grid(local_grid_proto):
    """Unpack the local grid proto."""
    # Determine the data type for the bytes data.
    data_type = get_numpy_data_type(local_grid_proto.local_grid)
    if data_type is None:
        print("Cannot determine the dataformat for the local grid.")
        return None
    # Decode the local grid.
    if local_grid_proto.local_grid.encoding == local_grid_pb2.LocalGrid.ENCODING_RAW:
        full_grid = np.frombuffer(local_grid_proto.local_grid.data, dtype=data_type)
    elif local_grid_proto.local_grid.encoding == local_grid_pb2.LocalGrid.ENCODING_RLE:
        full_grid = expand_data_by_rle_count(local_grid_proto, data_type=data_type)
    else:
        # Return nothing if there is no encoding type set.
        return None
    # Apply the offset and scaling to the local grid.
    if local_grid_proto.local_grid.cell_value_scale == 0:
        return full_grid
    full_grid_float = full_grid.astype(np.float64)
    full_grid_float *= local_grid_proto.local_grid.cell_value_scale
    full_grid_float += local_grid_proto.local_grid.cell_value_offset
    return full_grid_float


def compute_ground_height_in_vision_frame(robot_state_client):
    """Get the z-height of the ground plane in vision frame from the current robot state."""
    robot_state = robot_state_client.get_robot_state()
    vision_tform_ground_plane = get_a_tform_b(
        robot_state.kinematic_state.transforms_snapshot,
        VISION_FRAME_NAME,
        GROUND_PLANE_FRAME_NAME,
    )
    return vision_tform_ground_plane.position.x


def get_local_grid(spot: SpotAgent):
    robot_state_client = spot.spot_wrapper._clients["robot_state"]

    proto = spot.spot_wrapper._clients["robot_local_grid"].get_local_grids(
        ["terrain", "terrain_valid", "intensity", "no_step", "obstacle_distance"]
    )

    for local_grid_found in proto:
        if local_grid_found.local_grid_type_name == "obstacle_distance":
            local_grid_proto = local_grid_found
            cell_size = local_grid_found.local_grid.extent.cell_size
    # print(local_grid_found)
    # Unpack the data field for the local grid.
    cells_obstacle_dist = unpack_grid(local_grid_proto).astype(np.float32)
    # Populate the x,y values with a complete combination of all possible pairs for the dimensions in the grid extent.
    ys, xs = np.mgrid[
        0 : local_grid_proto.local_grid.extent.num_cells_x,
        0 : local_grid_proto.local_grid.extent.num_cells_y,
    ]

    # Get the estimated height (z value) of the ground in the vision frame.
    transforms_snapshot = local_grid_proto.local_grid.transforms_snapshot
    vision_tform_body = get_a_tform_b(
        transforms_snapshot, VISION_FRAME_NAME, BODY_FRAME_NAME
    )
    z_ground_in_vision_frame = compute_ground_height_in_vision_frame(robot_state_client)
    # Numpy vstack makes it so that each column is (x,y,z) for a single no step grid point. The height values come
    # from the estimated height of the ground plane as if the robot was standing.
    cell_count = (
        local_grid_proto.local_grid.extent.num_cells_x
        * local_grid_proto.local_grid.extent.num_cells_y
    )
    z = np.ones(cell_count, dtype=np.float32)
    z *= z_ground_in_vision_frame
    pts = np.vstack(
        [np.ravel(xs).astype(np.float32), np.ravel(ys).astype(np.float32), z]
    ).T
    pts[:, [0, 1]] *= (
        local_grid_proto.local_grid.extent.cell_size,
        local_grid_proto.local_grid.extent.cell_size,
    )
    # # Determine the coloration of the obstacle grid. Set the inside of the obstacle as a red hue, the outside of the obstacle
    # # as a blue hue, and the border of an obstacle as a green hue. Note that the inside of an obstacle is determined by a
    # # negative distance value in a grid cell, and the outside of an obstacle is determined by a positive distance value in a
    # # grid cell. The border of an obstacle is considered a distance of [0,.33] meters for a grid cell value.

    # OBSTACLE_DISTANCE_TRESHOLD = 0.3
    OBSTACLE_DISTANCE_TRESHOLD = 0.0

    colored_pts = np.ones([cell_count, 3], dtype=np.uint8)
    colored_pts[:, 0] = cells_obstacle_dist <= 0.0
    colored_pts[:, 1] = np.logical_and(
        0.0 < cells_obstacle_dist, cells_obstacle_dist < OBSTACLE_DISTANCE_TRESHOLD
    )
    colored_pts[:, 2] = cells_obstacle_dist >= OBSTACLE_DISTANCE_TRESHOLD
    # twofivefive = np.array(255)
    # colored_pts *= twofivefive.astype(np.uint8)
    colored_pts *= np.uint8(255)
    # colored_pts *= 255 # removed this because of mypy type error

    # so depending on which channel we look at means whether it can be sampled or not.

    fixed_pts = np.reshape(colored_pts, (128, 128, 3))

    return fixed_pts


### Test functions
def plot_local_grid(grid_img: list):
    # plt.ion()
    plt.imshow(grid_img, origin="lower")
    # plt.pause(0.001)

    plt.show()


def move_demo_usecase():
    spot = SpotAgent()

    spot.get_localization()
    time.sleep(5)
    x = 2
    y = 0
    heading = 0.0
    print("I m going to walk")

    spot.move_body_frame((x, y), heading)
    time.sleep(15)
    spot.get_localization()
    print("I have arrived")
    spot.move_body_frame((-x, -y), heading)
    print("Returning")
    spot.get_localization()
    time.sleep(15)


def move_vision_demo_usecase():
    spot = SpotAgent()

    spot.get_localization()
    time.sleep(5)
    x_goal = 0
    y_goal = 0
    heading = 0.0
    print("I m going to walk")
    # spot.move_vision_frame((x_goal,y_goal))
    spot.move_vision_frame((4, 0), np.pi / 2)
    time.sleep(10)
    spot.move_vision_frame((3, 4))

    time.sleep(25)
    spot.get_localization()
    print("I have arrived")
    spot.move_vision_frame((-x_goal, y_goal), 0.0)
    print("Returning")
    spot.get_localization()
    time.sleep(15)


# def move_to_sampled_point_usecase():
#     spot = SpotAgent()
#     time.sleep(7)
#     plt.ion()
#     plt.show()

#     spot.get_localization()
#     while True:

#         plt.clf()
#         grid_img = get_local_grid(spot)
#         # plot_local_grid(grid_img)
#         plt.imshow(grid_img, origin="lower")
#         time.sleep(1)

#         lg = LocalGrid((0, 0), grid_img, 3.84, 0.03)
#         print(lg)
#         frontiers = lg.los_sample_frontiers_on_cellmap(60, 50)
#         print(frontiers)

#         plt.imshow(grid_img, origin="lower")
#         # plt.imshow(grid_img)
#         plt.plot(frontiers[:, 0], frontiers[:, 1], "X")
#         # plt.show()
#         plt.pause(5)

#         x, y, z = spot.get_localization()

#         x_goal = x + (frontiers[0, 0] - 64) * 0.03
#         y_goal = y + (frontiers[0, 1] - 64) * 0.03
#         print(f"ima at {x}, {y}, moving to: {x_goal}, {y_goal}")

#         spot.move_vision_frame((x_goal, y_goal))
#         time.sleep(5)


def movement_square_VISION_test(spot):
    spot.move_vision_frame((0, -6), 0)
    time.sleep(10)
    spot.move_vision_frame((3.5, -6), 0)
    time.sleep(10)
    spot.move_vision_frame((3.5, 0), 0)
    time.sleep(10)
    spot.move_vision_frame((0, 0), 0)
    time.sleep(10)


def movement_square_ODOM_test(spot):
    # spot.move_odom_frame((0, -6), 0)
    spot.move_odom_frame((6, 0), 0)
    time.sleep(10)
    # spot.move_odom_frame((3.5, -6), 0)
    spot.move_odom_frame((6, 3.5), 0)
    time.sleep(10)
    # spot.move_odom_frame((3.5, 0), 0)
    spot.move_odom_frame((0, 3.5), 0)
    time.sleep(10)
    # spot.move_odom_frame((0, 0), 0)
    spot.move_odom_frame((0, 0), 0)
    time.sleep(10)


if __name__ == "__main__":
    # move_demo_usecase()
    # move_vision_demo_usecase()
    # move_to_sampled_point_usecase()

    spot = SpotAgent()

    # movement_square_VISION_test(spot)
    # movement_square_ODOM_test(spot)

    spot.move_odom_frame((0, 0), np.pi)

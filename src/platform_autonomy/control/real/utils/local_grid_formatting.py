import numpy as np
from bosdyn.api import local_grid_pb2
from bosdyn.client.frame_helpers import (BODY_FRAME_NAME,
                                         GROUND_PLANE_FRAME_NAME,
                                         VISION_FRAME_NAME,
                                         get_a_tform_b)

from src.platform_autonomy.control.real.utils.spot_wrapper import SpotWrapper


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


def get_local_grid(spot_wrapper: SpotWrapper):
    robot_state_client = spot_wrapper._clients["robot_state"]

    proto = spot_wrapper._clients["robot_local_grid"].get_local_grids(
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

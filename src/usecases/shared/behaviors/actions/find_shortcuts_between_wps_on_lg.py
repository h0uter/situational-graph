import math
from dataclasses import dataclass

from src.config import cfg
from src.mission_autonomy.situational_graph import SituationalGraph
from src.platform_control.abstract_agent import AbstractAgent
from src.platform_state.local_grid import LocalGrid
from src.shared.situations import Situations
from src.utils.event import post_event


@dataclass
class WaypointShortcutViewModel:
    """A view model for a shortcut between two waypoints on the local grid."""
    local_grid: LocalGrid
    collision_cells: list[tuple[int, int]]
    shortcut_candidate_cells: list[tuple[int, int]]


# BUG: on the real robot sometimes impossible shortcuts are added.
def add_shortcut_edges_between_wps_on_lg(
    lg: LocalGrid, tosg: SituationalGraph, agent: AbstractAgent
):
    collision_cells = []
    close_nodes = tosg.get_nodes_of_type_in_margin(
        lg.world_pos, cfg.WP_SHORTCUT_MARGIN, Situations.WAYPOINT
    )
    shortcut_candidate_positions = []
    shortcut_candidate_cells = []
    for node in close_nodes:
        if node != agent.at_wp:
            shortcut_candidate_positions.append(tosg.get_node_data_by_node(node)["pos"])

    if shortcut_candidate_positions:
        for point in shortcut_candidate_positions:
            at_cell = lg.length_num_cells // 2, lg.length_num_cells // 2

            to_cell = lg.world_coords2cell_idxs(point)
            shortcut_candidate_cells.append(to_cell)

            (
                is_collision_free,
                collision_point,
            ) = lg.is_collision_free_straight_line_between_cells(at_cell, to_cell)
            # I think this function might be messing it up

            if collision_point:
                collision_cell = lg.world_coords2cell_idxs(collision_point)
                collision_cells.append(collision_cell)

            if is_collision_free:
                from_wp = agent.at_wp
                to_wp = tosg.get_node_by_pos(point)

                if not tosg.G.has_edge(from_wp, to_wp):
                    tosg.add_waypoint_diedge(from_wp, to_wp)

    data = WaypointShortcutViewModel(
        local_grid=lg,
        collision_cells=collision_cells,
        shortcut_candidate_cells=shortcut_candidate_cells,
    )
    post_event("shortcut checking data", data)

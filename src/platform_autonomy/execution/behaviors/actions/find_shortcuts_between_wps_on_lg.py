from dataclasses import dataclass

from src.config import cfg
from src.mission_autonomy.situational_graph import SituationalGraph
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.platform_autonomy.state.local_grid import LocalGrid
from src.shared.prior_knowledge.situations import Situations
from src.core.topics import Topics
from src.core.event_system import post_event


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
        lg.lg_xy, cfg.WP_SHORTCUT_MARGIN, Situations.WAYPOINT
    )
    wp_positions_to_shortcut_to_candidates = []
    shortcut_candidate_cells = []
    for node in close_nodes:
        if node != agent.at_wp:
            wp_positions_to_shortcut_to_candidates.append(tosg.get_node_data_by_node(node)["pos"])

    agent_at_rc = lg.LG_LEN_IN_N_CELLS // 2, lg.LG_LEN_IN_N_CELLS // 2
    
    if wp_positions_to_shortcut_to_candidates:
        for wp_pos in wp_positions_to_shortcut_to_candidates:

            to_cell = lg.xy2rc(wp_pos)
            shortcut_candidate_cells.append(to_cell)

            (
                is_collision_free,
                collision_point,
            ) = lg.is_collision_free_straight_line_between_cells(agent_at_rc, to_cell)
            # I think this function might be messing it up

            if collision_point:
                collision_cell = lg.xy2rc(collision_point)
                collision_cells.append(collision_cell)

            if is_collision_free:
                from_wp = agent.at_wp
                to_wp = tosg.get_node_by_pos(wp_pos)

                if not tosg.G.has_edge(from_wp, to_wp):
                    tosg.add_waypoint_diedge(from_wp, to_wp)

    data = WaypointShortcutViewModel(
        local_grid=lg,
        collision_cells=collision_cells,
        shortcut_candidate_cells=shortcut_candidate_cells,
    )
    post_event(str(Topics.SHORTCUT_CHECKING), data)

from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.usecases.actions.abstract_action import AbstractAction
from src.utils.config import Config
from src.utils.my_types import NodeType

import uuid
from typing import Union

from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.local_grid import LocalGrid
from src.usecases.abstract_mission import AbstractMission
from src.utils.event import post_event
from src.utils.config import Config
from src.utils.my_types import EdgeType, Node, NodeType


class ExploreFrontier(AbstractAction):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def run(self, agent: AbstractAgent, krm: KnowledgeRoadmap, action_path):
        self.next_node = action_path[1]  # HACK: this is a hack, but it works for now

        node_data = krm.get_node_data_by_idx(action_path[1])
        agent.move_to_pos(node_data["pos"])

        at_destination = (
            len(
                krm.get_nodes_of_type_in_margin(
                    agent.get_localization(), self.cfg.ARRIVAL_MARGIN, NodeType.FRONTIER
                )
            )
            >= 1
        )
        self._log.debug(f"{agent.name}: at_destination: {at_destination}")

        if at_destination:
            self._log.debug(
                f"{agent.name}: Now the frontier is visited it can be removed to sample a waypoint in its place."
            )
            krm.remove_frontier(self.next_node)
            # self.selected_frontier_idx = None

            self.sample_waypoint_from_pose(agent, krm)
            lg = self.get_lg(agent)
            self.obtain_and_process_new_frontiers(
                agent, krm, lg
            )  # XXX: this is my most expensive function, so I should try to optimize it
            self.prune_frontiers(
                krm
            )  # XXX: this is my 2nd expensive function, so I should try to optimize it
            self.find_shortcuts_between_wps(lg, krm, agent)
            w_os = agent.look_for_world_objects_in_perception_scene()
            if w_os:
                for w_o in w_os:
                    krm.add_world_object(w_o.pos, w_o.name)
            post_event("new lg", lg)
            self.target_node = None
            self.action_path = None

        """Path Execution"""

    #############################################################################################
    def sample_waypoint_from_pose(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap
    ) -> None:
        """
        Sample a new waypoint at current agent pos, and add an edge connecting it to prev wp.
        this should be sampled from the pose graph eventually
        """
        # BUG:  this can make the agent teleport to a random frontier in the vicinty.
        # better would be to explicitly check if we reached the frontier we intended to reach.
        # and if we didnt to attempt to walk to it again. To attempt to actually expand the krm
        # with the intended frontier and not a random one
        # HACK: just taking the first one from the list is not neccessarily the closest
        # BUG: list index out of range range
        wp_at_previous_pos = krm.get_nodes_of_type_in_margin(
            agent.previous_pos, self.cfg.PREV_POS_MARGIN, NodeType.WAYPOINT
        )[0]
        krm.add_waypoint(agent.get_localization(), wp_at_previous_pos)
        agent.at_wp = krm.get_nodes_of_type_in_margin(
            agent.get_localization(), self.cfg.AT_WP_MARGIN, NodeType.WAYPOINT
        )[0]

    # utitlies
    ############################################################################################

    def get_lg(self, agent: AbstractAgent) -> LocalGrid:
        lg_img = agent.get_local_grid_img()

        return LocalGrid(
            world_pos=agent.get_localization(), img_data=lg_img, cfg=self.cfg,
        )

    def obtain_and_process_new_frontiers(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap, lg: LocalGrid,
    ) -> None:
        frontiers_cells = lg.sample_frontiers_on_cellmap(
            radius=self.cfg.FRONTIER_SAMPLE_RADIUS_NUM_CELLS,
            num_frontiers_to_sample=self.cfg.N_SAMPLES,
        )
        # self._log.debug(f"{agent.name}: found {frontiers_cells} new frontiers")
        for frontier_cell in frontiers_cells:
            frontier_pos_global = lg.cell_idx2world_coords(frontier_cell)
            krm.add_frontier(frontier_pos_global, agent.at_wp)

    def prune_frontiers(self, krm: KnowledgeRoadmap) -> None:
        """obtain all the frontier nodes in krm in a certain radius around the current position"""

        waypoints = krm.get_all_waypoint_idxs()

        for wp in waypoints:
            wp_pos = krm.get_node_data_by_idx(wp)["pos"]
            # close_frontiers = self.get_nodes_of_type_in_radius(
            close_frontiers = krm.get_nodes_of_type_in_margin(
                wp_pos, self.cfg.PRUNE_RADIUS, NodeType.FRONTIER
            )
            for frontier in close_frontiers:
                krm.remove_frontier(frontier)

    def find_shortcuts_between_wps(
        self, lg: LocalGrid, krm: KnowledgeRoadmap, agent: AbstractAgent
    ):
        close_nodes = krm.get_nodes_of_type_in_margin(
            lg.world_pos, self.cfg.WP_SHORTCUT_MARGIN, NodeType.WAYPOINT
        )
        points = []
        for node in close_nodes:
            if node != agent.at_wp:
                points.append(krm.get_node_data_by_idx(node)["pos"])

        if points:
            for point in points:
                at_cell = lg.length_num_cells / 2, lg.length_num_cells / 2
                to_cell = lg.world_coords2cell_idxs(point)
                is_collision_free, _ = lg.is_collision_free_straight_line_between_cells(
                    at_cell, to_cell
                )
                if is_collision_free:
                    from_wp = agent.at_wp
                    to_wp = krm.get_node_by_pos(point)

                    # TODO: encapsulate this in krm
                    edge_len = krm.calc_edge_len(from_wp, to_wp)
                    krm.graph.add_edge(
                        from_wp, to_wp, type=EdgeType.WAYPOINT_EDGE, cost=edge_len
                    )
                    krm.graph.add_edge(
                        to_wp, from_wp, type=EdgeType.WAYPOINT_EDGE, cost=edge_len
                    )

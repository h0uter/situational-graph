from src.entities.abstract_agent import AbstractAgent
from src.entities.krm import KRM
from src.usecases.actions.abstract_action import AbstractAction
from src.utils.config import Config
from src.entities.local_grid import LocalGrid
from src.utils.event import post_event
from src.utils.my_types import NodeType, Node
from src.utils.saving_data_objects import load_something, save_something


class ExploreAction(AbstractAction):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def run(self, agent: AbstractAgent, krm: KRM, action_path):
        next_node = action_path[0][1]
        next_node_pos = krm.get_node_data_by_node(next_node)["pos"]

        # special case: initialization
        if len(krm.get_all_frontiers_idxs()) <= 1 and not agent.init:
            lg = self.get_lg(agent)
            self.sample_new_frontiers_and_add_to_krm(agent, krm, lg)
            agent.set_init()
            return []

        if agent.get_localization() is not next_node_pos:
            agent.move_to_pos(next_node_pos)
            self._log.debug(f"{agent.name}: moving to {next_node_pos}")
        else:
            self._log.warning(f"{agent.name}: already at next node")

        if self.check_at_destination(agent, krm, next_node):
            self._log.debug(
                f"{agent.name}: Now the frontier is visited it can be removed to sample a waypoint in its place."
            )
            krm.remove_frontier(next_node)
            lg = self.get_lg(agent)

            # HACK: this is to deal with explosion of frontiers if we cannot sample a new wp
            if not self.sample_waypoint_from_pose(agent, krm):
                self._log.error(f"sampling waypoint failed")
                return []

            # XXX: this is my 2nd  most expensive function, so I should try to optimize it
            self.sample_new_frontiers_and_add_to_krm(agent, krm, lg)

            # XXX: this is my 3nd expensive function, so I should try to optimize it
            self.prune_frontiers(krm)
            self.find_shortcuts_between_wps(lg, krm, agent)

            self.process_world_objects(agent, krm)

            return []

        else:
            # Recovery behaviour
            self._log.warning(
                f"{agent.name}: did not reach destination during explore action."
            )
            krm.remove_frontier(next_node)
            # maintain the previous heading to stop tedious turning
            agent.move_to_pos(
                krm.get_node_data_by_node(action_path[0][0])["pos"], agent.heading
            )
            agent.previous_pos = agent.get_localization()

            self.prune_frontiers(krm)

            return []

    # TODO: move this to agent services or smth
    def process_world_objects(self, agent: AbstractAgent, krm: KRM) -> None:
        w_os = agent.look_for_world_objects_in_perception_scene()
        if w_os:
            for w_o in w_os:
                krm.add_world_object(w_o.pos, w_o.name)

    def check_at_destination(
        self, agent: AbstractAgent, krm: KRM, destination_node: Node
    ) -> bool:
        """
        Check if the agent is at the destination.
        """
        # This is there so we can initialze by adding a frontier self edge on 0
        at_destination = False
        destination_node_type = krm.get_node_data_by_node(destination_node)["type"]

        nodes_near_where_i_ended_up = krm.get_nodes_of_type_in_margin(
            agent.get_localization(), self.cfg.ARRIVAL_MARGIN, destination_node_type,
        )

        if destination_node in nodes_near_where_i_ended_up:
            at_destination = True

        self._log.debug(f"{agent.name}: at_destination: {at_destination}")
        return at_destination

    """Path Execution"""
    #############################################################################################
    def sample_waypoint_from_pose(self, agent: AbstractAgent, krm: KRM) -> bool:
        """
        Sample a new waypoint at current agent pos, and add an edge connecting it to prev wp.
        """
        print(agent.previous_pos)
        wp_at_previous_pos_candidates = krm.get_nodes_of_type_in_margin(
            agent.previous_pos, self.cfg.PREV_POS_MARGIN, NodeType.WAYPOINT
        )

        if len(wp_at_previous_pos_candidates) == 0:
            self._log.error(
                f"{agent.name}: No waypoint at previous pos {agent.previous_pos}, no wp added."
            )
            self._log.error(
                f"{agent.name}: {agent.pos=} and {agent.get_localization()=}."
            )
            agent.localize_to_waypoint(krm)

            return False

        elif len(wp_at_previous_pos_candidates) > 1:
            self._log.warning(
                f"{agent.name}: Multiple waypoints at previous pos, taking first one: {wp_at_previous_pos_candidates[0]}."
            )
            wp_at_previous_pos = wp_at_previous_pos_candidates[0]
            krm.add_waypoint(agent.get_localization(), wp_at_previous_pos)
            agent.localize_to_waypoint(krm)

            return True
        elif len(wp_at_previous_pos_candidates) == 1:
            wp_at_previous_pos = wp_at_previous_pos_candidates[0]
            krm.add_waypoint(agent.get_localization(), wp_at_previous_pos)
            agent.localize_to_waypoint(krm)
            return True

        # agent.localize_to_waypoint(krm)

    def sample_new_frontiers_and_add_to_krm(
        self, agent: AbstractAgent, krm: KRM, lg: LocalGrid,
    ) -> None:
        new_frontier_cells = lg.los_sample_frontiers_on_cellmap(
            radius=self.cfg.FRONTIER_SAMPLE_RADIUS_NUM_CELLS,
            num_frontiers_to_sample=self.cfg.N_SAMPLES,
        )
        self._log.debug(f"{agent.name}: found {len(new_frontier_cells)} new frontiers")
        for frontier_cell in new_frontier_cells:
            frontier_pos_global = lg.cell_idx2world_coords(frontier_cell)
            krm.add_frontier(frontier_pos_global, agent.at_wp)

    def prune_frontiers(self, krm: KRM) -> None:
        waypoints = krm.get_all_waypoint_idxs()

        for wp in waypoints:
            wp_pos = krm.get_node_data_by_node(wp)["pos"]
            close_frontiers = krm.get_nodes_of_type_in_margin(
                wp_pos, self.cfg.PRUNE_RADIUS, NodeType.FRONTIER
            )
            for frontier in close_frontiers:
                krm.remove_frontier(frontier)

    # BUG: on the real robot sometimes impossible shortcuts are added.
    def find_shortcuts_between_wps(self, lg: LocalGrid, krm: KRM, agent: AbstractAgent):
        close_nodes = krm.get_nodes_of_type_in_margin(
            lg.world_pos, self.cfg.WP_SHORTCUT_MARGIN, NodeType.WAYPOINT
        )
        shortcut_candidate_positions = []
        for node in close_nodes:
            if node != agent.at_wp:
                shortcut_candidate_positions.append(
                    krm.get_node_data_by_node(node)["pos"]
                )

        if shortcut_candidate_positions:
            for point in shortcut_candidate_positions:
                at_cell = lg.length_num_cells / 2, lg.length_num_cells / 2
                to_cell = lg.world_coords2cell_idxs(point)
                is_collision_free, _ = lg.is_collision_free_straight_line_between_cells(
                    at_cell, to_cell
                )
                if is_collision_free:
                    from_wp = agent.at_wp
                    to_wp = krm.get_node_by_pos(point)

                    if not krm.check_if_edge_exists(from_wp, to_wp):
                        self._log.debug(
                            f"{agent.name}: Adding shortcut from {from_wp} to {to_wp}."
                        )
                        krm.add_waypoint_diedge(from_wp, to_wp)

    def get_lg(self, agent: AbstractAgent) -> LocalGrid:
        lg_img = agent.get_local_grid_img()
        # save_something(lg_img, "lg_img")
        lg = LocalGrid(
            world_pos=agent.get_localization(), img_data=lg_img, cfg=self.cfg,
        )
        post_event("new lg", lg)

        return lg

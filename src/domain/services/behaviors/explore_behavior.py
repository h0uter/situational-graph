from typing import Sequence

from src.domain.abstract_agent import AbstractAgent
from src.domain.entities.node_and_edge import Edge, Node
from src.domain.entities.local_grid import LocalGrid
from src.domain.entities.object_types import ObjectTypes
from src.domain.services.tosg import TOSG
from src.domain.services.behaviors.abstract_behavior import (AbstractBehavior,
                                                      BehaviorResult)
from src.configuration.config import Config
from src.entrypoints.utils.event import post_event
from src.utils.saving_data_objects import load_something, save_something


class ExploreBehavior(AbstractBehavior):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def _run_behavior_implementation(
        self, agent: AbstractAgent, tosg: TOSG, behavior_edge
    ) -> BehaviorResult:
        target_node = behavior_edge[1]
        target_node_pos = tosg.get_node_data_by_node(target_node)["pos"]

        # FIXME: move this to the initialize behavior
        # special case: initialization
        if len(tosg.get_all_frontiers_idxs()) <= 1 and not agent.init:
            lg = self.__get_lg(agent)

            new_frontier_cells = self.__sample_new_frontiers(agent, tosg, lg)
            self.__add_new_frontiers_to_tosg(new_frontier_cells, lg, tosg, agent)

            agent.set_init()
            return BehaviorResult(False)

        # the goto action
        if agent.get_localization() is not target_node_pos:
            agent.move_to_pos(target_node_pos)
            self._log.debug(f"{agent.name}: moving to {target_node_pos}")
            return BehaviorResult(True)
        else:
            self._log.warning(f"{agent.name}: already at next node")
            self._log.warning(f"edge: {behavior_edge}")
            return BehaviorResult(False)

    def _check_postconditions(
        self,
        agent: AbstractAgent,
        tosg: TOSG,
        result: BehaviorResult,
        behavior_edge: Edge,
    ):
        """Check if the postconditions for the behavior are met."""
        next_node = behavior_edge[1]
        return self.__check_at_destination(agent, tosg, next_node)

    def _mutate_graph_and_tasks_success(
        self, agent: AbstractAgent, tosg: TOSG, behavior_edge: Edge, affordances
    ):
        next_node = behavior_edge[1]
        self._log.debug(
            f"{agent.name}: Now the frontier is visited it can be removed to sample a waypoint in its place."
        )
        # start mutate graph
        tosg.remove_frontier(next_node)
        lg = self.__get_lg(agent)

        # HACK: this is to deal with explosion of frontiers if we cannot sample a new wp
        if not self.__sample_waypoint_from_pose(agent, tosg):
            self._log.error("sampling waypoint failed")
            # return []

        # XXX: this is my 2nd  most expensive function, so I should try to optimize it
        new_frontier_cells = self.__sample_new_frontiers(agent, tosg, lg)
        self.__add_new_frontiers_to_tosg(new_frontier_cells, lg, tosg, agent)

        # XXX: this is my 3nd expensive function, so I should try to optimize it
        self.__prune_frontiers(tosg)
        self.__find_shortcuts_between_wps(lg, tosg, agent)

        self.__process_world_objects(agent, tosg)

    def _mutate_graph_and_tasks_failure(
        self, agent: AbstractAgent, tosg: TOSG, behavior_edge: Edge
    ):
        # Recovery behaviour
        self._log.warning(
            f"{agent.name}: did not reach destination during explore action."
        )
        # this is the actual mutation of the grpah on failure
        tosg.remove_frontier(behavior_edge[1])
        # maintain the previous heading to stop tedious turning
        # TODO: this move to pos is the recovery of the behavior, it should be in the run method.
        agent.move_to_pos(
            tosg.get_node_data_by_node(behavior_edge[0])["pos"], agent.heading
        )
        agent.previous_pos = agent.get_localization()

        # this is the actual mutation of the grpah on failure
        self.__prune_frontiers(tosg)

    ##############################################################################################
    # exploration specific functions
    ##############################################################################################

    # TODO: move this to agent services or smth
    def __process_world_objects(self, agent: AbstractAgent, tosg: TOSG) -> None:
        w_os = agent.look_for_world_objects_in_perception_scene()
        if w_os:
            for w_o in w_os:
                tosg.add_world_object(w_o.pos, w_o.name)

    def __check_at_destination(
        self, agent: AbstractAgent, tosg: TOSG, destination_node: Node
    ) -> bool:
        """
        Check if the agent is at the destination.
        """
        # This is there so we can initialze by adding a frontier self edge on 0
        at_destination = False
        destination_node_type = tosg.get_node_data_by_node(destination_node)["type"]

        nodes_near_where_i_ended_up = tosg.get_nodes_of_type_in_margin(
            agent.get_localization(),
            self.cfg.ARRIVAL_MARGIN,
            destination_node_type,
        )

        if destination_node in nodes_near_where_i_ended_up:
            at_destination = True

        self._log.debug(f"{agent.name}: at_destination: {at_destination}")
        return at_destination

    def __sample_waypoint_from_pose(self, agent: AbstractAgent, tosg: TOSG) -> bool:
        """
        Sample a new waypoint at current agent pos, and add an edge connecting it to prev wp.
        """
        print(agent.previous_pos)
        wp_at_previous_pos_candidates = tosg.get_nodes_of_type_in_margin(
            agent.previous_pos, self.cfg.PREV_POS_MARGIN, ObjectTypes.WAYPOINT
        )

        if len(wp_at_previous_pos_candidates) == 0:
            self._log.error(
                f"{agent.name}: No waypoint at previous pos {agent.previous_pos}, no wp added."
            )
            self._log.error(
                f"{agent.name}: {agent.pos=} and {agent.get_localization()=}."
            )
            agent.localize_to_waypoint(tosg)

            return False

        elif len(wp_at_previous_pos_candidates) > 1:
            self._log.warning(
                f"{agent.name}: Multiple waypoints at previous pos, taking first one: {wp_at_previous_pos_candidates[0]}."
            )
            wp_at_previous_pos = wp_at_previous_pos_candidates[0]
            tosg.add_waypoint(agent.get_localization(), wp_at_previous_pos)
            agent.localize_to_waypoint(tosg)

            return True

        elif len(wp_at_previous_pos_candidates) == 1:
            wp_at_previous_pos = wp_at_previous_pos_candidates[0]
            tosg.add_waypoint(agent.get_localization(), wp_at_previous_pos)
            agent.localize_to_waypoint(tosg)

            return True

        # agent.localize_to_waypoint(krm)

    def __sample_new_frontiers(
        self,
        agent: AbstractAgent,
        tosg: TOSG,
        lg: LocalGrid,
    ) -> Sequence:
        new_frontier_cells = lg.los_sample_frontiers_on_cellmap(
            radius=self.cfg.FRONTIER_SAMPLE_RADIUS_NUM_CELLS,
            num_frontiers_to_sample=self.cfg.N_SAMPLES,
        )
        self._log.debug(f"{agent.name}: found {len(new_frontier_cells)} new frontiers")

        return new_frontier_cells

    def __add_new_frontiers_to_tosg(self, new_frontier_cells, lg, tosg: TOSG, agent):
        for frontier_cell in new_frontier_cells:
            frontier_pos_global = lg.cell_idx2world_coords(frontier_cell)
            tosg.add_frontier(frontier_pos_global, agent.at_wp)

    def __prune_frontiers(self, tosg: TOSG) -> None:
        waypoints = tosg.get_all_waypoint_idxs()

        for wp in waypoints:
            wp_pos = tosg.get_node_data_by_node(wp)["pos"]
            close_frontiers = tosg.get_nodes_of_type_in_margin(
                wp_pos, self.cfg.PRUNE_RADIUS, ObjectTypes.FRONTIER
            )
            for frontier in close_frontiers:
                tosg.remove_frontier(frontier)

    # BUG: on the real robot sometimes impossible shortcuts are added.
    def __find_shortcuts_between_wps(
        self, lg: LocalGrid, tosg: TOSG, agent: AbstractAgent
    ):
        close_nodes = tosg.get_nodes_of_type_in_margin(
            lg.world_pos, self.cfg.WP_SHORTCUT_MARGIN, ObjectTypes.WAYPOINT
        )
        shortcut_candidate_positions = []
        for node in close_nodes:
            if node != agent.at_wp:
                shortcut_candidate_positions.append(
                    tosg.get_node_data_by_node(node)["pos"]
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
                    to_wp = tosg.get_node_by_pos(point)

                    if not tosg.check_if_edge_exists(from_wp, to_wp):
                        self._log.debug(
                            f"{agent.name}: Adding shortcut from {from_wp} to {to_wp}."
                        )
                        tosg.add_waypoint_diedge(from_wp, to_wp)

    def __get_lg(self, agent: AbstractAgent) -> LocalGrid:
        lg_img = agent.get_local_grid_img()
        # save_something(lg_img, "lg_img")
        lg = LocalGrid(
            world_pos=agent.get_localization(),
            img_data=lg_img,
            cfg=self.cfg,
        )
        post_event("new lg", lg)

        return lg

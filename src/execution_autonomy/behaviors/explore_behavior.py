from typing import Optional, Sequence

from src.config import cfg
from src.execution_autonomy.abstract_behavior import AbstractBehavior, BehaviorResult
from src.mission_autonomy.situational_graph import SituationalGraph
from src.platform_control.abstract_agent import AbstractAgent
from src.platform_state.frontier_sampling_strategies import (
    AngularLOSFrontierSamplingStrategy,
)
from src.platform_state.local_grid import LocalGrid
from src.shared.prior_knowledge.affordance import Affordance
from src.shared.node_and_edge import Edge, Node
from src.shared.prior_knowledge.situations import Situations
from src.shared.world_object import WorldObject
from src.execution_autonomy.behaviors.actions.find_shortcuts_between_wps_on_lg import (
    add_shortcut_edges_between_wps_on_lg,
)


class ExploreBehavior(AbstractBehavior):
    def __init__(self, agent: AbstractAgent):
        super().__init__(agent)
        # self._sampling_strategy = LOSFrontierSamplingStrategy()
        self._sampling_strategy = AngularLOSFrontierSamplingStrategy()

    def _run_behavior_implementation(
        self, agent: AbstractAgent, tosg: SituationalGraph, behavior_edge
    ) -> BehaviorResult:
        target_node = behavior_edge[1]
        target_node_pos = tosg.get_node_data_by_node(target_node)["pos"]

        """The first exploration step is just sampling in place."""
        # HACK: this should just be an init behavior or something.
        if not agent.init_explore_step_completed:
            lg = agent.get_local_grid()
            new_frontier_cells = self._sampling_strategy.sample_frontiers(lg)
            # BUG: something goes wrong when sampling with the Angular strategy here
            self.__add_new_frontiers_to_tosg(new_frontier_cells, lg, tosg, agent)
            agent.set_init_explore_step()
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
        tosg: SituationalGraph,
        result: BehaviorResult,
        behavior_edge: Edge,
    ):
        """Check if the postconditions for the behavior are met."""
        next_node = behavior_edge[1]
        return self.__check_at_destination(agent, tosg, next_node)

    # FIXME: this is an expensive function
    def _mutate_graph_and_tasks_success(
        self,
        agent: AbstractAgent,
        tosg: SituationalGraph,
        result: BehaviorResult,
        behavior_edge: Edge,
        affordances: list[Affordance],
    ):
        next_node = behavior_edge[1]
        self._log.debug(
            f"{agent.name}: Now the frontier is visited it can be removed to sample a waypoint in its place."
        )
        # start mutate graph
        tosg.remove_frontier(next_node)
        lg = agent.get_local_grid()

        """part 1: use local grid to process new virtual objects"""
        # HACK: this is to deal with explosion of frontiers if we cannot sample a new wp
        if not self.__sample_waypoint_from_pose(agent, tosg):
            self._log.error("sampling waypoint failed")

        # FIXME: this is my 2nd  most expensive function, so I should try to optimize it
        # new_frontier_cells = self.__sample_new_frontiers(agent, tosg, lg)
        new_frontier_cells = self._sampling_strategy.sample_frontiers(lg)

        self.__add_new_frontiers_to_tosg(new_frontier_cells, lg, tosg, agent)

        # FIXME: this is my 3nd expensive function, so I should try to optimize it
        self.__prune_frontiers(tosg)
        # self.__find_shortcuts_between_wps(lg, tosg, agent)
        add_shortcut_edges_between_wps_on_lg(lg, tosg, agent)

        """part 2: use perception service to sense new world objects"""
        # 1. obtain world objects in perception scene
        worldobjects = self.__process_world_objects(agent, tosg, affordances)

        if worldobjects:
            # 2. check if they not already in the graph
            for wo in worldobjects:
                if tosg.get_node_by_pos(wo.pos):
                    self._log.debug(
                        f"{wo.object_type} at {wo.pos} already in the graph"
                    )
                    return

            # 3. add them to the graph
            for wo in worldobjects:
                self._log.debug(
                    f">>>>{agent.name}: adding world object {wo.object_type}"
                )

                tosg.add_node_with_task_and_edges_from_affordances(
                    agent.at_wp, wo.object_type, wo.pos, affordances
                )

    def _mutate_graph_and_tasks_failure(
        self, agent: AbstractAgent, tosg: SituationalGraph, behavior_edge: Edge
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
    def __process_world_objects(
        self,
        agent: AbstractAgent,
        tosg: SituationalGraph,
        affordances: Sequence[Affordance],
    ) -> Optional[Sequence[WorldObject]]:
        return agent.look_for_world_objects_in_perception_scene()
        # TODO: this should  return the object type and pose so that we can process it in the mutate graph step

    def __check_at_destination(
        self, agent: AbstractAgent, tosg: SituationalGraph, destination_node: Node
    ) -> bool:
        at_destination = False
        destination_node_type = tosg.get_node_data_by_node(destination_node)["type"]

        nodes_near_where_i_ended_up = tosg.get_nodes_of_type_in_margin(
            agent.get_localization(),
            cfg.ARRIVAL_MARGIN,
            destination_node_type,
        )

        if destination_node in nodes_near_where_i_ended_up:
            at_destination = True

        self._log.debug(f"{agent.name}: at_destination: {at_destination}")
        return at_destination

    def __sample_waypoint_from_pose(
        self, agent: AbstractAgent, tosg: SituationalGraph
    ) -> bool:
        """
        Sample a new waypoint at current agent pos, and add an edge connecting it to prev wp.
        """
        wp_at_previous_pos_candidates = tosg.get_nodes_of_type_in_margin(
            agent.previous_pos, cfg.PREV_POS_MARGIN, Situations.WAYPOINT
        )

        if len(wp_at_previous_pos_candidates) == 0:
            self._log.error(
                f"{agent.name}: No waypoint at previous pos {agent.previous_pos}, no wp added.\n {agent.name}: {agent.pos=} and {agent.get_localization()=}."
            )

            self._localize_to_waypoint(agent, tosg)

            return False

        elif len(wp_at_previous_pos_candidates) > 1:
            self._log.warning(
                f"{agent.name}: Multiple waypoints at previous pos, taking first one: {wp_at_previous_pos_candidates[0]}."
            )
            wp_at_previous_pos = wp_at_previous_pos_candidates[0]
            tosg.add_waypoint_and_diedge(agent.get_localization(), wp_at_previous_pos)
            self._localize_to_waypoint(agent, tosg)

            return True

        elif len(wp_at_previous_pos_candidates) == 1:
            wp_at_previous_pos = wp_at_previous_pos_candidates[0]
            tosg.add_waypoint_and_diedge(agent.get_localization(), wp_at_previous_pos)
            self._localize_to_waypoint(agent, tosg)

            return True

    def __add_new_frontiers_to_tosg(
        self, new_frontier_cells, lg: LocalGrid, tosg: SituationalGraph, agent
    ):
        for frontier_cell in new_frontier_cells:
            frontier_pos_global = lg.rc2xy(frontier_cell)
            tosg.add_frontier(frontier_pos_global, agent.at_wp)

    # 50% of compute time goes to this function for multiple agents
    def __prune_frontiers(self, tosg: SituationalGraph) -> None:

        ft_and_pos = [(ft, tosg.G.nodes[ft]["pos"]) for ft in tosg.frontier_idxs]

        # FIXME: this function is most expensive
        # One solution would be using neightbors property in the graph
        # so instead of doing it for the entire graph, only do it locally next to where the graph was modified
        close_frontiers = set()  # avoid duplicates

        for wp in tosg.waypoint_idxs:
            wp_pos = tosg.get_node_data_by_node(wp)["pos"]
            for ft, ft_pos in ft_and_pos:
                if (
                    abs(wp_pos[0] - ft_pos[0]) < cfg.PRUNE_RADIUS
                    and abs(wp_pos[1] - ft_pos[1]) < cfg.PRUNE_RADIUS
                ):
                    close_frontiers.add(ft)

        for frontier in close_frontiers:
            tosg.remove_frontier(frontier)
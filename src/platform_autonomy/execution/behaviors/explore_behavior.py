from typing import Optional, Sequence

from src.config import cfg
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.platform_autonomy.execution.abstract_behavior import (
    AbstractBehavior,
    BehaviorResult,
)
from src.platform_autonomy.execution.behaviors.actions.find_shortcuts_between_wps_on_lg import (
    add_shortcut_edges_between_wps_on_lg,
)
from src.platform_autonomy.state.frontier_sampling_strategies import (
    AngularLOSFrontierSamplingStrategy,
)
from src.platform_autonomy.state.local_grid import LocalGrid
from src.shared.prior_knowledge.affordance import Affordance
from src.shared.prior_knowledge.sar_situations import Situations
from src.shared.situational_graph import SituationalGraph
from src.shared.types.node_and_edge import Edge, Node
from src.shared.world_object import WorldObject


class ExploreBehavior(AbstractBehavior):
    def __init__(self, affordances: list[Affordance]):
        super().__init__(affordances)
        self._sampling_strategy = AngularLOSFrontierSamplingStrategy()

    def _run_behavior_implementation(
        self, agent: AbstractAgent, situational_graph: SituationalGraph, behavior_edge
    ) -> BehaviorResult:
        target_node = behavior_edge[1]
        target_node_pos = situational_graph.get_node_data_by_node(target_node)["pos"]

        """The first exploration step is just sampling in place."""
        # HACK: this should just be an init behavior or something.
        if not agent.init_explore_step_completed:
            lg = agent.get_local_grid()
            new_frontier_cells = self._sampling_strategy.sample_frontiers(lg)
            # BUG: something goes wrong when sampling with the Angular strategy here
            self.__add_new_frontiers_to_situational_graph(new_frontier_cells, lg, situational_graph, agent)
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
        situational_graph: SituationalGraph,
        result: BehaviorResult,
        behavior_edge: Edge,
    ):
        """Check if the postconditions for the behavior are met."""
        next_node = behavior_edge[1]
        return self.__check_at_destination(agent, situational_graph, next_node)

    # FIXME: this is an expensive function
    def _mutate_graph_and_tasks_success(
        self,
        agent: AbstractAgent,
        situational_graph: SituationalGraph,
        result: BehaviorResult,
        behavior_edge: Edge,
        affordances: list[Affordance],
    ):
        next_node = behavior_edge[1]
        self._log.debug(
            f"{agent.name}: Now the frontier is visited it can be removed to sample a waypoint in its place."
        )
        # start mutate graph
        situational_graph.remove_node_and_tasks(next_node)
        lg = agent.get_local_grid()

        """part 1: use local grid to process new virtual objects"""
        # HACK: this is to deal with explosion of frontiers if we cannot sample a new wp
        if not self.__sample_waypoint_from_pose(agent, situational_graph):
            self._log.error("sampling waypoint failed")

        # FIXME: this is my 2nd  most expensive function, so I should try to optimize it
        new_frontier_cells = self._sampling_strategy.sample_frontiers(lg)

        self.__add_new_frontiers_to_situational_graph(new_frontier_cells, lg, situational_graph, agent)

        # FIXME: this is my 3nd expensive function, so I should try to optimize it
        self.__prune_frontiers(situational_graph)

        add_shortcut_edges_between_wps_on_lg(lg, situational_graph, agent)

        """part 2: use perception service to sense new world objects"""
        # 1. obtain world objects in perception scene
        worldobjects = self.__process_world_objects(agent, situational_graph, affordances)

        if worldobjects:
            # 2. check if they not already in the graph
            for wo in worldobjects:
                if situational_graph.get_node_by_exact_pos(wo.pos):
                    self._log.debug(
                        f"{wo.object_type} at {wo.pos} already in the graph"
                    )
                    return

            # 3. add them to the graph
            for wo in worldobjects:
                self._log.debug(
                    f">>>>{agent.name}: adding world object {wo.object_type}"
                )

                situational_graph.add_node_with_task_and_edges_from_affordances(
                    agent.at_wp, wo.object_type, wo.pos, affordances
                )

    def mutate_graph_and_tasks_failure(
        self, agent: AbstractAgent, situational_graph: SituationalGraph, behavior_edge: Edge
    ):
        # Recovery behaviour
        self._log.warning(
            f"{agent.name}: did not reach destination during explore action."
        )
        # this is the actual mutation of the grpah on failure
        situational_graph.remove_node_and_tasks(behavior_edge[1])
        # maintain the previous heading to stop tedious turning
        # TODO: this move to pos is the recovery of the behavior, it should be in the run method.
        agent.move_to_pos(
            situational_graph.get_node_data_by_node(behavior_edge[0])["pos"], agent.heading
        )
        agent.previous_pos = agent.get_localization()

        # this is the actual mutation of the grpah on failure
        self.__prune_frontiers(situational_graph)

    ##############################################################################################
    # exploration specific functions
    ##############################################################################################

    # TODO: move this to agent services or smth
    def __process_world_objects(
        self,
        agent: AbstractAgent,
        situational_graph: SituationalGraph,
        affordances: Sequence[Affordance],
    ) -> Optional[Sequence[WorldObject]]:
        return agent.look_for_world_objects_in_perception_scene()
        # TODO: this should  return the object type and pose so that we can process it in the mutate graph step

    def __check_at_destination(
        self, agent: AbstractAgent, situational_graph: SituationalGraph, destination_node: Node
    ) -> bool:
        at_destination = False
        destination_node_type = situational_graph.get_node_data_by_node(destination_node)["type"]

        nodes_near_where_i_ended_up = situational_graph.get_nodes_of_type_in_margin(
            agent.get_localization(),
            cfg.MOVE_TO_POS_ARRIVAL_MARGIN,
            destination_node_type,
        )

        if destination_node in nodes_near_where_i_ended_up:
            at_destination = True

        self._log.debug(f"{agent.name}: at_destination: {at_destination}")
        return at_destination

    def __sample_waypoint_from_pose(
        self, agent: AbstractAgent, situational_graph: SituationalGraph
    ) -> bool:
        """
        Sample a new waypoint at current agent pos, and add an edge connecting it to prev wp.
        """

        wp_at_previous_pos = situational_graph.get_closest_waypoint_to_pos(agent.previous_pos)
        if not wp_at_previous_pos:
            self._log.error(
                f"{agent.name}: No waypoint at previous pos {agent.previous_pos}, no wp added.\n {agent.name}: {agent.pos=} and {agent.get_localization()=}."
            )
            return False

        new_wp = situational_graph.add_node_of_type(agent.get_localization(), Situations.WAYPOINT)
        situational_graph.add_waypoint_diedge(new_wp, wp_at_previous_pos)

        agent.at_wp = situational_graph.get_closest_waypoint_to_pos(agent.get_localization())
        return True

    def __add_new_frontiers_to_situational_graph(
        self, new_frontier_cells, lg: LocalGrid, situational_graph: SituationalGraph, agent
    ):
        for frontier_cell in new_frontier_cells:
            frontier_pos_global = lg.rc2xy(frontier_cell)
            situational_graph.add_node_with_task_and_edges_from_affordances(
                agent.at_wp, Situations.FRONTIER, frontier_pos_global, self.AFFORDANCES
            )

    # 50% of compute time goes to this function for multiple agents
    def __prune_frontiers(self, situational_graph: SituationalGraph) -> None:

        ft_and_pos = [
            (ft, situational_graph.G.nodes[ft]["pos"])
            for ft in situational_graph.get_nodes_by_type(Situations.FRONTIER)
        ]

        # FIXME: this function is most expensive
        # One solution would be using neightbors property in the graph
        # so instead of doing it for the entire graph, only do it locally next to where the graph was modified
        close_frontiers = set()  # avoid duplicates

        # for wp in situational_graph.waypoint_idxs:
        for wp in situational_graph.get_nodes_by_type(Situations.WAYPOINT):
            wp_pos = situational_graph.get_node_data_by_node(wp)["pos"]
            for ft, ft_pos in ft_and_pos:
                if (
                    abs(wp_pos[0] - ft_pos[0]) < cfg.PRUNE_RADIUS
                    and abs(wp_pos[1] - ft_pos[1]) < cfg.PRUNE_RADIUS
                ):
                    close_frontiers.add(ft)

        for frontier in close_frontiers:
            situational_graph.remove_node_and_tasks(frontier)

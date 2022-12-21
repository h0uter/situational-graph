from src.core import event_system
from src.core.topics import Topics
from src.mission_autonomy.mission_initializer import MissionInitializer
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.shared.plan import Plan
from src.shared.prior_knowledge.sar_behaviors import Behaviors
from src.shared.prior_knowledge.sar_objectives import Objectives
from src.shared.prior_knowledge.sar_situations import Situations
from src.shared.situational_graph import SituationalGraph
from src.shared.task import Task


class ExplorationMissionInitializer(MissionInitializer):
    """This is the initializer for the search and rescue exploration usecase"""

    def initialize_mission(
        self, agents: list[AbstractAgent], situational_graph: SituationalGraph
    ):
        """Manually set first task to exploring current position."""

        self.init_place_initial_waypoint_for_each_start_pose(
            situational_graph, start_poses=[agent.pos for agent in agents]
        )
        self.init_localize_agents_to_waypoints(agents, situational_graph)
        self.init_create_first_tasks(agents, situational_graph)

    @staticmethod
    def init_place_initial_waypoint_for_each_start_pose(
        situational_graph: SituationalGraph,
        start_poses: list[tuple[float, float]],
    ):
        """Add a waypoint to the situational_graph for each agent, but check for duplicates"""
        duplicate_start_poses = []
        for start_pos in start_poses:
            if start_pos in duplicate_start_poses:
                continue

            situational_graph.add_node_of_type(start_pos, Situations.WAYPOINT)
            duplicate_start_poses.append(start_pos)

    @staticmethod
    def init_localize_agents_to_waypoints(
        agents: list[AbstractAgent], situational_graph: SituationalGraph
    ):
        """setup vizualisation of start poses"""
        for agent in agents:
            agent.get_local_grid()
            agent.at_wp = situational_graph.get_closest_waypoint_to_pos(agent.pos)

            event_system.post_event(Topics.VIEW__MISSION_START_POINT, agent.pos)

    @staticmethod
    def init_create_first_tasks(
        agents: list[AbstractAgent], situational_graph: SituationalGraph
    ):
        """Manually set first task to exploring current position."""
        for agent in agents:

            # Add an explore edge on the start node to ensure a exploration sampling action
            edge = situational_graph.add_edge_of_type(
                agent.at_wp, agent.at_wp, Behaviors.EXPLORE
            )
            situational_graph.tasks.append(Task(edge, Objectives.EXPLORE_ALL_FTS))

            # spoof the task selection, just select the first one.
            agent.task = situational_graph.tasks[0]

            # obtain the plan which corresponds to this edge.
            init_explore_edge = agent.task.edge

            agent.plan = Plan([init_explore_edge])

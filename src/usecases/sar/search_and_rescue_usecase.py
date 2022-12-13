import time
from abc import ABC, abstractmethod
from typing import Sequence
from src.mission_autonomy.abstract_planner import Executor

import src.shared.event_system as event_system
from src.config import Scenario, cfg
from src.execution_autonomy.abstract_behavior import AbstractBehavior
from src.execution_autonomy.plan_model import PlanModel
from src.mission_autonomy.online_planner import OnlinePlanner
from src.mission_autonomy.situational_graph import SituationalGraph
from src.platform_control.abstract_agent import AbstractAgent
from src.platform_control.real.spot_agent import SpotAgent
from src.platform_control.sim.simulated_agent import SimulatedAgent
from src.shared.prior_knowledge.behaviors import Behaviors
from src.shared.prior_knowledge.capabilities import Capabilities
from src.shared.prior_knowledge.objectives import Objectives
from src.shared.task import Task
from src.shared.topics import Topics
from src.usecases.feedback_pipeline import (
    feedback_pipeline_completion,
    feedback_pipeline_init,
    feedback_pipeline_single_step,
)
from src.usecases.sar.sar_affordances import SAR_AFFORDANCES
from src.usecases.sar.sar_behaviors import SAR_BEHAVIORS

# I want my mainloop to only contain 4 high level steps:
# 1. mission_logic
# 2. platform logic
# 3. process events


def common_initialization(
    tosg: SituationalGraph, agents: Sequence[AbstractAgent], start_poses
):
    """Add a waypoint to the tosg for each agent, but check for duplicates"""
    duplicate_start_poses = []
    for start_pos in start_poses:
        if start_pos not in duplicate_start_poses:
            tosg.add_waypoint_node(start_pos)
            duplicate_start_poses.append(start_pos)

    """setup vizualisation of start poses"""
    for agent in agents:
        agent.get_local_grid()
        # agent.localize_to_waypoint(tosg)
        # HACK: not ideal but this removes dependency of agent on tosg
        AbstractBehavior._localize_to_waypoint(agent, tosg)
        event_system.post_event(
            str(Topics.MISSION_VIEW_START_POINT), agent.pos
        )  # viz start position


class Usecase(ABC):
    def __init__(self):
        self.step = 0
        self.mission_completed = False

    def run(self):
        """setup the specifics of the usecase"""
        agents, tosg, planner = self.domain_initialization()

        success = self.main_loop(agents, tosg, planner)

        return success

    @abstractmethod
    def domain_initialization(
        self,
    ) -> tuple[list[AbstractAgent], SituationalGraph, OnlinePlanner]:
        pass

    def main_loop(
        self,
        agents: list[AbstractAgent],
        tosg: SituationalGraph,
        planner: OnlinePlanner,
    ):

        start, tosg_stats, my_logger = feedback_pipeline_init()

        """ Main Logic Loop"""
        while (not self.mission_completed) and self.step < cfg.MAX_STEPS:

            self.inner_loop(agents, tosg, planner, my_logger, tosg_stats)

        feedback_pipeline_completion(
            self.step, agents, tosg, tosg_stats, planner, my_logger, start
        )

        # krm_stats.save()
        return self.mission_completed

    def inner_loop(self, agents, tosg, planner, my_logger, tosg_stats):
        step_start = time.perf_counter()

        # task allocation

        for agent_idx in range(len(agents)):
            # TODO: split this into task allocation, planning and execution
            
            # planning 
            if planner.pipeline(agents[agent_idx], tosg):

                """pipeline returns true if there are no more tasks."""
                self.mission_completed = True
                my_logger.info(f"Agent {agent_idx} completed exploration")
                break

            # execution

        feedback_pipeline_single_step(
            self.step, step_start, agents, tosg, tosg_stats, planner, my_logger
        )
        self.step += 1


class SearchAndRescueUsecase(Usecase):
    @staticmethod
    def init_search_and_rescue_entities() -> tuple[
        list[AbstractAgent], SituationalGraph, OnlinePlanner
    ]:
        agent1_capabilities = {Capabilities.CAN_ASSESS}
        if cfg.SCENARIO == Scenario.REAL:
            agents = [SpotAgent(agent1_capabilities)]
        else:
            agents = [
                SimulatedAgent(agent1_capabilities)
            ]  # make the first agent only posses the capabilities
            agents.extend([SimulatedAgent(set(), i) for i in range(1, cfg.NUM_AGENTS)])

        tosg = SituationalGraph()

        domain_behaviors = SAR_BEHAVIORS
        affordances = SAR_AFFORDANCES
        # planner = OfflinePlanner(domain_behaviors, affordances)
        executor = Executor(domain_behaviors, affordances)
        planner = OnlinePlanner(executor)

        return agents, tosg, planner

    def domain_initialization(self):
        """Manually set first task to exploring current position."""

        agents, tosg, planner = self.init_search_and_rescue_entities()

        common_initialization(tosg, agents, start_poses=[agent.pos for agent in agents])

        for agent in agents:

            # Add an explore edge on the start node to ensure a exploration sampling action
            edge = tosg.add_edge_of_type(agent.at_wp, agent.at_wp, Behaviors.EXPLORE)
            tosg.tasks.append(Task(edge, Objectives.EXPLORE_ALL_FTS))

            # spoof the task selection, just select the first one.
            agent.task = tosg.tasks[0]

            # obtain the plan which corresponds to this edge.
            init_explore_edge = agent.task.edge

            agent.plan = PlanModel([init_explore_edge])

        return agents, tosg, planner

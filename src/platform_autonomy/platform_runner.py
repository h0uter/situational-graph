from dataclasses import dataclass
from typing import Mapping, Type

from src.core.event_system import subscribe
from src.core.topics import Topics
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.platform_autonomy.execution.abstract_behavior import AbstractBehavior
from src.platform_autonomy.execution.plan_executor import PlanExecutor
from src.platform_autonomy.planning.graph_task_planner import (
    CouldNotFindPlan,
    GraphTaskPlanner,
    TargetNodeNotFound,
)
from src.shared.prior_knowledge.sar_behaviors import Behaviors
from src.shared.situational_graph import SituationalGraph


@dataclass
class PlatformRunnerMessage:
    # this is still coupled more than I would like because we send object references.
    agent: AbstractAgent
    situational_graph: SituationalGraph


class PlatformRunner:
    def __init__(
        self, affordances: list, behaviors: Mapping[Behaviors, Type[AbstractBehavior]]
    ):
        subscribe(Topics.RUN_PLATFORM, self.platform_runner)

        # TODO: this prior knowledge needs to be injected from the usecase

        self.plan_executor = PlanExecutor(behaviors, affordances)
        self.planner = GraphTaskPlanner()

    def platform_runner(self, data: PlatformRunnerMessage):
        agent = data.agent
        situational_graph = data.situational_graph

        if agent.init_explore_step_completed:
            filtered_situational_graph = situational_graph.get_filtered_graph(agent.capabilities)

            """planning"""
            try:
                agent.plan = self.planner.find_plan_for_task(
                    agent.at_wp, situational_graph, agent.task, filtered_situational_graph
                )
            except CouldNotFindPlan:
                self.planner._log.error(f"Could not find a plan for task {agent.task}")
                agent.clear_task()
            except TargetNodeNotFound:
                self.planner._log.error(
                    f"Could not find a target node for task {agent.task}"
                )
                agent.clear_task()

        """execution"""
        if agent.plan:
            # if agent.plan and (agent.task in situational_graph.tasks):
            result = self.plan_executor.execute_plan(agent, situational_graph, agent.plan)

            self.plan_executor.process_execution_result(result, agent, situational_graph)

        # TODO: make this publish execution results to the mission system.

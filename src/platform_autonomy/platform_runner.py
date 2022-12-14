from dataclasses import dataclass

from src.core.event_system import subscribe
from src.core.planning.graph_task_planner import (
    CouldNotFindPlan,
    GraphTaskPlanner,
    TargetNodeNotFound,
)
from src.core.topics import Topics
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.platform_autonomy.execution.plan_executor import PlanExecutor
from src.shared.sar_affordances import SAR_AFFORDANCES
from src.shared.situational_graph import SituationalGraph
from src.usecases.search_and_rescue.sar_behaviors import SAR_BEHAVIORS


@dataclass
class PlatformRunnerMessage:
    # this is still coupled more than I would like because we send object references.
    agent: AbstractAgent
    tosg: SituationalGraph


class PlatformRunner:
    def __init__(self):
        subscribe(Topics.RUN_PLATFORM, self.platform_runner)

        # TODO: this prior knowledge needs to be injected from the usecase
        domain_behaviors = SAR_BEHAVIORS
        affordances = SAR_AFFORDANCES

        self.plan_executor = PlanExecutor(domain_behaviors, affordances)
        self.planner = GraphTaskPlanner()

    def platform_runner(self, data: PlatformRunnerMessage):
        agent = data.agent
        tosg = data.tosg

        # if not agent.task:
        #     return

        if agent.init_explore_step_completed:
            filtered_tosg = tosg._filter_graph(agent.capabilities)

            """planning"""
            try:
                agent.plan = self.planner.find_plan_for_task(
                    agent.at_wp, tosg, agent.task, filtered_tosg
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
        # if agent.plan and (agent.task in tosg.tasks):
            result = self.plan_executor.execute_plan(agent, tosg, agent.plan)

            self.plan_executor.process_execution_result(result, agent, tosg)

        # TODO: make this publish execution results to the mission system.

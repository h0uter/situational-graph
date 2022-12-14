from dataclasses import dataclass
from src.mission_autonomy.graph_task_planner import (
    CouldNotFindPlan,
    GraphTaskPlanner,
    TargetNodeNotFound,
)
from src.mission_autonomy.sar.sar_affordances import SAR_AFFORDANCES
from src.mission_autonomy.sar.sar_behaviors import SAR_BEHAVIORS
from src.mission_autonomy.situational_graph import SituationalGraph
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.platform_autonomy.plan_executor import PlanExecutor
from src.core.event_system import subscribe
from src.core.topics import Topics

@dataclass
class PlatformRunnerMessage:
    agent: AbstractAgent
    tosg: SituationalGraph

class PlatformRunner:
    def __init__(self):
        subscribe(Topics.RUN_PLATFORM, self.platform_runner)

    @staticmethod
    def platform_runner(data: PlatformRunnerMessage):
        agent = data.agent 
        tosg = data.tosg
        print("recieved platform runner event: ", agent, tosg)
        planner = GraphTaskPlanner()
        domain_behaviors = SAR_BEHAVIORS
        affordances = SAR_AFFORDANCES
        plan_executor = PlanExecutor(domain_behaviors, affordances)

        if agent.init_explore_step_completed:

            # # TODO: conceptually figure out who should do the filtering of the graph
            filtered_tosg = planner._filter_graph(tosg, agent.capabilities)

            """---------------------------------------"""
            # TODO: this should be a post event that posts a task to a platform
            # so I send a task and a sg to the platform. it changes the sg.
            # so still shared state in the sg object
            # but the plan_excutor, the planner can be moved to the platform.

            # planning
            try:
                agent.plan = planner.find_plan_for_task(
                    agent.at_wp, tosg, agent.task, filtered_tosg
                )
            except CouldNotFindPlan:
                planner._log.error(f"Could not find a plan for task {agent.task}")
                agent.clear_task()
            except TargetNodeNotFound:
                planner._log.error(f"Could not find a target node for task {agent.task}")
                agent.clear_task()

        # execution
        if agent.plan:
            result = plan_executor._plan_execution(agent, tosg, agent.plan)

            plan_executor.process_execution_result(result, agent, tosg)
            

from src.mission.graph_task_planner import (
    CouldNotFindPlan,
    CouldNotFindTask,
    TargetNodeNotFound,
)
from src.mission.plan_executor import destroy_task
from src.mission.graph_planner_interface import GraphPlannerInterface
from src.mission.situational_graph import SituationalGraph
from src.platform.control.abstract_agent import AbstractAgent


class OfflinePlanner(GraphPlannerInterface):
    def pipeline(self, agent: AbstractAgent, tosg: SituationalGraph) -> bool:
        """filter the graph over the agent capabilities"""

        filtered_tosg = self._filter_graph(tosg, agent)

        """select a task"""
        if not agent.task:
            try:
                agent.task = self._task_selection(agent, filtered_tosg)
                if not agent.task:
                    raise CouldNotFindTask(
                        f"Could not find a task for agent {agent.name}"
                    )
            except CouldNotFindTask as e:
                self._log.error(e)
                return False

        """ generate a plan"""
        if not agent.plan:
            try:
                agent.plan = self._find_plan_for_task(
                    agent.at_wp, tosg, agent.task, filtered_tosg
                )
            except CouldNotFindPlan:
                self._log.error(f"Could not find a plan for task {agent.task}")
                agent.clear_task()
            except TargetNodeNotFound:
                self._log.error(f"Could not find a target node for task {agent.task}")
                agent.clear_task()

        """ execute the plan"""
        if agent.plan and len(agent.plan) >= 1:
            # TODO: make this also use the filtered_tosg
            agent.plan = self._plan_execution(agent, tosg, agent.plan)

            if agent.plan and len(agent.plan) == 0:
                destroy_task(agent, tosg)

        """check completion of mission"""
        return _check_if_tasks_exhausted(tosg)

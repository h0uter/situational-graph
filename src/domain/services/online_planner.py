from src.domain.services.abstract_agent import AbstractAgent
from src.domain.services.offline_planner import OfflinePlanner, CouldNotFindPlan, CouldNotFindTask, TargetNodeNotFound
from src.domain.services.tosg import TOSG


class OnlinePlanner(OfflinePlanner):
    '''This planner selects the optimal task and makes a plan each iteration'''
    def pipeline(self, agent: AbstractAgent, tosg: TOSG) -> bool:

        if agent.init_explore_step_completed:

            filtered_tosg = self._filter_graph(tosg, agent)

            # this fails because we overide the initialisation
            """select a task"""
            # agent.task = self._task_selection(agent, tosg)
            agent.task = self._task_selection(agent, filtered_tosg)
            if not agent.task:
                return self._check_if_tasks_exhausted(tosg)

            """ generate a plan"""
            try:
                agent.plan = self._find_plan_for_task(agent.at_wp, tosg, agent.task, filtered_tosg)
            except CouldNotFindPlan:
                self._log.error(f"Could not find a plan for task {agent.task}")
                agent.clear_task()
            except TargetNodeNotFound:
                self._log.error(f"Could not find a target node for task {agent.task}")
                agent.clear_task()

        """ execute the plan"""
        agent.plan = self._plan_execution(agent, tosg, agent.plan)

        if agent.plan and len(agent.plan) == 0:
            self._destroy_task(agent, tosg)

        """check completion of mission"""
        return self._check_if_tasks_exhausted(tosg)

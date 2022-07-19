from src.domain.services.abstract_agent import AbstractAgent
from src.domain.services.offline_planner import OfflinePlanner
from src.domain.services.tosg import TOSG


class OnlinePlanner(OfflinePlanner):
    '''This planner selects the optimal task and makes a plan each iteration'''
    def pipeline(self, agent: AbstractAgent, tosg: TOSG) -> bool:

        if agent.init_explore_step_completed:
            # this fails because we overide the initialisation
            """select a task"""
            agent.task = self._task_selection(agent, tosg)

            """ generate a plan"""
            agent.plan = self._find_plan_for_task(agent.at_wp, tosg, agent.task)

        """ execute the plan"""
        agent.plan = self._plan_execution(agent, tosg, agent.plan)

        if agent.plan and len(agent.plan) == 0:
            self._destroy_task(agent, tosg)

        """check completion of mission"""
        return self._check_if_tasks_exhausted(tosg)

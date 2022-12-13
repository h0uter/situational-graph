from typing import Sequence

from src.execution_autonomy.plan_model import PlanModel
from src.mission_autonomy.situational_graph import SituationalGraph
from src.platform_control.abstract_agent import AbstractAgent
from src.shared.prior_knowledge.behaviors import Behaviors
from src.shared.prior_knowledge.objectives import Objectives
from src.shared.task import Task
from src.usecases.usecase import Usecase


class SearchAndRescueUsecase(Usecase):
    def run(self):
        agents, tosg, usecases = self.init_entities()
        self.common_setup(tosg, agents, start_poses=[agent.pos for agent in agents])

        """setup the specifics of the usecase"""
        self.setup(tosg, agents)

        success = self.main_loop(agents, tosg, usecases)

        return success

    def setup(self, tosg: SituationalGraph, agents: Sequence[AbstractAgent]):
        """Manually set first task to exploring current position."""

        for agent in agents:

            # Add an explore self edge on the start node to ensure a exploration sampling action
            edge = tosg.add_edge_of_type(agent.at_wp, agent.at_wp, Behaviors.EXPLORE)
            tosg.tasks.append(Task(edge, Objectives.EXPLORE_ALL_FTS))

            # spoof the task selection, just select the first one.
            agent.task = tosg.tasks[0]

            # obtain the plan which corresponds to this edge.
            init_explore_edge = agent.task.edge

            agent.plan = PlanModel([init_explore_edge])

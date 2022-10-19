from typing import Sequence

from src.domain import TOSG, Behaviors, Objectives, Plan, Task
from src.domain.services.abstract_agent import AbstractAgent
from src.usecases.usecase import Usecase

class SearchAndRescueUsecase(Usecase):
    def run(self):
        agents, tosg, usecases, viz_listener = self.init_entities()
        self.common_setup(
            tosg, agents, start_poses=[agent.pos for agent in agents]
        )

        """setup the specifics of the usecase"""
        self.setup(tosg, agents)

        success = self.run_demo(agents, tosg, usecases, viz_listener)

        return success

    def setup(self, tosg: TOSG, agents: Sequence[AbstractAgent]):
        """Manually set first task to exploring current position."""
        # for the demo I dont need this setup, I can instead manually craft the graph.
        for agent in agents:

            # Add an explore self edge on the start node to ensure a exploration sampling action
            edge = tosg.add_edge_of_type(agent.at_wp, agent.at_wp, Behaviors.EXPLORE)
            tosg.tasks.append(Task(edge, Objectives.EXPLORE_ALL_FTS))

            # spoof the task selection, just select the first one.
            agent.task = tosg.tasks[0]

            # obtain the plan which corresponds to this edge.
            init_explore_edge = agent.task.edge

            agent.plan = Plan([init_explore_edge])

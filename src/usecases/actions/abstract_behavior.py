from abc import ABC, abstractmethod
from typing import Sequence
from src.utils.config import Config

import logging


class AbstractBehavior(ABC):
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._log = logging.getLogger(__name__)

    def execute_pipeline(self, agent, tosgraph, plan) -> Sequence:
        """Execute the behavior pipeline."""

        behavior_edge = plan[0]
        if not self.check_preconditions(agent, tosgraph, behavior_edge):
            return []

        result = self.run(agent, tosgraph, behavior_edge)
        if not result:
            plan = []
            return plan

        if self.check_postconditions(agent, tosgraph, result, plan):
            tosgraph = self.mutate_graph_success(agent, tosgraph, behavior_edge[1])
            plan.pop(0)
        else:
            tosgraph = self.mutate_graph_failure(agent, tosgraph, behavior_edge)
            plan = []

        return plan

    @abstractmethod
    def check_preconditions(self, agent, tosgraph, behavior_edge) -> bool:
        pass

    @abstractmethod
    def run(self, agent, tosgraph, action_path):
        pass

    @abstractmethod
    def check_postconditions(self, agent, tosgraph, result, plan) -> bool:
        """Check if the postconditions for the behavior are met."""
        pass

    # @abstractmethod
    # def perception_to_tasks(self):  # -> list[Object]
    #     pass

    @abstractmethod
    def mutate_graph_success(self, agent, tosgraph, next_node):
        """Mutate the graph according to the behavior."""
        pass

    @abstractmethod
    def mutate_graph_failure(self, agent, tosgraph, action_path):
        """Mutate the graph according to the behavior."""
        pass




    # 1. check_preconditions(agent, edge)
    # 2. results = run()
    # 3. if check_postconditions(result, sensors)
        # graph, plan = mutate_success(graph, plan)
        # tasks = check_perception_scene()
    # else:
        # graph, plan = mutate_failure(graph, plan)
    
    # return plan

    # these should all be methods of the behavior, so the run method is then still a wrapper for the actual behavior implementation.

    ## concretely for goto
    # 1. localisation at source node
    # 2. return success 
    # 3. check localisation matches target node.
        # - check perception scene and instantiate new tasks through affordances
        # pop shit uit die plan

    ## concretely for explore
    # 1. localisation at source node
    # 2. return {frontiers, new world objects}
    # 3. check localisation matches target node, (check frontiers are valid with current local grid.)
        # - remove current frontier and replace with wp
        # - check perception scene and instantiate new tasks through affordances

    ## concretely for assess/inspect/whatever
    # 1. localisation at source node
    # 2. return {data collected}
    # 3. check localisation matches source node, (check data collected matches goal of behavior) (ex. picture contains class of object interested in.)
        # - mark world object completed, mark task completed.
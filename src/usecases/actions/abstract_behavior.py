from abc import ABC, abstractmethod
from typing import Sequence
from src.utils.config import Config

import logging


class AbstractBehavior(ABC):
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._log = logging.getLogger(__name__)

    def execute_pipeline(self, agent, TOSgraph, plan) -> Sequence:
        """Execute the behavior pipeline."""
        if not self.check_preconditions(agent, TOSgraph):
            return []

        result = self.run(agent, TOSgraph, plan)

        plan = self.run(agent, TOSgraph, plan)
        if self.check_postconditions(agent, result):
            plan = self.mutate_graph_success(agent, TOSgraph)
        else:
            plan = self.mutate_graph_failure(agent, TOSgraph)

        return plan

    # @abstractmethod
    # def check_preconditions(self, agent, krm) -> bool:
    #     pass

    # @abstractmethod
    # def run(self, agent, krm, action_path) -> list:
    #     pass

    # @abstractmethod
    # def check_postconditions(self, agent, krm) -> bool:
    #     """Check if the postconditions for the behavior are met."""
    #     pass

    # @abstractmethod
    # def perception_to_tasks(self):  # -> list[Object]
    #     pass

    # @abstractmethod
    # def mutate_graph_success(self, agent, krm) -> Sequence:
    #     """Mutate the graph according to the behavior."""
    #     pass

    # @abstractmethod
    # def mutate_graph_failure(self, agent, krm) -> Sequence:
    #     """Mutate the graph according to the behavior."""
    #     pass




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
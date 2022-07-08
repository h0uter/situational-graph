import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.entities.static_data.affordances import AFFORDANCES
from src.entities.tosg import TOSG
from src.utils.config import Config


@dataclass
class BehaviorResult:
    success: bool
    # can_task_be_cleared: bool


class AbstractBehavior(ABC):
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._log = logging.getLogger(__name__)

    def execute_pipeline(self, agent, tosg: TOSG, plan) -> BehaviorResult:
        """Execute the behavior pipeline."""

        # FIXME: make this use just the edge and present a result.
        behavior_edge = plan[0]

        result = self.run_implementation(agent, tosg, behavior_edge)

        if not result.success:
            return result

        if self.check_postconditions(agent, tosg, result, plan):
            self._log.debug(f"postconditions satisfied")
            # TODO: make it actually mutate tasks
            self.mutate_graph_and_tasks_success(
                agent, tosg, behavior_edge[1], AFFORDANCES
            )
        else:
            # TODO: make it actually mutate tasks
            self._log.debug(f"postconditions not satisfied")
            self.mutate_graph_and_tasks_failure(agent, tosg, behavior_edge)

        tosg.remove_invalid_tasks()

        return result

    @abstractmethod
    def run_implementation(self, agent, tosgraph, plan) -> BehaviorResult:
        pass

    @abstractmethod
    def check_postconditions(self, agent, tosgraph, result, plan) -> bool:
        """Check if the postconditions for the behavior are met."""
        pass

    # @abstractmethod
    # def perception_to_tasks(self):  # -> list[Object]
    #     pass

    @abstractmethod
    def mutate_graph_and_tasks_success(self, agent, tosgraph, next_node, affordances):
        """Mutate the graph according to the behavior."""
        pass

    @abstractmethod
    def mutate_graph_and_tasks_failure(self, agent, tosgraph, plan):
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

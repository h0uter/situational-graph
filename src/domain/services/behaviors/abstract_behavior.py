import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.domain import TOSG, Edge
from src.usecases.sar_affordances import SAR_AFFORDANCES
from src.configuration.config import Config


@dataclass
class BehaviorResult:
    success: bool
    # can_task_be_cleared: bool


class AbstractBehavior(ABC):
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._log = logging.getLogger(__name__)

    def pipeline(self, agent, tosg: TOSG, behavior_edge: Edge) -> BehaviorResult:
        """Execute the behavior pipeline."""

        result = self._run_behavior_implementation(agent, tosg, behavior_edge)

        if not result.success:
            return result

        if self._check_postconditions(agent, tosg, result, behavior_edge):
            self._log.debug(f"postconditions satisfied")
            # TODO: make it actually mutate tasks
            self._mutate_graph_and_tasks_success(
                agent, tosg, behavior_edge, SAR_AFFORDANCES
            )
        else:
            # TODO: make it actually mutate tasks
            self._log.debug(f"postconditions not satisfied")
            self._mutate_graph_and_tasks_failure(agent, tosg, behavior_edge)

        tosg.remove_invalid_tasks()

        return result

    @abstractmethod
    def _run_behavior_implementation(
        self, agent, tosgraph: TOSG, behavior_edge: Edge
    ) -> BehaviorResult:
        pass

    @abstractmethod
    def _check_postconditions(
        self, agent, tosgraph: TOSG, result, behavior_edge: Edge
    ) -> bool:
        """Check if the postconditions for the behavior are met."""
        pass

    # @abstractmethod
    # def perception_to_tasks(self):  # -> list[Object]
    #     pass

    @abstractmethod
    def _mutate_graph_and_tasks_success(
        self, agent, tosgraph: TOSG, next_node, affordances
    ):
        """Mutate the graph according to the behavior."""
        pass

    @abstractmethod
    def _mutate_graph_and_tasks_failure(
        self, agent, tosgraph: TOSG, behavior_edge: Edge
    ):
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

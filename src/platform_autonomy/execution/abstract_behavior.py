import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

from src.config import cfg
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.shared.prior_knowledge.affordance import Affordance
from src.shared.prior_knowledge.sar_situations import Situations
from src.shared.situational_graph import SituationalGraph
from src.shared.types.node_and_edge import Edge


@dataclass
class BehaviorResult:
    success: bool


class AbstractBehavior(ABC):
    def __init__(self, affordances: Sequence[Affordance]) -> None:
        self._log = logging.getLogger(__name__)
        self.AFFORDANCES = affordances

    def pipeline(
        self, agent: AbstractAgent, tosg: SituationalGraph, behavior_edge: Edge
    ) -> BehaviorResult:
        """Execute the behavior pipeline."""

        result = self._run_behavior_implementation(agent, tosg, behavior_edge)

        if not result.success:
            return result

        if self._check_postconditions(agent, tosg, result, behavior_edge):
            self._log.debug(f"postconditions satisfied")
            # TODO: make it actually mutate tasks
            self._mutate_graph_and_tasks_success(
                agent, tosg, result, behavior_edge, self.AFFORDANCES
            )
        else:
            # TODO: make it actually mutate tasks
            self._log.debug(f"postconditions not satisfied")
            self._mutate_graph_and_tasks_failure(agent, tosg, behavior_edge)

        return result

    @abstractmethod
    def _run_behavior_implementation(
        self, agent, tosgraph: SituationalGraph, behavior_edge: Edge
    ) -> BehaviorResult:
        pass

    @abstractmethod
    def _check_postconditions(
        self,
        agent: AbstractAgent,
        tosgraph: SituationalGraph,
        result,
        behavior_edge: Edge,
    ) -> bool:
        """Check if the postconditions for the behavior are met."""
        pass

    @abstractmethod
    def _mutate_graph_and_tasks_success(
        self,
        agent: AbstractAgent,
        tosg: SituationalGraph,
        result: BehaviorResult,
        behavior_edge: Edge,
        affordances: Sequence[Affordance],
    ):
        pass

    @abstractmethod
    def _mutate_graph_and_tasks_failure(
        self, agent: AbstractAgent, tosgraph: SituationalGraph, behavior_edge: Edge
    ):
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

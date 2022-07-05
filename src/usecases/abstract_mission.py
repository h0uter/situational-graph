from abc import ABC, abstractmethod
import logging
from typing import Optional, Sequence, Literal

from src.entities.abstract_agent import AbstractAgent
from src.entities.krm import KRM
from src.utils.config import Config
from src.utils.my_types import Node, EdgeType, Edge


class AbstractMission(ABC):
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.completed = False
        self.action_path: Sequence[Optional[Edge]] = []
        self.target_node: Optional[Node] = None
        self._log = logging.getLogger(__name__)

    # CONTEXT
    def main_loop(self, agent: AbstractAgent, krm: KRM) -> bool:
        something_was_done = False

        if not self.check_target_available(krm) and not agent.init:
            self._log.debug(
                f"{agent.name}: No targets available. Performing initialization."
            )
            self.action_path, self.target_node = self.setup_target_initialisation(krm)

        if self.target_node is None:
            self._log.debug(f"{agent.name}: No target node set. Setting one.")
            self.target_node = self.target_selection(agent, krm)
            something_was_done = True

        if not self.action_path:
            self._log.debug(
                f"{agent.name}: No action path set. Finding one to {self.target_node}."
            )
            self.action_path = self.path_generation(agent, krm, self.target_node)
            something_was_done = True

        if len(self.action_path) >= 1:
            self._log.debug(f"{agent.name}: Action path set. Executing one.")
            self.action_path = self.plan_execution(agent, krm, self.action_path)
            if not self.action_path:
                self._log.debug(f"{agent.name}: Action path execution finished.")
            something_was_done = True

        # only ever have to check completion here
        if self.check_completion(krm):
            self._log.debug(f"{agent.name}: Exploration completed.")
            self.completed = True

        if not something_was_done:
            logging.warning("No exploration step taken")

        return self.completed

    def check_target_available(self, krm: KRM) -> bool:
        num_targets = 0
        num_frontiers = len(krm.get_all_frontiers_idxs())
        num_targets += num_frontiers
        num_targets += len(krm.get_all_world_object_idxs())

        if num_targets < 1:
            return False
        else:
            return True

    def clear_target(self) -> None:
        self.target_node = None

    def setup_target_initialisation(
        self, krm: KRM
    ) -> tuple[Sequence[Edge], Literal[0]]:
        # Add a frontier edge self loop on the start node to ensure a exploration sampling action
        edge_id = krm.graph.add_edge(0, 0, type=EdgeType.EXPLORE_FT_EDGE)
        self._log.debug(
            f"{self.__class__.__name__}: Adding frontier edge self loop. {krm.graph.edges()}"
        )
        action_path: list[Edge] = [(0, 0, edge_id)]
        target_node: Node = 0
        return action_path, target_node

    def check_target_still_valid(self, krm: KRM, target_node: Optional[Node]) -> bool:
        if target_node is None:
            return False
        return krm.check_node_exists(target_node)

    @abstractmethod
    def target_selection(self, agent: AbstractAgent, krm: KRM) -> Node:
        pass

    @abstractmethod
    def path_generation(
        self, agent: AbstractAgent, krm: KRM, target_node: Node
    ) -> Sequence[Optional[Edge]]:
        pass

    @abstractmethod
    def plan_execution(
        self, agent: AbstractAgent, krm: KRM, action_path: Sequence[Optional[Edge]]
    ) -> Sequence[Optional[Edge]]:
        pass

    @abstractmethod
    def check_completion(self, krm: KRM) -> bool:
        pass

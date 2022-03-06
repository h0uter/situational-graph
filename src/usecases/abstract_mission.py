from abc import ABC, abstractmethod
import logging
from typing import Union

from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.utils.config import Config
from src.utils.my_types import Node, EdgeType


class AbstractMission(ABC):
    def __init__(self, cfg: Config) -> None:
        self._log = logging.getLogger(__name__)
        self.cfg = cfg
        self.exploration_completed = False
        self.action_path = list()
        self.target_node = None
        self.init_flag = False

    # CONTEXT
    def main_loop(self, agent: AbstractAgent, krm: KnowledgeRoadmap) -> bool:
        something_was_done = False

        if not self.check_target_available(krm) and not self.init_flag:
            self._log.debug(
                f"{agent.name}: No targets available. Performing initialization."
            )
            self.action_path, self.target_node = self.fix_target_initialisation(krm)
            self.init_flag = True

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

        if self.action_path:
            self._log.debug(f"{agent.name}: Action path set. Executing one.")
            self.action_path = self.path_execution(agent, krm, self.action_path)
            if not self.action_path:
                self._log.debug(f"{agent.name}: Action path execution finished.")

        # only ever have to check completion here
        if self.check_completion(krm):
            self._log.debug(f"{agent.name}: Exploration completed.")
            self.exploration_completed = True
            something_was_done = True

        if not something_was_done:
            logging.warning("No exploration step taken")

        return self.exploration_completed

    @abstractmethod
    def target_selection(self, agent: AbstractAgent, krm: KnowledgeRoadmap) -> Node:
        pass

    @abstractmethod
    def path_generation(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap, target_node: Union[str, int]
    ) -> Union[list[Node], None]:
        pass

    @abstractmethod
    def path_execution(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap, action_path: list[Node]
    ) -> Union[tuple[KnowledgeRoadmap, AbstractAgent, list[Node]], None]:
        pass

    @abstractmethod
    def check_completion(self, krm: KnowledgeRoadmap) -> bool:
        pass

    def check_target_still_valid(
        self, krm: KnowledgeRoadmap, target_node: Node
    ) -> bool:
        return krm.check_node_exists(target_node)

    def check_target_available(self, krm: KnowledgeRoadmap) -> bool:
        num_targets = 0
        num_frontiers = len(krm.get_all_frontiers_idxs())
        num_targets += num_frontiers
        # TODO: also add other targets

        if num_targets < 1:
            return False
        else:
            return True

    def fix_target_initialisation(self, krm: KnowledgeRoadmap) -> tuple:
        # Add a frontier edge self loop on the start node to ensure a exploration sampling action
        krm.graph.add_edge(0, 0, type=EdgeType.FRONTIER_EDGE)
        action_path = [0, 0]
        return action_path, 0

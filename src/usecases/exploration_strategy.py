from abc import ABC, abstractmethod
import logging
from typing import Union

from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.utils.config import Config
from src.utils.my_types import Node


class ExplorationStrategy(ABC):

    target_node = None
    action_path = list()

    def __init__(self, cfg: Config) -> None:
        self._logger = logging.getLogger(__name__)
        self.cfg = cfg
        self.exploration_completed = False

    # CONTEXT
    def run_exploration_step(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap
    ) -> tuple[AbstractAgent, KnowledgeRoadmap]:

        if not self.target_node:
            self._logger.debug(f"{agent.name}: No target node set. Setting one.")
            self.target_node = self.target_selection(agent, krm)
            return agent, krm

        if not self.action_path:
            self._logger.debug(f"{agent.name}: No action path set. Setting one.")
            self.action_path = self.path_generation(agent, krm, self.target_node)
            return agent, krm

        if self.action_path:
            self._logger.debug(f"{agent.name}: Action path set. Executing one.")
            self.action_path = self.path_execution(agent, krm, self.action_path)
            if not self.action_path:
                self._logger.debug(f"{agent.name}: Action path execution finished.")
                self.target_node = None
                self.action_path = None
                self.exploration_completed = self.check_completion(krm)

            return agent, krm

        logging.warning("No exploration step taken")
        return agent, krm

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

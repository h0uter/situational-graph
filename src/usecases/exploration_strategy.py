from abc import ABC, abstractmethod
import logging
from typing import Union

from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.utils.config import Config
from src.utils.my_types import Node


class ExplorationStrategy(ABC):


    def __init__(self, cfg: Config) -> None:
        self._log = logging.getLogger(__name__)
        self.cfg = cfg
        self.exploration_completed = False
        self.action_path = list()
        self.target_node = None

    # CONTEXT
    def run_exploration_step(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap
    ) -> tuple[AbstractAgent, KnowledgeRoadmap]:
        something_was_done = False

        if not self.target_node:
            self._log.debug(f"{agent.name}: No target node set. Setting one.")
            self.target_node = self.target_selection(agent, krm)
            # return agent, krm
            something_was_done = True

        if not self.action_path:
            self._log.debug(f"{agent.name}: No action path set. Setting one.")
            self.action_path = self.path_generation(agent, krm, self.target_node)
            something_was_done = True
            # return agent, krm

        if self.action_path:

            self._log.debug(f"{agent.name}: Action path set. Executing one.")
            self.action_path = self.path_execution(agent, krm, self.action_path)
            if not self.action_path:
                self._log.debug(f"{agent.name}: Action path execution finished.")
                self.target_node = None
                self.action_path = None
                self.exploration_completed = self.check_completion(krm)  # only ever have to check completion here
            something_was_done = True

            # return agent, krm

        if not something_was_done:
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

    @abstractmethod
    def check_target_still_valid(self, krm: KnowledgeRoadmap, target_node: Node) -> bool:
        pass

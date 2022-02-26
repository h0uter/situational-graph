from abc import ABC, abstractmethod
import logging
from typing import Union

from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap

Node = Union[str, int]


class ExplorationStrategy(ABC):

    target_node = None
    action_path = list()

    # CONTEXT
    def run_exploration_step(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap
    ) -> tuple[AbstractAgent, KnowledgeRoadmap]:

        if not self.target_node:
            self.target_node = self.target_selection(agent, krm)
            return agent, krm

        if not self.action_path:
            self.action_path = self.path_generation(agent, krm, self.target_node)
            return agent, krm

        if self.action_path:
            self.action_path = self.path_execution(agent, krm, self.action_path)
            if not self.action_path:
                self.target_node = None

            return agent, krm

        logging.warning("No exploration step taken")
        return agent, krm

    @abstractmethod
    def target_selection(self, agent: AbstractAgent, krm: KnowledgeRoadmap) -> Node:
        pass

    @abstractmethod
    def path_generation(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap, target_node: Union[str, int]
    ) -> list[Node]:
        pass

    @abstractmethod
    def path_execution(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap, action_path: list[Node]
    ) -> Union[tuple[KnowledgeRoadmap, AbstractAgent, list[Node]], None]:
        pass

        # if action_node == "waypoint":

        # elif action_node == "frontier":

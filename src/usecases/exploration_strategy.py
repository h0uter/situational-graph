from abc import ABC, abstractmethod

from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap


class ExplorationStrategy(ABC):
    # CONTEXT
    @abstractmethod
    def run_exploration_step(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap
    ) -> tuple[KnowledgeRoadmap, AbstractAgent]:
        return krm, agent

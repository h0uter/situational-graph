from abc import ABC, abstractmethod
from src.entities.abstract_agent import AbstractAgent

from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.local_grid import LocalGrid
from src.utils.config import Config


class AbstractVizualisation(ABC):

    @abstractmethod
    def __init__(self, cfg: Config) -> None:
        pass

    @abstractmethod
    def figure_update(self, krm: KnowledgeRoadmap, agent: AbstractAgent, lg: LocalGrid) -> None:
        pass

from abc import ABC, abstractmethod
from typing import Union, Sequence
from src.entities.abstract_agent import AbstractAgent

from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.local_grid import LocalGrid
from src.utils.config import Config


class AbstractVizualisation(ABC):
    @abstractmethod
    def __init__(self, cfg: Config) -> None:
        pass

    @abstractmethod
    def figure_update(
        self, krm: KnowledgeRoadmap, agents: Sequence[AbstractAgent], lg: Union[None, LocalGrid]
    ) -> None:
        pass

    @abstractmethod
    def figure_final_result(
        self, krm: KnowledgeRoadmap, agents: Sequence[AbstractAgent], lg: Union[None, LocalGrid]
    ):
        pass

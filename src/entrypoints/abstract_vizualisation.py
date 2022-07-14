from abc import ABC, abstractmethod
from typing import Union, Sequence

from src.domain.services.abstract_agent import AbstractAgent
from src.domain.services.tosg import TOSG
from src.domain.services.planner import Planner

# from src.usecases.exploration_usecase import ExplorationUsecase
from src.domain.entities.local_grid import LocalGrid
from src.configuration.config import Config


class AbstractVizualisation(ABC):
    @abstractmethod
    def __init__(self, cfg: Config) -> None:
        pass

    @abstractmethod
    def figure_update(
        self,
        krm: TOSG,
        agents: Sequence[AbstractAgent],
        lg: Union[None, LocalGrid],
        usecases: Sequence[Planner],
    ) -> None:
        pass

    @abstractmethod
    def figure_final_result(
        self, krm: TOSG, agents: Sequence[AbstractAgent], lg: Union[None, LocalGrid]
    ):
        pass

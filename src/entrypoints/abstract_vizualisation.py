from abc import ABC, abstractmethod
from typing import Union, Sequence

from src.data_providers.abstract_agent import AbstractAgent
from src.usecases.tosg import TOSG
from src.usecases.planner import Planner

# from src.usecases.exploration_usecase import ExplorationUsecase
from src.entities.dynamic_data.local_grid import LocalGrid
from src.utils.config import Config


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

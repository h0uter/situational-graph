from abc import ABC, abstractmethod
from typing import Union, Sequence

from src.platform.abstract_agent import AbstractAgent
from src.planning.tosg import TOSG
from src.planning.offline_planner import OfflinePlanner

# from src.usecases.exploration_usecase import ExplorationUsecase
from src.perception_processing.local_grid import LocalGrid


class AbstractVizualisation(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def figure_update(
        self,
        krm: TOSG,
        agents: Sequence[AbstractAgent],
        lg: Union[None, LocalGrid],
        usecases: Sequence[OfflinePlanner],
    ) -> None:
        pass

    @abstractmethod
    def figure_final_result(
        self, krm: TOSG, agents: Sequence[AbstractAgent], lg: Union[None, LocalGrid]
    ):
        pass

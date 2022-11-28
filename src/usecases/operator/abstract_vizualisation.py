from abc import ABC, abstractmethod
from typing import Sequence, Union

# from src.usecases.exploration_usecase import ExplorationUsecase
from src.platform_state.local_grid import LocalGrid
from src.mission_autonomy.offline_planner import OfflinePlanner
from src.platform_control.abstract_agent import AbstractAgent
from src.mission_autonomy.situational_graph import SituationalGraph


class AbstractVizualisation(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def figure_update(
        self,
        krm: SituationalGraph,
        agents: Sequence[AbstractAgent],
        lg: Union[None, LocalGrid],
        usecases: Sequence[OfflinePlanner],
    ) -> None:
        pass

    @abstractmethod
    def figure_final_result(
        self, krm: SituationalGraph, agents: Sequence[AbstractAgent], lg: Union[None, LocalGrid]
    ):
        pass

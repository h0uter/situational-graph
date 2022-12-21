from abc import ABC, abstractmethod

from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.shared.situational_graph import SituationalGraph


class MissionInitializer(ABC):
    @abstractmethod
    def initialize_mission(self, agents: list[AbstractAgent], situational_graph: SituationalGraph):
        pass

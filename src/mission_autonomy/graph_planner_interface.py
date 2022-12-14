import logging
from abc import ABC, abstractmethod

from src.mission_autonomy.situational_graph import SituationalGraph
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.shared.plan_model import PlanModel
from src.shared.task import Task
from src.shared.types.node_and_edge import Node


class GraphPlannerInterface(ABC):
    def __init__(self):
        self._log = logging.getLogger(__name__)

    @abstractmethod
    def find_plan_for_task(
        self,
        agent_localized_to: Node,
        full_tosg: SituationalGraph,
        task: Task,
        filtered_tosg: SituationalGraph,
    ) -> PlanModel:
        pass

    @staticmethod
    @abstractmethod
    def _filter_graph(tosg: SituationalGraph, capabilities: set) -> SituationalGraph:
        pass

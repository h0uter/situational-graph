import logging
from abc import ABC, abstractmethod

from src.shared.situational_graph import SituationalGraph
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

    #TODO: remove this abstract method, it should not be part of the interface.
    @staticmethod
    @abstractmethod
    def _filter_graph(tosg: SituationalGraph, capabilities: set) -> SituationalGraph:
        pass

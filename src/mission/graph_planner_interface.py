import logging
from abc import ABC, abstractmethod

from src.mission.situational_graph import SituationalGraph
from src.platform.execution.plan_model import PlanModel
from src.platform.control.abstract_agent import AbstractAgent
from src.shared.types.node_and_edge import Node
from src.shared.task import Task


class GraphPlannerInterface(ABC):
    def __init__(self):
        self._log = logging.getLogger(__name__)

    @abstractmethod
    def _find_plan_for_task(
        self,
        agent_localized_to: Node,
        full_tosg: SituationalGraph,
        task: Task,
        filtered_tosg: SituationalGraph,
    ) -> PlanModel:
        pass

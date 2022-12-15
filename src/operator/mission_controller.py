
from src.core import event_system
from src.core.topics import Topics
from src.shared.prior_knowledge.objectives import Objectives
from src.shared.task import Task
from src.shared.types.node_and_edge import Node, Edge


class MissionController:
    def add_task_to_queue(self, node: Node):

        # BUG: real spot only navigates to the start of the edge, not the end

        edge: Edge = (None, node, None)  # HACK: this should be a proper edge
        task = Task(edge, Objectives.VISIT_ALL_HOTSPOTS)
        
        event_system.post_event(Topics.OPERATOR_TASK, task)
        
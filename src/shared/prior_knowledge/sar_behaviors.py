from enum import Enum
from typing import Optional

from src.shared.prior_knowledge.sar_capabilities import Capabilities


class Behaviors(Enum):
    GOTO = (set(), 1, "Go to a waypoint.")
    EXPLORE = (set(), 1, "Go to a place and sample new frontiers.")
    ASSESS = ({Capabilities.CAN_ASSESS}, 2, "Assess a victim.")

    # OPEN_DOOR = auto()
    # GUIDE_WP_EDGE = auto()

    def __init__(
        self,
        required_capabilities: set[Optional[Capabilities]],
        cost: float,
        description: str,
    ):
        self.required_capabilities = required_capabilities
        self.cost = cost
        self.description = description

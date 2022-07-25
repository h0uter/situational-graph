from enum import Enum

from src.domain.entities.capabilities import Capabilities

# TODO: add capabilities here.
# TODO: make BaseBehaviors class to inherit from for specific domains
class Behaviors(Enum):
    GOTO = (set(), 1, "Go to a waypoint.")
    EXPLORE = (set(), 1, "Go to a place and sample new frontiers.")
    ASSESS = ({Capabilities.CAN_ASSESS}, 2, "Assess a victim.")

    # GOTO = auto()
    # EXPLORE = auto()
    # ASSESS = auto()
    # OPEN_DOOR = auto()
    # PLAN_EXTRACTION_WO_EDGE = auto()
    # GUIDE_WP_EDGE = auto()

    def __init__(self, required_capabilities: set[Capabilities], cost: float, description: str):
        self.required_capabilities = required_capabilities
        self.cost = cost
        self.description = description
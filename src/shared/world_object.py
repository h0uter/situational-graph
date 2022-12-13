from dataclasses import dataclass
from src.shared.prior_knowledge.situations import Situations


@dataclass
class WorldObject:
    pos: tuple
    object_type: Situations

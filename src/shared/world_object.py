from dataclasses import dataclass
from src.shared.situations import Situations


@dataclass
class WorldObject:
    pos: tuple
    object_type: Situations
    # self.id: int = None

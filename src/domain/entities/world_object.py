from dataclasses import dataclass
from src.domain.entities.object_types import Situations


@dataclass
class WorldObject:
    pos: tuple
    object_type: Situations
    # self.id: int = None

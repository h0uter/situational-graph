
from dataclasses import dataclass
from src.domain.entities.object_types import ObjectTypes


@dataclass
class WorldObject:
    pos: tuple
    object_type: ObjectTypes
    # self.id: int = None

from enum import Enum, auto
from uuid import uuid4


class Objective(Enum):
    EXPLORE_ALL_FTS = (10, "Explore every frontier")
    ASSES_ALL_VICTIMS = (100, "Asses every encountered victim")
    VISIT_ALL_HOTSPOTS = (1000, "visit a hotspot node")
    OPEN_ALL_DOORS = (10, "Open all doors")

    def __init__(self, reward, description):
        self.reward = reward
        self.description = description

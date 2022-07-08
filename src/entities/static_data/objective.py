from enum import Enum, auto
from uuid import uuid4


class Objective(Enum):
    EXPLORE = (10, "Explore every frontier")
    ASSES = (100, "Asses every encountered victim")

    def __init__(self, reward, description):
        self.reward = reward
        self.description = description

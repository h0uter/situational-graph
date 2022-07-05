from enum import Enum
from uuid import uuid4


class Objective:
    def __init__(self, name: Enum, reward):
        self.id = uuid4()
        self.name = name
        self.reward = reward

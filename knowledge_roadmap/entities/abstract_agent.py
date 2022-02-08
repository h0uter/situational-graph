from abc import ABC, abstractmethod

class AbstractAgent(ABC):

    def __init__(self, start_pos:tuple) -> None:
        # TODO: remove as much as possible
        self.at_wp = 0
        self.pos = start_pos
        self.previous_pos = self.pos

        # FIXME: this should not be in the agent
        self.no_more_frontiers = False
        # FIXME: this should not be in the agent
        self.steps_taken = 0

    @abstractmethod
    def move_to_pos(self, pos:tuple) -> None:
        '''
        Move the agent to a new position.
        
        :param pos: the position of the agent
        :return: None
        '''
        pass

    @abstractmethod
    def get_localization(self) -> tuple:
        pass
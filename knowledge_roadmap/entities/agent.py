from knowledge_roadmap.entities.abstract_agent import AbstractAgent

class Agent(AbstractAgent):
    ''' 
    The goal of this method is to
    - provide a simulated agent
    '''

    # def __init__(self, start_pos:tuple, debug=False) -> None:
    #     # TODO: remove as much as possible
    #     self.at_wp = 0
    #     self.pos = start_pos
    #     self.previous_pos = self.pos
    #     # self.debug = debug
    #     # self.agent_drawing = None
    #     # self.local_grid_drawing = None
    #     # FIXME: this should not be in the agent
    #     self.no_more_frontiers = False
    #     # FIXME: this should not be in the agent
    #     self.steps_taken = 0

    def teleport_to_pos(self, pos:tuple) -> None:
        '''
        Teleport the agent to a new position.
        
        :param pos: the position of the agent
        :return: None
        '''
        # TODO: add a check to see if the position is within the navigation radius.
        self.previous_pos = self.pos
        self.pos = pos
        self.steps_taken += 1
    
    def move_to_pos(self, pos:tuple) -> None:
        self.teleport_to_pos(pos)

    def get_localization(self) -> tuple:
        return self.pos

        



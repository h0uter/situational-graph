

class Agent():
    ''' 
    The goal of this method is to
    - be an adapter for sending commands to the spot robot.
    '''

    def __init__(self, start_pos:tuple, debug=False) -> None:
        self.debug = debug
        self.at_wp = 0
        self.pos = start_pos
        self.previous_pos = self.pos
        self.agent_drawing = None
        self.local_grid_drawing = None
        self.no_more_frontiers = False
        self.steps_taken = 0

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
        '''
        Move the agent to a new position.
        
        :param pos: the position of the agent
        :return: None
        '''

        print(f"im moving to {pos}")
        


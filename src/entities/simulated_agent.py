from src.entities.abstract_agent import AbstractAgent

class SimulatedAgent(AbstractAgent):
    ''' 
    The goal of this method is to
    - provide a simulated agent
    '''

    def __init__(self, start_pos:tuple[float,float]) -> None:
        super().__init__(start_pos)


    def teleport_to_pos(self, pos:tuple[float,float]) -> None:
        '''
        Teleport the agent to a new position.
        
        :param pos: the position of the agent
        :return: None
        '''
        # TODO: add a check to see if the position is within the navigation radius.
        self.previous_pos = self.pos
        self.pos = pos
        self.steps_taken += 1
    
    def move_to_pos(self, pos:tuple[float, float]) -> None:
        self.teleport_to_pos(pos)

    def get_localization(self) -> tuple:
        return self.pos

    def get_local_grid_img(self) -> list[list]:
        pass

        



# import all the boston shite

from knowledge_roadmap.entities.agent import Agent

class SpotRobot(Agent):

    def __init__(self, debug=False, start_pos=None):
        super().__init__(debug=debug, start_pos=start_pos)

    def move_to_pos(self, pos):
        pass
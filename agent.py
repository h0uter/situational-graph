import matplotlib.pyplot as plt

from knowledge_road_map import KnowledgeRoadmap

class Agent():
    # only here to test the framework
    def __init__(self):
        self.at_wp = 10
        # self.pos = (-5,-5)
        self.agent_drawing = None
        self.krm = KnowledgeRoadmap((0,0))
    
    def teleport_to_wp(self, goal_wp):
        ''' teleport to goal_wp '''
        self.at_wp = goal_wp

    def draw_agent(self, wp):
        ''' draw the agent on the world '''
        if self.agent_drawing != None:
            self.agent_drawing.remove()
        self.agent_drawing = plt.arrow(wp[0], wp[1], 0.3, 0.3, width=0.3,color='blue')
    
    def use_sensors(self, world):
        '''
        use sensors to find the frontier nodes
        '''
        local_grid = world.get_local_grid(self.at_wp)
        return local_grid


    def sample_frontiers(self, local_grid):
        ''' sample new frontiers from local_grid '''
        # HACK:: check if nodes not already in KRM
        new_frontier_nodes = [
            node for node in local_grid if node not in self.krm.KRM.nodes]
        return new_frontier_nodes

        

    def select_target_frontier(self ):
        pass

    def goto_target_frontier(self, target):
        pass

    def sample_waypoint(self):
        '''
        sample a new waypoint from the pose graph of the agent.
        '''
        # HACK:: turn a visited frontier node into a waypoint
        pass






    #TODO: create a function which explores a GraphWorld and returns a list of frontier node
    # how to ensure that the agent only has acces to the observed part of the world?
    def explore(self, world):

        local_grid = self.use_sensors(world)

        new_frontiers = self.sample_frontiers(local_grid)

        print(new_frontiers)

        # # action selection
        # self.select_target_frontier()

        # self.goto_target_frontier()

        # self.sample_waypoint()

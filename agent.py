import matplotlib.pyplot as plt

from knowledge_road_map import KnowledgeRoadmap


class Agent():
    ''' Agent only here to test the KRM framework im developping'''
    def __init__(self):
        self.at_wp = 13
        # self.pos = (-5,-5)
        self.agent_drawing = None
        self.krm = KnowledgeRoadmap((0, 0))

    def teleport_to_wp(self, goal_wp):
        ''' teleport to goal_wp '''
        self.at_wp = goal_wp

    def draw_agent(self, wp):
        ''' draw the agent on the world '''
        if self.agent_drawing != None:
            self.agent_drawing.remove()
        self.agent_drawing = plt.arrow(
            wp[0], wp[1], 0.3, 0.3, width=0.3, color='blue')

    def get_local_grid(self, world):
        '''
        process sensor to obtain the local grid
        '''
        observation = world.observe(self.at_wp)
        # HACK:: we directly observe all neighbors of the current node
        local_grid = observation

        return local_grid

    # TODO:: write a test for the sample frontiers function with a networkx demo graph
    def sample_frontiers(self, local_grid):
        ''' sample new frontiers from local_grid '''
        # HACK:: check if nodes not already in KRM
        new_frontier_nodes = [
            node for node in local_grid if node not in self.krm.KRM.nodes]
        # TODO:: krm.KRM is ugly

        return new_frontier_nodes

    def select_target_frontier(self):
        ''' using the KRM, obtain the optimal frontier to visit next'''
        pass

    def goto_target_frontier(self, target):
        '''perform the move actions to reach the target frontier'''
        pass

    def sample_waypoint(self):
        '''
        sample a new waypoint from the pose graph of the agent.
        '''
        # HACK:: turn a visited frontier node into a waypoint
        pass

    def explore(self, world):
        # TODO:: complete the exploration behaviour

        local_grid = self.get_local_grid(world)

        new_frontiers = self.sample_frontiers(local_grid)
        print(new_frontiers)

        # add the new frontiers to the KRM

        # # action selection
        # self.select_target_frontier()

        # self.goto_target_frontier()

        # self.sample_waypoint()

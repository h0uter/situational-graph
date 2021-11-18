import matplotlib.pyplot as plt

from knowledge_road_map import KnowledgeRoadmap


class Agent():
    ''' Agent only here to test the KRM framework im developping'''
    def __init__(self):
        self.at_wp = 0
        self.pos = (0, 0)
        self.agent_drawing = None
        self.krm = KnowledgeRoadmap((0, 0))
        self.no_more_frontiers = False

    def teleport_to_wp(self, goal_wp):
        ''' teleport to goal_wp '''
        self.at_wp = goal_wp

    def teleport_to_pos(self, pos):
        self.pos = pos

    def draw_agent(self, wp):
        ''' draw the agent on the world '''
        if self.agent_drawing != None:
            self.agent_drawing.remove()
        self.agent_drawing = plt.arrow(
            wp[0], wp[1], 0.3, 0.3, width=0.3, color='blue')

    # TODO:: write a test for the sample frontiers function with a networkx demo graph
    def sample_frontiers(self, world):
        ''' sample new frontiers from local_grid '''
        # HACK:: check if nodes not already in KRM

        observable_nodes = world.world.neighbors(self.at_wp)
        frontier_counter = 0

        for node in observable_nodes:
            if node not in self.krm.KRM.nodes:
                print(node)
                print(world.world._node[node]['pos'])
                frontier_pos = world.world._node[node]['pos']
                self.krm.add_frontier(frontier_pos)
                frontier_counter += 1

        if frontier_counter == 0:
            self.no_more_frontiers = True

    def select_target_frontier(self):
        ''' using the KRM, obtain the optimal frontier to visit next'''
        frontiers = self.krm.get_all_frontiers()
        # HACK: just pick first frontier
        selected_frontier = frontiers[0]
        return selected_frontier
        # pass

    def goto_target_frontier(self, target):
        '''perform the move actions to reach the target frontier'''
        
        pass

    def sample_waypoint(self):
        '''
        sample a new waypoint from the pose graph of the agent.
        '''
        # HACK:: turn a visited frontier node into a waypoint
        self.at_wp = self.krm.add_waypoint(self.pos)
        # pass

    def explore(self, world):
        # TODO:: complete the exploration behaviour

        self.krm.draw_current_krm()

        # I want to get the position of all the candidate frontiers so that I can
        # add them to my KRM as frontier nodes.
        # this position should be in the node dictionary I obtain from the world.
        # however what I actually have are the idx of the node, not the complete dictionary

        while self.no_more_frontiers == False:
            self.sample_frontiers(world)
            self.krm.draw_current_krm()
            selected_frontier = self.select_target_frontier()
            self.teleport_to_pos(selected_frontier['pos'])
            self.sample_waypoint()



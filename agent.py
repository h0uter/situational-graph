import matplotlib.pyplot as plt

from knowledge_road_map import KnowledgeRoadmap

import keyboard
import time

class Agent():
    ''' Agent only here to test the KRM framework im developping'''
    def __init__(self):
        self.at_wp = 0
        self.pos = (0, 0)
        self.previous_pos = self.pos
        self.agent_drawing = None
        self.krm = KnowledgeRoadmap((0, 0))
        self.no_more_frontiers = False
        self.keypress = None


    def teleport_to_pos(self, pos):
        self.previous_pos = self.pos
        self.pos = pos

    # TODO:: write a test for the sample frontiers function with a networkx demo graph
    def sample_frontiers(self, world):
        ''' sample new frontiers from local_grid '''
        # observable_nodes = world.world.neighbors(self.at_wp)
        observable_nodes = world.world[self.at_wp] # indexing the graph like this returns the neigbors

        # these are in wp idx
        for node in observable_nodes:
            if node not in self.krm.KRM.nodes:
                frontier_pos = world.world._node[node]['pos']
                self.krm.add_frontier(frontier_pos, self.at_wp)

    def select_target_frontier(self):
        ''' using the KRM, obtain the optimal frontier to visit next'''
        frontiers = self.krm.get_all_frontiers()
        print(f"len frontiers {len(frontiers)}")
        if len(frontiers) > 0:
        # HACK: just pick first frontier. this is where the interesting logic comes in.
            target_frontier = frontiers[0]
            return target_frontier
        else:
            self.no_more_frontiers = True
            return 

    def goto_target_frontier(self, target):
        '''perform the move actions to reach the target frontier'''
        pass

    def sample_waypoint(self):
        '''
        sample a new waypoint from the pose graph of the agent and remove the current frontier.
        '''
        wp_at_previous_pos = self.krm.get_node_by_pos(self.previous_pos)
        self.krm.add_waypoint(self.pos, wp_at_previous_pos)
        self.at_wp = self.krm.get_node_by_pos(self.pos)

    def explore(self, world):
        ''' explore the world by sampling new frontiers and waypoints '''

        while self.no_more_frontiers == False:
            self.keypress = keyboard.read_key()
            if self.keypress:
                self.keypress = None
                self.sample_frontiers(world)
                self.krm.draw_current_krm()
                selected_frontier = self.select_target_frontier()
                if self.no_more_frontiers == True:
                    break
                self.teleport_to_pos(selected_frontier['pos'])
                self.krm.remove_frontier(selected_frontier)
                self.sample_waypoint()
            # time.sleep(0.1)

            
        self.krm.draw_current_krm()

    def draw_agent(self, wp):
        ''' draw the agent on the world '''
        if self.agent_drawing != None:
            self.agent_drawing.remove()
        self.agent_drawing = plt.arrow(
            wp[0], wp[1], 0.3, 0.3, width=0.3, color='blue')

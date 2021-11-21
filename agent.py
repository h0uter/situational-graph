import matplotlib.pyplot as plt

from knowledge_road_map import KnowledgeRoadmap

class Agent():
    ''' Agent only here to test the KRM framework im developping'''
    def __init__(self):
        self.at_wp = 0
        self.previous_at_wp = self.at_wp
        self.pos = (0, 0)
        self.previous_pos = self.pos
        self.agent_drawing = None
        self.krm = KnowledgeRoadmap((0, 0))
        self.no_more_frontiers = False
        self.wp_idx = 0

    def teleport_to_wp(self, goal_wp):
        ''' teleport to goal_wp '''
        self.previous_at_wp = self.at_wp
        self.at_wp = goal_wp

    def teleport_to_pos(self, pos):
        # self.previous_at_wp = self.at_wp
        self.previous_pos = self.pos
        self.pos = pos
        self.wp_idx += 1

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

        # observable_nodes = world.world.neighbors(self.at_wp)
        print(f"self.at_wp: {self.at_wp}")
        # BUG:: this no longer syncs to the world.world. graph
        # observable_nodes = world.world[self.at_wp]
        observable_nodes = world.world[self.at_wp]
        frontier_counter = 0
        print(f"len observable nodes {observable_nodes}")

        # these are in wp idx
        for node in observable_nodes:
            if node not in self.krm.KRM.nodes:
                # print(node)
                # print(world.world._node[node]['pos'])
                frontier_pos = world.world._node[node]['pos']
                # print(f"frontierpos {frontier_pos}")

                self.krm.add_frontier(frontier_pos, self.at_wp)
                frontier_counter += 1

        if frontier_counter == 0:
            self.no_more_frontiers = True

    def select_target_frontier(self):
        ''' using the KRM, obtain the optimal frontier to visit next'''
        frontiers = self.krm.get_all_frontiers()
        print(f"len frontiers {len(frontiers)}")
        if len(frontiers) > 0:
        # HACK: just pick first frontier
            target_frontier = frontiers[0]
            return target_frontier
        else:
            self.no_more_frontiers = True
            return 
        # pass

    def goto_target_frontier(self, target):
        '''perform the move actions to reach the target frontier'''
        
        pass

    def sample_waypoint(self):
        '''
        sample a new waypoint from the pose graph of the agent and remove the current frontier.
        '''
        # HACK:: turn a visited frontier node into a waypoint
        # HACK:: need to decided between passing idx and the complete node dictionary
        # print("target_frontier: ",target_frontier) 
        # target_frontier is a dictionary;
        # how to obtain the key that matches this dictionary?

        # target = self.krm.get_node_by_pos(target_frontier['pos'])

        # HACK:: at_wp needs to me updated in the move function
        wp_at_previous_pos = self.krm.get_node_by_pos(self.previous_pos)
        print(f"wp_at_previous_pos: {wp_at_previous_pos}")

        self.at_wp = self.krm.add_waypoint(self.pos, wp_at_previous_pos)
        # self.wp_idx += 1
        # pass

    def explore(self, world):
        # TODO:: complete the exploration behaviour

        # self.krm.draw_current_krm()

        # I want to get the position of all the candidate frontiers so that I can
        # add them to my KRM as frontier nodes.
        # this position should be in the node dictionary I obtain from the world.
        # however what I actually have are the idx of the node, not the complete dictionary

        while self.no_more_frontiers == False:
            self.sample_frontiers(world)
            # self.krm.draw_current_krm()
            self.krm.draw_KRM_from_skratch()
            selected_frontier = self.select_target_frontier()
            if self.no_more_frontiers == True:
                break
            self.teleport_to_pos(selected_frontier['pos'])
            self.krm.remove_frontier(selected_frontier)
            self.sample_waypoint()


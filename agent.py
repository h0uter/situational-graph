import matplotlib.pyplot as plt
import numpy as np
from knowledge_road_map import KnowledgeRoadmap
import networkx as nx
import keyboard

class Agent():
    ''' Agent only here to test the KRM framework im developping'''
    def __init__(self):
        self.at_wp = 0
        self.pos = (0, 0)
        self.previous_pos = self.pos
        self.agent_drawing = None
        self.krm = KnowledgeRoadmap((0, 0))
        self.no_more_frontiers = False
        # self.keypress = None

    def teleport_to_pos(self, pos):
        self.previous_pos = self.pos
        self.pos = pos

    # TODO:: write a test for the sample frontiers function with a networkx demo graph
    def sample_frontiers(self, world):
        ''' sample new frontiers from local_grid '''
        agent_at_world_node = world.get_node_by_pos(self.pos)
        observable_nodes = world.world[agent_at_world_node] # indexing the graph like this returns the neigbors
        world_node_pos_dict = nx.get_node_attributes(world.world, 'pos')

        for node in observable_nodes:
            obs_pos = world_node_pos_dict[node]
            krm_node_pos_dict = nx.get_node_attributes(self.krm.KRM, 'pos')
            # check if the there is already a node in my KRM with the same position as the observable node
            if obs_pos not in krm_node_pos_dict.values():
                # frontier_pos = world.world._node[node]['pos']
                frontier_pos = obs_pos
                self.krm.add_frontier(frontier_pos, self.at_wp)

    def select_target_frontier(self):
        ''' using the KRM, obtain the optimal frontier to visit next'''
        frontiers = self.krm.get_all_frontiers()
        if len(frontiers) > 0:
            # HACK: just pick a random frontier. this is where the interesting logic comes in.
            idx = np.random.randint(0, len(frontiers))
            target_frontier = frontiers[idx]
            return target_frontier
        else:
            self.no_more_frontiers = True
            return 

    def goto_target_frontier(self, target):
        '''perform the move actions to reach the target frontier'''
        pass

    def sample_for_shortcuts(self):
        ''' check if we can add edges which create a shortcut for existing waypoints'''
        pass

    def sample_waypoint(self):
        '''
        sample a new waypoint from the pose graph of the agent and remove the current frontier.
        '''
        wp_at_previous_pos = self.krm.get_node_by_pos(self.previous_pos)
        # TODO: add a check if the proposed new wp is not already in the KRM
        self.krm.add_waypoint(self.pos, wp_at_previous_pos)
        self.at_wp = self.krm.get_node_by_pos(self.pos)

    def explore_algo(self, world):
        '''the logic powering exploration'''
        # HACK:: the whole logic of this function is one big hack
        self.sample_frontiers(world)  # sample frontiers from the world
        self.krm.draw_current_krm()  # illustrate krm with new frontiers
        self.draw_agent(self.pos)  # draw the agent on the world
        plt.pause(0.2)
        selected_frontier = self.select_target_frontier()  # select a frontier to visit
        if self.no_more_frontiers == True:  # if there are no more frontiers, we are done
            print("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
            return

        # TODO:: hide this logic somewhere appropriate
        # obtain the idx from the frontier object using its id
        selected_frontier_idx = self.krm.get_node_by_UUID(
            selected_frontier["id"])

        # a frontier only has 1 wp as neighbor, so we ask for that neigbor
        closest_wp_to_selected_frontier_idx = list(
            nx.neighbors(self.krm.KRM, selected_frontier_idx))[0]
        closest_wp_to_selected_frontier = self.krm.get_node_by_idx(
            closest_wp_to_selected_frontier_idx)

        if closest_wp_to_selected_frontier['pos'] != self.pos:
            # if the pos of the closest wp to our frontier is not our agent pos, we need to move to it
            self.teleport_to_pos(
                closest_wp_to_selected_frontier["pos"])
        self.teleport_to_pos(selected_frontier['pos'])
        self.krm.remove_frontier(selected_frontier)
        self.sample_waypoint()
        self.debug_logger()

    def explore(self, world):
        ''' explore the world by sampling new frontiers and waypoints '''

        while self.no_more_frontiers == False:
            self.explore_algo(world)

        self.krm.draw_current_krm()

    def explore_stepwise(self, world):
        ''' explore the world one step for each key press'''
        while self.no_more_frontiers == False:
            # BUG:: matplotlib crashes after 10 sec if we block the execution like this.
            self.keypress = keyboard.read_key()
            if self.keypress:
                self.keypress = False
                self.explore_algo(world)

        self.krm.draw_current_krm()

    def draw_agent(self, wp):
        ''' draw the agent on the world '''
        if self.agent_drawing != None:
            self.agent_drawing.remove()
        self.agent_drawing = plt.arrow(
            wp[0], wp[1], 0.3, 0.3, width=0.4, color='blue')
        plt.draw()
        # plt.pause(0.1)


    def debug_logger(self):
        print("==============================")
        print(">>> " + nx.info(self.krm.KRM))
        print(f">>> self.at_wp: {self.at_wp}")
        print(f">>> movement: {self.previous_pos} >>>>>> {self.pos}")
        print(f">>> frontiers: {self.krm.get_all_frontiers()}")
        print("==============================")

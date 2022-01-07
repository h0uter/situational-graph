import matplotlib.pyplot as plt
import numpy as np
from numpy.core.numeric import Inf, Infinity
from src.entities.knowledge_road_map import KnowledgeRoadmap
import networkx as nx
import keyboard


class Agent():
    ''' 
    Agent only here to test the KRM framework im developping.
    Feature wise it should match the out of the box capabilities of Spot.
    '''

    def __init__(self, debug=False):
        self.debug = debug
        self.at_wp = 0
        self.pos = (0, 0)
        self.previous_pos = self.pos
        self.agent_drawing = None
        self.local_grid_drawing = None
        self.krm = KnowledgeRoadmap()
        self.no_more_frontiers = False
        self.steps_taken = 0

    def debug_logger(self):
        print("==============================")
        print(">>> " + nx.info(self.krm.KRM))
        print(f">>> self.at_wp: {self.at_wp}")
        print(f">>> movement: {self.previous_pos} >>>>>> {self.pos}")
        print(f">>> frontiers: {self.krm.get_all_frontiers_idxs()}")
        print("==============================")

    # TODO: this shouldnt be in the agent but in a GUI
    def draw_agent(self, wp):
        ''' draw the agent on the world '''
        if self.agent_drawing != None:
            self.agent_drawing.remove()
        if self.local_grid_drawing != None:
            self.local_grid_drawing.remove()
        # self.agent_drawing = plt.arrow(
        #     wp[0], wp[1], 0.3, 0.3, width=0.4, color='blue') # One day the agent will have direction
        self.agent_drawing = plt.gca().add_patch(plt.Circle(
            (wp[0], wp[1]), 1.2, fc='blue'))
        
        rec_len = 10
        self.local_grid_drawing = plt.gca().add_patch(plt.Rectangle(
            (wp[0]-0.5*rec_len, wp[1]-0.5*rec_len), rec_len, rec_len, alpha=0.2, fc='blue'))

    def teleport_to_pos(self, pos):
        self.previous_pos = self.pos
        self.pos = pos
        self.steps_taken += 1

    def sample_frontiers(self, world):
        ''' sample new frontier positions from local_grid '''
        agent_at_world_node = world.get_node_by_pos(self.pos)
        # indexing the graph like this returns the neigbors
        observable_nodes = world.world[agent_at_world_node]

        # so this is godmode dictionary with pos info of all nodes
        world_node_pos_dict = nx.get_node_attributes(world.world, 'pos')

        for node in observable_nodes:
            obs_pos = world_node_pos_dict[node]
            # dict with all the pos of nodes already in krm
            krm_node_pos_dict = nx.get_node_attributes(self.krm.KRM, 'pos')

            # check if the there is not already a node in my KRM with the same position as the observable node
            if obs_pos not in krm_node_pos_dict.values():
                frontier_pos = obs_pos

                # if there is no node at that pos in the KRM, add it
                self.krm.add_frontier(frontier_pos, self.at_wp)

    #############################################################################################
    ### ENTRYPOINT FOR GUIDING EXPLORATION WITH SEMANTICS ###
    #############################################################################################
    def evaluate_frontiers(self, frontier_idxs):
        ''' Evaluate the frontiers and return the best one.
        this is the entrypoint for exploiting semantics        
        '''
        shortest_path_by_node_count = float('inf')
        selected_frontier_idx = None

        for frontier_idx in frontier_idxs:
            candidate_path = nx.shortest_path(
                self.krm.KRM, source=self.at_wp, target=frontier_idx)
            # choose the last shortest path among equals
            if len(candidate_path) <= shortest_path_by_node_count:
                # if len(candidate_path) < shortest_path_len: # choose the first shortest path among equals
                shortest_path_by_node_count = len(candidate_path)
                selected_frontier_idx = candidate_path[-1]

        return selected_frontier_idx
    #############################################################################################

    def select_target_frontier(self):
        ''' using the KRM, obtain the optimal frontier to visit next'''
        frontier_idxs = self.krm.get_all_frontiers_idxs()
        if len(frontier_idxs) > 0:
            target_frontier = self.evaluate_frontiers(frontier_idxs)

            return target_frontier
        else:
            self.no_more_frontiers = True
            return None, None

    def find_path_to_closest_wp_to_selected_frontier(self, target_frontier):
        path = nx.shortest_path(
            self.krm.KRM, source=self.at_wp, target=target_frontier)
        # HACK:: pop the last element, cause its a frontier and this is required for the wp sampling logic....
        path.pop()
        return path

    def sample_waypoint(self):
        '''
        Sample a new waypoint at current agent pos, and add an edge connecting it to prev wp.
        this should be sampled from the pose graph eventually
        '''
        wp_at_previous_pos = self.krm.get_node_by_pos(self.previous_pos)
        # TODO: add a check if the proposed new wp is not already in the KRM
        self.krm.add_waypoint(self.pos, wp_at_previous_pos)
        self.at_wp = self.krm.get_node_by_pos(self.pos)

    def execute_path(self, path, world):

        closest_wp_to_selected_frontier = self.krm.get_node_data_by_idx(
            path[-1])

        '''If the pos of the closest wp to our frontier is not our agent pos, we need to move to it'''
        if closest_wp_to_selected_frontier['pos'] != self.pos:
            for node_idx in path:
                node_data = self.krm.get_node_data_by_idx(node_idx)
                self.teleport_to_pos(node_data['pos'])
                # TODO: how to decouple drawing from movement logic?
                self.draw_agent(node_data['pos'])
                plt.show()
                plt.pause(0.05)

    def step_from_wp_to_frontier(self, selected_frontier_idx):
        selected_frontier_data = self.krm.get_node_data_by_idx(
            selected_frontier_idx)
        self.teleport_to_pos(selected_frontier_data['pos'])

    def check_for_shortcuts(self, world):
        agent_at_world_node = world.get_node_by_pos(self.pos)
        observable_nodes = world.world[agent_at_world_node]

        for world_node in observable_nodes:
            # convert observable world node to krm node
            krm_node = self.krm.get_node_by_pos(world.world.nodes[world_node]['pos'])

            if not self.krm.KRM.has_edge(krm_node, self.at_wp):
                if krm_node != self.at_wp and krm_node: # prevent self loops and None errors
                    if self.debug: print("shortcut found")
                    # add the correct type of edge
                    if self.krm.KRM.nodes[krm_node]["type"] == "frontier":
                        self.krm.KRM.add_edge(self.at_wp, krm_node, type="frontier_edge")
                    else:
                        self.krm.KRM.add_edge(self.at_wp, krm_node, type="waypoint_edge")

    # HACK: perception processing should be more eleborate
    def process_perception(self, world):
        agent_at_world_node = world.get_node_by_pos(self.pos)
        if "world_object_dummy" in world.world.nodes[agent_at_world_node].keys():
            world_object = world.world.nodes[agent_at_world_node]["world_object_dummy"]
            print(f"world object '{world_object}' found")
            wo_pos = world.world.nodes[agent_at_world_node]["world_object_pos_dummy"]
            self.krm.add_world_object(wo_pos, world_object)
        
    def explore_algo(self, world):
        '''the logic powering exploration'''

        self.sample_frontiers(world)  # sample frontiers from the world

        '''visualize the KRM'''
        self.krm.draw_current_krm()  # illustrate krm with new frontiers
        self.draw_agent(self.pos)  # draw the agent on the world
        plt.pause(0.3)

        '''select the target frontier and if there are no more frontiers remaining, we are done'''
        selected_frontier_idx = self.select_target_frontier()  # select a frontier to visit
        
        if not self.no_more_frontiers:  # if there are no more frontiers, we are done
            selected_path = self.find_path_to_closest_wp_to_selected_frontier(
                selected_frontier_idx)

            self.execute_path(selected_path, world)

            '''after reaching the wp next to the selected frontier, move to the selected frontier'''
            self.step_from_wp_to_frontier(selected_frontier_idx)

            '''now we have visited the frontier we can remove it from the KRM and sample a waypoint in its place'''
            self.krm.remove_frontier(selected_frontier_idx)
            # TODO: pruning frontiers should be independent of sampling waypoints
            self.sample_waypoint()
            self.check_for_shortcuts(world)  # check for shortcuts
            self.process_perception(world)

            #  ok what I actually want is:
            # - if I get near the frontier prune it
            # - if i get out of range d_b of my waypoint, sample a new waypoint

        else:
            print("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
            print(f"I took {self.steps_taken} steps to complete the exploration")

        if self.debug:
            self.debug_logger()

    def explore(self, world, stepwise=False):
        '''
        Explore the world by sampling new frontiers and waypoints.
        if stepwise is True, the exploration will be done in steps.
        '''
        while self.no_more_frontiers == False:
            if not stepwise:
                self.explore_algo(world)
            elif stepwise:
                # BUG:: matplotlib crashes after 10 sec if we block the execution like this.
                self.keypress = keyboard.read_key()
                if self.keypress:
                    self.keypress = False
                    self.explore_algo(world)

        self.krm.draw_current_krm() # 

   
from src.entities.simulated_agent import SimulatedAgent
from src.entities.archive.frontier_sampler import FrontierSampler
from src.data_providers.local_grid_adapter import LocalGridAdapter

import networkx as nx

import uuid
   
class graphExplorationUseCase():

    def __init__(self, agent:SimulatedAgent, debug=True):
        self.agent  = agent
        self.consumable_path = None
        self.selected_frontier_idx = None
        self.init = False
        self.debug = debug
        self.sampler = FrontierSampler(debug_mode=True)
        self.frontier_sample_radius = 180
        self.prune_radius = 2.2
        self.shortcut_radius = 5
        self.N_samples = 20

    #############################################################################################
    ### ENTRYPOINT FOR GUIDING EXPLORATION WITH SEMANTICS ###
    #############################################################################################
    def evaluate_frontiers(self, agent, frontier_idxs, krm):
        ''' 
        Evaluate the frontiers and return the best one.
        this is the entrypoint for exploiting semantics        
        '''
        shortest_path_by_node_count = float('inf')
        selected_frontier_idx = None

        for frontier_idx in frontier_idxs:
            candidate_path = nx.shortest_path(
                krm.KRM, source=agent.at_wp, target=frontier_idx)
            # choose the last shortest path among equals
            # if len(candidate_path) <= shortest_path_by_node_count:
            #  choose the first shortest path among equals
            if len(candidate_path) < shortest_path_by_node_count:
                shortest_path_by_node_count = len(candidate_path)
                selected_frontier_idx = candidate_path[-1]

        return selected_frontier_idx
    #############################################################################################

    def select_target_frontier(self, agent, krm):
        ''' using the KRM, obtain the optimal frontier to visit next'''
        frontier_idxs = krm.get_all_frontiers_idxs()
        if len(frontier_idxs) > 0:
            target_frontier = self.evaluate_frontiers(agent, frontier_idxs, krm)

            return target_frontier
        else:
            self.no_more_frontiers = True
            return None, None

    def find_path_to_selected_frontier(self, agent, target_frontier, krm):
        '''
        Find the shortest path from the current waypoint to the target frontier.
        
        :param target_frontier: the frontier that we want to reach
        :return: The path to the selected frontier.
        '''
        path = nx.shortest_path(
            krm.KRM, source=agent.at_wp, target=target_frontier)
        return path


    def sample_waypoint(self, agent, krm):
        '''
        Sample a new waypoint at current agent pos, and add an edge connecting it to prev wp.
        this should be sampled from the pose graph eventually
        '''
        wp_at_previous_pos = krm.get_node_by_pos(agent.previous_pos)
        krm.add_waypoint(agent.pos, wp_at_previous_pos)
        agent.at_wp = krm.get_node_by_pos(agent.pos)


    def run_exploration_step(self, world, agent, local_grid_img, local_grid_adapter, krm):
        # TODO: some logic that is only used for exploration should be moved from the agent to here.
        # TODO: the conditions for these if statements are hella wonky. They should be tested more.

        if not self.init:
            # self.agent.sample_frontiers(world)  # sample frontiers from the world
            self.real_sample_step(agent, local_grid_img, local_grid_adapter, krm)
            self.init = True

        elif krm.KRM.nodes[krm.get_node_by_pos(self.agent.pos)]["type"] == "frontier":
            if self.debug:
                print(f"1. step: frontier processing")
            '''now we have visited the frontier we can remove it from the KRM and sample a waypoint in its place'''
            krm.remove_frontier(self.selected_frontier_idx)
            self.sample_waypoint(agent, krm)
            # self.agent.check_for_shortcuts(world)  # check for shortcuts
            # self.agent.process_world_object_perception(world)
            # self.agent.sample_frontiers(world)  # sample frontiers from the world
            self.real_sample_step(agent, local_grid_img, local_grid_adapter, krm)
            self.prune_frontiers(agent, krm)
            # print(f"agent_at_wp: {self.agent.at_wp}")
            # self.look_for_shortcuts(self.agent.at_wp, agent, local_grid_img, local_grid_adapter, world)
            
            self.selected_frontier_idx = None
        elif self.consumable_path:
            if self.debug:
                print(f"2. step: execute consumable path")
            self.consumable_path = self.agent.perform_path_step(self.consumable_path, krm)
        elif not self.selected_frontier_idx:
            '''if there are no more frontiers, exploration is done'''
            self.selected_frontier_idx = self.select_target_frontier(agent, krm)
            if self.no_more_frontiers:
                print("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
                print(f"It took {self.agent.steps_taken} steps to complete the exploration.")
                return True

            if self.debug:
                print(f"3. step: select target frontier and find path")
            # self.agent.sample_frontiers(world)  # sample frontiers from the world
            self.real_sample_step(agent, local_grid_img, local_grid_adapter, krm)
            self.prune_frontiers(agent, krm)
            self.consumable_path = self.find_path_to_selected_frontier(agent, self.selected_frontier_idx, krm)
            

        # if self.agent.debug:
        #     self.agent.debug_logger()  
   

    # def sample_frontiers(self, world):
    #     '''
    #     It samples a frontier from the world and adds it to the KRM, if its not already in it.
        
    #     :param world: the world object
    #     :return: None
    #     '''
    #     agent_at_world_node = world.get_node_by_pos(self.pos)
    #     # indexing the graph like this returns the neigbors
    #     observable_nodes = world.graph[agent_at_world_node]

    #     # so this is godmode dictionary with pos info of all nodes
    #     world_node_pos_dict = nx.get_node_attributes(world.graph, 'pos')

    #     for node in observable_nodes:
    #         obs_pos = world_node_pos_dict[node]
    #         # dict with all the pos of nodes already in krm
    #         krm_node_pos_dict = nx.get_node_attributes(self.krm.KRM, 'pos')

    #         # check if the there is not already a node in my KRM with the same position as the observable node
    #         if obs_pos not in krm_node_pos_dict.values():
    #             frontier_pos = obs_pos

    #             # if there is no node at that pos in the KRM, add it
    #             self.krm.add_frontier(frontier_pos, self.at_wp)

   
   
   
    def check_for_shortcuts_node_world(self, world, krm):
        agent_at_world_node = world.get_node_by_pos(self.pos)
        observable_nodes = world.graph[agent_at_world_node]

        for world_node in observable_nodes:
            # convert observable world node to krm node
            krm_node = krm.get_node_by_pos(world.graph.nodes[world_node]['pos'])

            if not krm.KRM.has_edge(krm_node, self.at_wp):
                if krm_node != self.at_wp and krm_node: # prevent self loops and None errors
                    if self.debug: 
                        print("shortcut found")
                    # add the correct type of edge
                    if krm.KRM.nodes[krm_node]["type"] == "frontier":
                        krm.KRM.add_edge(self.at_wp, krm_node, type="frontier_edge")
                    else:
                        krm.KRM.add_edge(self.at_wp, krm_node, type="waypoint_edge")

    # HACK: perception processing should be more eleborate and perhaps be its own separate entity
    def process_world_object_perception(self, world, krm):
        agent_at_world_node = world.get_node_by_pos(self.pos)
        if "world_object_dummy" in world.graph.nodes[agent_at_world_node].keys():
            world_object = world.graph.nodes[agent_at_world_node]["world_object_dummy"]
            if self.debug:
                print(f"world object '{world_object}' found")
            wo_pos = world.graph.nodes[agent_at_world_node]["world_object_pos_dummy"]
            krm.add_world_object(wo_pos, world_object)
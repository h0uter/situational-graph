from knowledge_roadmap.entities.agent import Agent
from knowledge_roadmap.entities.frontier_sampler import FrontierSampler
from knowledge_roadmap.entities.knowledge_road_map import KnowledgeRoadmap
from knowledge_roadmap.data_providers.local_grid_adapter import LocalGridAdapter

import networkx as nx
import uuid

class Exploration:
    def __init__(self, agent:Agent, len_of_map:float, debug=True):
        self.agent  = agent
        self.consumable_path = None
        self.selected_frontier_idx = None
        self.init = False
        self.debug = debug
        self.sampler = FrontierSampler(debug_mode=False)
        self.frontier_sample_radius = 180
        self.prune_radius = 2.2
        self.shortcut_radius = 5
        self.N_samples = 20
        self.len_of_entire_map = len_of_map

    #############################################################################################
    ### ENTRYPOINT FOR GUIDING EXPLORATION WITH SEMANTICS ###
    #############################################################################################
    def evaluate_frontiers(self, agent: Agent, frontier_idxs: list, krm: KnowledgeRoadmap):
        ''' 
        Evaluate the frontiers and return the best one.
        this is the entrypoint for exploiting semantics        
        '''
        shortest_path_by_node_count = float('inf')
        selected_frontier_idx = None

        for frontier_idx in frontier_idxs:
            candidate_path = nx.shortest_path(
                krm.graph, source=agent.at_wp, target=frontier_idx)
            # choose the last shortest path among equals
            # if len(candidate_path) <= shortest_path_by_node_count:
            #  choose the first shortest path among equals
            if len(candidate_path) < shortest_path_by_node_count:
                shortest_path_by_node_count = len(candidate_path)
                selected_frontier_idx = candidate_path[-1]

        return selected_frontier_idx
    #############################################################################################

    def select_target_frontier(self, agent: Agent, krm: KnowledgeRoadmap) -> int:
        ''' using the KRM, obtain the optimal frontier to visit next'''
        frontier_idxs = krm.get_all_frontiers_idxs()
        if len(frontier_idxs) > 0:
            target_frontier = self.evaluate_frontiers(agent, frontier_idxs, krm)

            return target_frontier
        else:
            self.no_more_frontiers = True
            return None, None

    def find_path_to_selected_frontier(self, agent: Agent, target_frontier: int, krm: KnowledgeRoadmap) -> list:
        '''
        Find the shortest path from the current waypoint to the target frontier.
        
        :param target_frontier: the frontier that we want to reach
        :return: The path to the selected frontier.
        '''
        path = nx.shortest_path(
                                krm.graph, 
                                source=agent.at_wp, 
                                target=target_frontier
                                )
        return path

    def real_sample_step(self, agent, local_grid_img, local_grid_adapter, krm):
        frontiers = self.sampler.sample_frontiers(
                                                local_grid_img, 
                                                local_grid_adapter, 
                                                radius=self.frontier_sample_radius, 
                                                num_frontiers_to_sample=self.N_samples
                                                )
        for frontier in frontiers:
            # translate the above to the global map
            x_local, y_local = frontier[0], frontier[1]
            # FIXME: what the hell conversiion is this
            x_global = agent.pos[0] + (x_local - local_grid_adapter.num_cells) / self.len_of_entire_map
            y_global = agent.pos[1] +  (y_local - local_grid_adapter.num_cells) / self.len_of_entire_map
            frontier_pos_global = (x_global, y_global)
            # gui.ax1.plot(x_global, y_global, 'ro')
            krm.add_frontier(frontier_pos_global, agent.at_wp)
    
    def sample_waypoint(self, agent, krm):
        '''
        Sample a new waypoint at current agent pos, and add an edge connecting it to prev wp.
        this should be sampled from the pose graph eventually
        '''
        wp_at_previous_pos = krm.get_node_by_pos(agent.previous_pos)
        krm.add_waypoint(agent.pos, wp_at_previous_pos)
        agent.at_wp = krm.get_node_by_pos(agent.pos)
   
    def get_nodes_of_type_in_radius(self, pos, radius, node_type, krm):
        '''
        Given a position, a radius and a node type, return a list of nodes of that type that are within the radius of the position.
        
        :param pos: the position of the agent
        :param radius: the radius of the circle
        :param node_type: the type of node to search for
        :return: The list of nodes that are close to the given position.
        '''
        close_nodes = []
        for node in krm.graph.nodes:
            data = krm.get_node_data_by_idx(node)
            if data['type'] == node_type:
                node_pos = data['pos']
                if abs(pos[0] - node_pos[0]) < radius and abs(pos[1] - node_pos[1]) < radius:
                    close_nodes.append(node)
        return close_nodes

    def prune_frontiers(self, agent, krm):
        '''obtain all the frontier nodes in krm in a certain radius around the current position'''
        
        waypoints = krm.get_all_waypoint_idxs()

        for wp in waypoints:
            wp_pos = krm.get_node_data_by_idx(wp)['pos']
            close_frontiers = self.get_nodes_of_type_in_radius(wp_pos, self.prune_radius, 'frontier', krm)
            for frontier in close_frontiers:
                krm.remove_frontier(frontier)

    # def look_for_shortcuts(self, new_wp, agent, local_grid_img, local_grid_adapter:LocalGridAdapter, world, krm):
    #     # get new_wp pos,
    #     new_wp_pos = krm.get_node_data_by_idx(new_wp)['pos']

    #     # get all the waypoints in a radius around it
    #     existing_nearby_wps = self.get_nodes_of_type_in_radius(new_wp_pos, self.shortcut_radius, 'waypoint')
    #     print(f"--nearby wps: {existing_nearby_wps}")
    #     if len(existing_nearby_wps) > 0:
    #         for existing_wp in existing_nearby_wps:
    #         # if there is a waypoint in the radius, add a new edge between the two waypoints
    #             if existing_wp != new_wp:
    #                 # BUG: do collision check here
    #                 existing_wp_pos = krm.get_node_data_by_idx(existing_wp)['pos']
    #                 # new_wp_x_pix, new_wp_y_pix = local_grid_adapter.world_coord2pix_idx(world, new_wp_pos[0], new_wp_pos[1])
    #                 new_wp_pix = local_grid_adapter.world_coord2global_pix_idx(world, new_wp_pos[0], new_wp_pos[1])
    #                 # new_wp_pix = local_grid_adapter.world_coord2global_pix_idx(world, new_wp_pos[1], new_wp_pos[0])
    #                 existing_wp_pix = local_grid_adapter.world_coord2global_pix_idx(world, existing_wp_pos[0], existing_wp_pos[1])
    #                 # existing_wp_pix = local_grid_adapter.world_coord2global_pix_idx(world, existing_wp_pos[1], existing_wp_pos[0])
                    
    #                 # existing_wp_pix = (abs(new_wp_pix[0]) - abs(existing_wp_pix[0]), abs(new_wp_pix[1]) - abs(existing_wp_pix[1]))
    #                 existing_wp_pix = (local_grid_adapter.size_pix + abs(existing_wp_pix[0]) - abs(new_wp_pix[0]), local_grid_adapter.size_pix + abs(existing_wp_pix[1]) - abs(new_wp_pix[1]))
                    
                    
    #                 print(f"--existing wp pix : {existing_wp_pix}")
    #                 new_wp_pix = (local_grid_adapter.size_pix, local_grid_adapter.size_pix)
    #                 new_edge_not_in_collision =self.sampler.collision_check(local_grid_img, new_wp_pix, existing_wp_pix,local_grid_adapter)
    #                 if new_edge_not_in_collision:
    #                     krm.graph.add_edge(new_wp, existing_wp, type="waypoint_edge", id=uuid.uuid4())
    #                 else:
    #                     print(f"existing_wp {existing_wp} is in collision with new_wp {new_wp}")


    def run_exploration_step(self, agent, local_grid_img, local_grid_adapter, krm):
        if not self.init:
            self.real_sample_step(agent, local_grid_img, local_grid_adapter, krm)
            self.init = True

        elif krm.graph.nodes[krm.get_node_by_pos(self.agent.pos)]["type"] == "frontier":
            if self.debug:
                print(f"1. step: frontier processing")
            '''now we have visited the frontier we can remove it from the KRM and sample a waypoint in its place'''
            krm.remove_frontier(self.selected_frontier_idx)
            self.sample_waypoint(agent, krm)
            self.real_sample_step(agent, local_grid_img, local_grid_adapter, krm)
            self.prune_frontiers(agent, krm)
            # self.look_for_shortcuts(self.agent.at_wp, agent, local_grid_img, local_grid_adapter, world)
            
            self.selected_frontier_idx = None
        elif self.consumable_path:
            if self.debug:
                print(f"2. step: execute consumable path")
            self.consumable_path = self.agent.perform_path_step(self.consumable_path, krm)
        elif not self.selected_frontier_idx:
            '''if there are no more frontiers, exploration is done'''
            self.selected_frontier_idx = self.select_target_frontier(agent, krm)
            if self.agent.no_more_frontiers:
                print("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
                print(f"It took {self.agent.steps_taken} steps to complete the exploration.")
                return True

            if self.debug:
                print(f"3. step: select target frontier and find path")
            self.real_sample_step(agent, local_grid_img, local_grid_adapter, krm)
            self.prune_frontiers(agent, krm)
            self.consumable_path = self.find_path_to_selected_frontier(agent, self.selected_frontier_idx, krm) 

        if self.agent.debug:
            self.agent.debug_logger()
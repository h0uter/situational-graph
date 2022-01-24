from knowledge_roadmap.entities.agent import Agent
from knowledge_roadmap.entities.frontier_sampler import FrontierSampler
from knowledge_roadmap.data_providers.local_grid_adapter import LocalGridAdapter

import uuid

class Exploration:
    def __init__(self, agent:Agent, debug=True):
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

    def real_sample_step(self, agent, local_grid_img, local_grid_adapter):
        frontiers = self.sampler.sample_frontiers(local_grid_img, local_grid_adapter, radius=self.frontier_sample_radius, num_frontiers_to_sample=self.N_samples)
        for frontier in frontiers:
                # plot the sampled frontier edge in fig2
                # should go to gui
                # xx, yy = self.sampler.get_cells_under_line((local_grid_adapter.size_pix, local_grid_adapter.size_pix), frontier)
                # plt.plot(xx, yy) # draw the line as collection of pixels

                # translate the above to the global map
                # this shoould go into the exploration logic
                x_local, y_local = frontier[0], frontier[1]
                x_global = agent.pos[0] + (x_local - local_grid_adapter.size_pix) / 50
                y_global = agent.pos[1] +  (y_local - local_grid_adapter.size_pix) /50
                frontier_pos_global = (x_global, y_global)
                # gui.ax1.plot(x_global, y_global, 'ro')
                agent.krm.add_frontier(frontier_pos_global, agent.at_wp)
        

    def get_nodes_of_type_in_radius(self, pos, radius, node_type):
        '''
        Given a position, a radius and a node type, return a list of nodes of that type that are within the radius of the position.
        
        :param pos: the position of the agent
        :param radius: the radius of the circle
        :param node_type: the type of node to search for
        :return: The list of nodes that are close to the given position.
        '''
        close_nodes = []
        for node in self.agent.krm.KRM.nodes:
            data = self.agent.krm.get_node_data_by_idx(node)
            if data['type'] == node_type:
                node_pos = data['pos']
                if abs(pos[0] - node_pos[0]) < radius and abs(pos[1] - node_pos[1]) < radius:
                    close_nodes.append(node)
        return close_nodes

    def prune_frontiers(self, agent):
        '''obtain all the frontier nodes in krm in a certain radius around the current position'''
        
        waypoints = agent.krm.get_all_waypoint_idxs()
        # print(f"all waypoints: {waypoints}")

        for wp in waypoints:
            wp_pos = agent.krm.get_node_data_by_idx(wp)['pos']
            # close_frontiers = self.get_frontiers_in_radius(wp_pos)
            close_frontiers = self.get_nodes_of_type_in_radius(wp_pos, self.prune_radius, 'frontier')
            for frontier in close_frontiers:
                agent.krm.remove_frontier(frontier)

    def look_for_shortcuts(self, new_wp, agent, local_grid_img, local_grid_adapter:LocalGridAdapter, world):
        # get new_wp pos,
        new_wp_pos = agent.krm.get_node_data_by_idx(new_wp)['pos']

        # get all the waypoints in a radius around it
        existing_nearby_wps = self.get_nodes_of_type_in_radius(new_wp_pos, self.shortcut_radius, 'waypoint')
        print(f"--nearby wps: {existing_nearby_wps}")
        if len(existing_nearby_wps) > 0:
            for existing_wp in existing_nearby_wps:
            # if there is a waypoint in the radius, add a new edge between the two waypoints
                if existing_wp != new_wp:
                    # print(f"--existing wp: {existing_wp}")
                    # BUG: do collision check here
                    existing_wp_pos = agent.krm.get_node_data_by_idx(existing_wp)['pos']
                    # new_wp_x_pix, new_wp_y_pix = local_grid_adapter.world_coord2pix_idx(world, new_wp_pos[0], new_wp_pos[1])
                    new_wp_pix = local_grid_adapter.world_coord2global_pix_idx(world, new_wp_pos[0], new_wp_pos[1])
                    # new_wp_pix = local_grid_adapter.world_coord2global_pix_idx(world, new_wp_pos[1], new_wp_pos[0])
                    existing_wp_pix = local_grid_adapter.world_coord2global_pix_idx(world, existing_wp_pos[0], existing_wp_pos[1])
                    # existing_wp_pix = local_grid_adapter.world_coord2global_pix_idx(world, existing_wp_pos[1], existing_wp_pos[0])
                    
                    # existing_wp_pix = (abs(new_wp_pix[0]) - abs(existing_wp_pix[0]), abs(new_wp_pix[1]) - abs(existing_wp_pix[1]))
                    existing_wp_pix = (local_grid_adapter.size_pix + abs(existing_wp_pix[0]) - abs(new_wp_pix[0]), local_grid_adapter.size_pix + abs(existing_wp_pix[1]) - abs(new_wp_pix[1]))
                    
                    
                    print(f"--existing wp pix : {existing_wp_pix}")
                    new_wp_pix = (local_grid_adapter.size_pix, local_grid_adapter.size_pix)
                    # print(f"--new wp pix : {new_wp_pix}")
                    new_edge_not_in_collision =self.sampler.collision_check(local_grid_img, new_wp_pix, existing_wp_pix,local_grid_adapter, True)
                    if new_edge_not_in_collision:
                        self.agent.krm.KRM.add_edge(new_wp, existing_wp, type="waypoint_edge", id=uuid.uuid4())
                        # print(f"--added edge between {new_wp} and {existing_wp}")
                    else:
                        print(f"existing_wp {existing_wp} is in collision with new_wp {new_wp}")
    def run_exploration_step(self, world, agent, local_grid_img, local_grid_adapter):
        # TODO: some logic that is only used for exploration should be moved from the agent to here.
        # TODO: the conditions for these if statements are hella wonky. They should be tested more.

        if not self.init:
            # self.agent.sample_frontiers(world)  # sample frontiers from the world
            self.real_sample_step(agent, local_grid_img, local_grid_adapter)
            self.init = True

        elif self.agent.krm.KRM.nodes[self.agent.krm.get_node_by_pos(self.agent.pos)]["type"] == "frontier":
            if self.debug:
                print(f"1. step: frontier processing")
            '''now we have visited the frontier we can remove it from the KRM and sample a waypoint in its place'''
            self.agent.krm.remove_frontier(self.selected_frontier_idx)
            self.agent.sample_waypoint()
            # self.agent.check_for_shortcuts(world)  # check for shortcuts
            # self.agent.process_world_object_perception(world)
            # self.agent.sample_frontiers(world)  # sample frontiers from the world
            self.real_sample_step(agent, local_grid_img, local_grid_adapter)
            self.prune_frontiers(agent)
            # print(f"agent_at_wp: {self.agent.at_wp}")
            # self.look_for_shortcuts(self.agent.at_wp, agent, local_grid_img, local_grid_adapter, world)
            
            self.selected_frontier_idx = None
        elif self.consumable_path:
            if self.debug:
                print(f"2. step: execute consumable path")
            self.consumable_path = self.agent.perform_path_step(self.consumable_path)
        elif not self.selected_frontier_idx:
            '''if there are no more frontiers, exploration is done'''
            self.selected_frontier_idx = self.agent.select_target_frontier()
            if self.agent.no_more_frontiers:
                print("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
                print(f"It took {self.agent.steps_taken} steps to complete the exploration.")
                return

            if self.debug:
                print(f"3. step: select target frontier and find path")
            # self.agent.sample_frontiers(world)  # sample frontiers from the world
            self.real_sample_step(agent, local_grid_img, local_grid_adapter)
            self.prune_frontiers(agent)
            self.consumable_path = self.agent.find_path_to_selected_frontier(self.selected_frontier_idx)
            

        if self.agent.debug:
            self.agent.debug_logger()
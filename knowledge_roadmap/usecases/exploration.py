from knowledge_roadmap.entities.agent import Agent
from knowledge_roadmap.entities.frontier_sampler import FrontierSampler

class Exploration:
    def __init__(self, agent:Agent, debug=True):
        self.agent  = agent
        self.consumable_path = None
        self.selected_frontier_idx = None
        self.init = False
        self.debug = debug
        self.sampler = FrontierSampler()

    def real_sample_step(self, agent, local_grid_img, local_grid_adapter):
        frontiers = self.sampler.sample_frontiers(local_grid_img, local_grid_adapter, radius=90, num_frontiers_to_sample=5)
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
        
    def prune_frontiers(self, agent):
        '''obtain all the frontier nodes in krm in a certain radius around the current position'''
        
        # remove frontiers that are too close to an existing waypoint
        # close_frontiers = self.get_frontiers_in_radius(agent.pos, 1)
        # if len(close_frontiers) > 0:
        #     for frontier in close_frontiers:
        #         agent.krm.remove_frontier(frontier)

        waypoints = agent.krm.get_all_waypoint_idxs()
        print(f"all waypoints: {waypoints}")

        for wp in waypoints:
            wp_pos = agent.krm.get_node_data_by_idx(wp)['pos']
            close_frontiers = self.get_frontiers_in_radius(wp_pos)
            for frontier in close_frontiers:
                agent.krm.remove_frontier(frontier)

    def get_frontiers_in_radius(self, pos, radius=1.2):
        close_frontiers = []
        for node in self.agent.krm.KRM.nodes:
            data = self.agent.krm.get_node_data_by_idx(node)

            if data['type'] == "frontier":
                frontier_pos = data['pos']
                print(f"frontier pos: {frontier_pos}")
                print(f"pos: {pos}")
                if abs(pos[0] - frontier_pos[0]) < radius and abs(pos[1] - frontier_pos[1]) < radius:
                    close_frontiers.append(node)
        print(f"{len(close_frontiers)} frontiers in radius {radius}")
        return close_frontiers

            


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
            self.consumable_path = self.agent.find_path_to_selected_frontier(self.selected_frontier_idx)
            

        if self.agent.debug:
            self.agent.debug_logger()
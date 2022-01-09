from src.entities.agent import Agent
from src.data_providers.world import ManualGraphWorld, LatticeWorld
import matplotlib.pyplot as plt
import keyboard


# HACK: exploration logic is still very tightly coupled to the agent class

class Exploration:
    def __init__(self, agent:Agent):
        # self.agent  = Agent(debug=False)
        self.agent  = agent
        self.consumable_path = None
        self.selected_frontier_idx = None
        self.init = False

    # def perform_path_step(self):
    #     '''
    #     Perform a single step of the active path.
    #     '''
    #     closest_wp_to_selected_frontier = self.agent.krm.get_node_data_by_idx(self.active_path[-1])

    #     '''If the pos of the closest wp to our frontier is not our agent pos, we need to move to it'''
    #     if closest_wp_to_selected_frontier['pos'] != self.agent.pos:
    #         node_idx = self.active_path.pop(0)
    #         node_data = self.agent.krm.get_node_data_by_idx(node_idx)
    #         self.teleport_to_pos(node_data['pos'])

    def exploration_procedure(self, world):
        '''the logic powering exploration'''
    
        self.agent.sample_frontiers(world)  # sample frontiers from the world
        self.agent.process_world_object_perception(world)

        # FIXME: exploration logic should not contain vizualisation
        '''visualize the KRM'''
        self.agent.krm.draw_current_krm()  # illustrate krm with new frontiers
        self.agent.draw_agent(self.agent.pos)  # draw the agent on the world
        plt.pause(0.05)

        '''select the target frontier and if there are no more frontiers remaining, we are done'''
        selected_frontier_idx = self.agent.select_target_frontier()  # select a frontier to visit
        
        # if there are no more frontiers, we are done
        if self.agent.no_more_frontiers:
            print("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
            print(f"It took {self.agent.steps_taken} steps to complete the exploration.")
            return

        selected_path = self.agent.find_path_to_selected_frontier(
            selected_frontier_idx)

        consumable_path = selected_path
        while consumable_path:
            # consumable_path = self.agent.perform_path_step(consumable_path, selected_frontier_idx)
            consumable_path = self.agent.perform_path_step(consumable_path)
            # FIXME: this drawing logic should go in the GUI
            self.agent.draw_agent(self.agent.pos)
            plt.show()
            plt.pause(0.05)
            if self.agent.krm.KRM.nodes[self.agent.krm.get_node_by_pos(self.agent.pos)]["type"] == "frontier":
                print(f"we are on a frontier node")

        '''now we have visited the frontier we can remove it from the KRM and sample a waypoint in its place'''
        self.agent.krm.remove_frontier(selected_frontier_idx)
        # TODO: pruning frontiers should be independent of sampling waypoints
        self.agent.sample_waypoint()
        self.agent.check_for_shortcuts(world)  # check for shortcuts

        if self.agent.debug:
            self.agent.debug_logger()


    # FIXME: I guess this should go to the GUI class
    def explore(self, world, stepwise=False):
        '''
        Explore the world by sampling new frontiers and waypoints.
        if stepwise is True, the exploration will be done in steps.
        '''
        while self.agent.no_more_frontiers == False:
            if not stepwise:
                self.exploration_procedure(world)
            # FIXME: this is the entrpoint for the gui
            elif stepwise:
                # BUG:: matplotlib crashes after 10 sec if we block the execution like this.
                self.keypress = keyboard.read_key()
                if self.keypress:
                    self.keypress = False
                    self.exploration_procedure(world)

        # FIXME: this should be done using the GUI
        self.agent.krm.draw_current_krm() # 


    # FIXME: I guess this should go to the GUI class
    def explore2(self, world, stepwise=False):
        '''
        Explore the world by sampling new frontiers and waypoints.
        if stepwise is True, the exploration will be done in steps.
        '''
        while self.agent.no_more_frontiers == False:
            if not stepwise:
                self.run_exploration_step(world)

                # FIXME: this is the entrpoint for the gui
                self.agent.krm.draw_current_krm()  # illustrate krm with new frontiers
                self.agent.draw_agent(self.agent.pos)  # draw the agent on the world
                plt.pause(0.05)
            elif stepwise:
                # BUG:: matplotlib crashes after 10 sec if we block the execution like this.
                self.keypress = keyboard.read_key()
                if self.keypress:
                    self.keypress = False
                    self.exploration_procedure(world)

        # FIXME: this should be done using the GUI
        self.agent.krm.draw_current_krm() # 


    def run_exploration_step(self, world):
        # TODO: the conditions for these if statements are hella wonky
        # they should be tested more.


        if not self.init:
            self.agent.sample_frontiers(world)  # sample frontiers from the world
            self.init = True
        # if there are no more frontiers, we are done
        elif self.agent.krm.KRM.nodes[self.agent.krm.get_node_by_pos(self.agent.pos)]["type"] == "frontier":
            print(f"we are on a frontier node")
            '''now we have visited the frontier we can remove it from the KRM and sample a waypoint in its place'''
            self.agent.krm.remove_frontier(self.selected_frontier_idx)
            # TODO: pruning frontiers should be independent of sampling waypoints
            self.agent.sample_waypoint()
            self.agent.check_for_shortcuts(world)  # check for shortcuts
            self.agent.process_world_object_perception(world)
            self.agent.sample_frontiers(world)  # sample frontiers from the world
            self.selected_frontier_idx = None
        elif self.consumable_path:
            print(f"we are executing a consumable path")
            self.consumable_path = self.agent.perform_path_step(self.consumable_path)
        elif self.selected_frontier_idx and not self.consumable_path:
            print(f"we are calculating a path")
            self.consumable_path = self.agent.find_path_to_selected_frontier(self.selected_frontier_idx)
        elif not self.selected_frontier_idx:
            print(f"we are selecting a new target frontier")
            self.agent.sample_frontiers(world)  # sample frontiers from the world
            self.selected_frontier_idx = self.agent.select_target_frontier()
            if self.agent.no_more_frontiers:
                print("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
                print(f"It took {self.agent.steps_taken} steps to complete the exploration.")
                return

        if self.agent.debug:
            self.agent.debug_logger()
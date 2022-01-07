from src.entities.agent import Agent
from src.entities.world import *
import matplotlib.pyplot as plt
import keyboard


class Exploration:

    def __init__(self):
        self.agent  = Agent()

    def explore_algo(self, world):
        '''the logic powering exploration'''
    
        self.agent.sample_frontiers(world)  # sample frontiers from the world

        # FIXME: this should be done using the GUI
        '''visualize the KRM'''
        self.agent.krm.draw_current_krm()  # illustrate krm with new frontiers
        self.agent.draw_agent(self.agent.pos)  # draw the agent on the world
        plt.pause(0.3)

        '''select the target frontier and if there are no more frontiers remaining, we are done'''
        selected_frontier_idx = self.agent.select_target_frontier()  # select a frontier to visit
        
        if not self.agent.no_more_frontiers:  # if there are no more frontiers, we are done
            selected_path = self.agent.find_path_to_closest_wp_to_selected_frontier(
                selected_frontier_idx)

            self.agent.execute_path(selected_path, world)

            '''after reaching the wp next to the selected frontier, move to the selected frontier'''
            self.agent.step_from_wp_to_frontier(selected_frontier_idx)

            '''now we have visited the frontier we can remove it from the KRM and sample a waypoint in its place'''
            self.agent.krm.remove_frontier(selected_frontier_idx)
            # TODO: pruning frontiers should be independent of sampling waypoints
            self.agent.sample_waypoint()
            self.agent.check_for_shortcuts(world)  # check for shortcuts
            self.agent.process_perception(world)

            #  ok what I actually want is:
            # - if I get near the frontier prune it
            # - if i get out of range d_b of my waypoint, sample a new waypoint

        else:
            print("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
            print(f"I took {self.agent.steps_taken} steps to complete the exploration")

        if self.agent.debug:
            self.agent.debug_logger()

    def explore(self, world, stepwise=False):
        '''
        Explore the world by sampling new frontiers and waypoints.
        if stepwise is True, the exploration will be done in steps.
        '''
        while self.agent.no_more_frontiers == False:
            if not stepwise:
                self.explore_algo(world)
            elif stepwise:
                # BUG:: matplotlib crashes after 10 sec if we block the execution like this.
                self.keypress = keyboard.read_key()
                if self.keypress:
                    self.keypress = False
                    self.explore_algo(world)

        # FIXME: this should be done using the GUI
        self.agent.krm.draw_current_krm() # 
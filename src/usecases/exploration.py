from src.entities.agent import Agent

class Exploration:
    def __init__(self, agent:Agent):
        self.agent  = agent
        self.consumable_path = None
        self.selected_frontier_idx = None
        self.init = False

    def run_exploration_step(self, world):
        # TODO: some logic that is only used for exploration should be moved from the agent to here.
        # TODO: the conditions for these if statements are hella wonky. They should be tested more.

        if not self.init:
            self.agent.sample_frontiers(world)  # sample frontiers from the world
            self.init = True

        elif self.agent.krm.KRM.nodes[self.agent.krm.get_node_by_pos(self.agent.pos)]["type"] == "frontier":
            
            print(f"we are on a frontier node")
            '''now we have visited the frontier we can remove it from the KRM and sample a waypoint in its place'''
            self.agent.krm.remove_frontier(self.selected_frontier_idx)
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
            
            '''if there are no more frontiers, exploration is done'''
            if self.agent.no_more_frontiers:
                print("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
                print(f"It took {self.agent.steps_taken} steps to complete the exploration.")
                return

        if self.agent.debug:
            self.agent.debug_logger()
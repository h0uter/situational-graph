from knowledge_roadmap.entities.agent import Agent

class Exploration:
    def __init__(self, agent:Agent, debug=False):
        self.agent  = agent
        self.consumable_path = None
        self.selected_frontier_idx = None
        self.init = False
        self.debug = debug

    def run_exploration_step(self, world):
        # TODO: some logic that is only used for exploration should be moved from the agent to here.
        # TODO: the conditions for these if statements are hella wonky. They should be tested more.

        if not self.init:
            self.agent.sample_frontiers(world)  # sample frontiers from the world
            self.init = True

        elif self.agent.krm.KRM.nodes[self.agent.krm.get_node_by_pos(self.agent.pos)]["type"] == "frontier":
            if self.debug:
                print(f"1. step: frontier processing")
            '''now we have visited the frontier we can remove it from the KRM and sample a waypoint in its place'''
            self.agent.krm.remove_frontier(self.selected_frontier_idx)
            self.agent.sample_waypoint()
            self.agent.check_for_shortcuts(world)  # check for shortcuts
            self.agent.process_world_object_perception(world)
            self.agent.sample_frontiers(world)  # sample frontiers from the world
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
            self.agent.sample_frontiers(world)  # sample frontiers from the world
            self.consumable_path = self.agent.find_path_to_selected_frontier(self.selected_frontier_idx)
            

        if self.agent.debug:
            self.agent.debug_logger()
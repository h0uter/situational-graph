import time
from typing import Sequence

from src.data_providers.abstract_agent import AbstractAgent
from src.usecases.tosg import TOSG
from src.usecases.behaviors.abstract_behavior import AbstractBehavior
from src.utils.audio_feedback import play_hi_follow_me
from src.utils.config import Config
from src.entities.dynamic_data.node_and_edge import Edge, Node


class PlanExtractionBehavior(AbstractBehavior):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def _run_behavior_implementation(
        self, agent: AbstractAgent, krm: TOSG, action_path: Sequence[Edge]
    ):
        """Currently the world object action is guide victim home action"""
        # Should I allow an action to set a different action path?
        if self.cfg.AUDIO_FEEDBACK:
            play_hi_follow_me()

        time.sleep(2)
        agent.assigned_victim = action_path[-1][1]
        krm.remove_world_object(action_path[-1][1])

        extraction_goal_node = self.find_best_exit(agent, krm)

        action_path = self.update_krm_with_guide_actions(
            agent, krm, extraction_goal_node
        )

        return action_path

        # start_node = self.guide_victim_home_old(agent, krm, action_path)
        # action_path = []
        # return action_path, start_node

    def update_krm_with_guide_actions(
        self, agent: AbstractAgent, krm: TOSG, exit_node: Node
    ) -> Sequence[Edge]:
        """
        Add guide actions to the krm.
        """
        path = krm.shortest_path(agent.at_wp, exit_node)
        krm.add_guide_action_edges(path)
        action_path = krm.node_list_to_edge_list(path)

        return action_path

    def find_best_exit(self, agent, krm):
        """
        Find the best exit for the agent.
        """
        # For now the best exit is always the start node.
        best_exit = 0
        return best_exit

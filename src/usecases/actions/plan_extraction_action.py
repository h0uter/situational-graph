from typing import Sequence
from src.entities.abstract_agent import AbstractAgent
from src.entities.krm import KRM
from src.usecases.actions.abstract_action import AbstractAction
from src.utils.config import Config
from src.utils.my_types import EdgeType, Node, Edge
from src.utils.audio_feedback import play_hi_follow_me
import time


class PlanExtractionAction(AbstractAction):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def run(self, agent: AbstractAgent, krm: KRM, action_path: Sequence[Edge]):
        """Currently the world object action is guide victim home action"""
        # Should I allow an action to set a different action path?
        if self.cfg.AUDIO_FEEDBACK:
            play_hi_follow_me()

        time.sleep(2)
        agent.assigned_victim = action_path[-1][1]
        krm.remove_world_object(action_path[-1][1])

        extraction_goal_node = self.find_best_exit(agent, krm)

        action_path = self.update_krm_with_guide_actions(agent, krm, extraction_goal_node)

        return action_path

        # start_node = self.guide_victim_home_old(agent, krm, action_path)
        # action_path = []
        # return action_path, start_node

    def update_krm_with_guide_actions(self, agent: AbstractAgent, krm: KRM, exit_node: Node) -> Sequence[Edge]:
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

    # def guide_victim_home_old(self, agent, krm, action_path):

    #     if self.cfg.AUDIO_FEEDBACK:
    #         play_hi_follow_me()

    #     self._log.debug(
    #         f"{agent.name}: world_object_action_edge():: removing world object {action_path[-1][-1]} from graph."
    #     )

    #     # calc the shortest path
    #     # add guide action edges along the path
    #     # set_target to the start node
    #     # perhaps add a droppoff action to the last node.

    #     time.sleep(2)
    #     krm.remove_world_object(action_path[-1][1])

    #     # TODO: can actions change the action path and/or the target_node?
    #     # action_path = krm.shortest_path(agent.at_wp, start_node)
    #     # self._log.debug(
    #     #     f"{agent.name}: world_object_action_edge():: action_path: {action_path}"
    #     # )
    #     # return action_path
    #     # self.target_node = start_node

    #     start_node = 0
    #     return start_node

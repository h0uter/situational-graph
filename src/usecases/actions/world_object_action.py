from src.usecases.actions.abstract_action import AbstractAction
from src.utils.config import Config
import time


class WorldObjectAction(AbstractAction):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def run(self, agent, krm, action_path):
        """Currently the world object action is guide victim home action"""
        # Should I allow an action to set a different action path?
        start_node = self.guide_victim_home(agent, krm, action_path)

        return [], start_node

    def guide_victim_home(self, agent, krm, action_path):
        start_node = 0
        self._log.debug(
            f"{agent.name}: world_object_action_edge():: removing world object {action_path[-1]} from graph."
        )
        time.sleep(2)
        krm.remove_world_object(action_path[-1])

        # TODO: can actions change the action path and/or the target_node?
        # action_path = krm.shortest_path(agent.at_wp, start_node)
        # self._log.debug(
        #     f"{agent.name}: world_object_action_edge():: action_path: {action_path}"
        # )
        # return action_path
        # self.target_node = start_node
        return start_node

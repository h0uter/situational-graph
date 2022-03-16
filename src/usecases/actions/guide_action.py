from src.usecases.actions.abstract_action import AbstractAction
from src.utils.config import Config
from src.utils.audio_feedback import play_hi_follow_me
from src.usecases.actions.goto_action import GotoAction
import time


class GuideAction(AbstractAction):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def run(self, agent, krm, action_path):
        """Currently the world object action is guide victim home action"""
        # Should I allow an action to set a different action path?
        self._log.debug(
            f"{agent.name}: GUiding  victim to next wp {action_path[0][1]}"
        )
        # if self.cfg.AUDIO_FEEDBACK:
        #     play_hi_follow_me()

        action_path = GotoAction(self.cfg).run(agent, krm, action_path)

        if self.check_if_victim_still_in_perception_scene(agent):
            # TODO: remove guide action edge
            self._log.debug(f"{agent.name}: guide action succesfull victim is still in perception scene")
            return action_path
        else:
            self._log.debug(f"{agent.name}: guide action failed victim is not in perception scene, going back")
            return []

    def check_if_victim_still_in_perception_scene(self, agent) -> bool:
        """
        Check if the victim is still in the perception scene.
        """
        return True

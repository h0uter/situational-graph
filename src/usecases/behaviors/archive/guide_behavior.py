from src.entities import AbstractAgent, TOSG
from src.usecases.behaviors.abstract_behavior import AbstractBehavior
from src.usecases.behaviors.goto_behavior import GotoBehavior
from src.utils.audio_feedback import play_file, play_hi_follow_me
from src.utils.config import Config, Scenario


class GuideBehavior(AbstractBehavior):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def _run_behavior_implementation(
        self, agent: AbstractAgent, krm: TOSG, action_path
    ):
        """Currently the world object action is guide victim home action"""
        # Should I allow an action to set a different action path?
        self._log.debug(f"{agent.name}: Guiding  victim to next wp {action_path[0][1]}")
        # if self.cfg.AUDIO_FEEDBACK:
        #     play_hi_follow_me()
        old_action_path = action_path

        if self.check_if_victim_still_in_perception_scene(agent):
            # action_path = GotoBehavior(self.cfg).run(agent, krm, action_path)
            action_path = GotoBehavior(self.cfg).pipeline(agent, krm, action_path)
            # TODO: remove guide action edge
            self._log.debug(
                f"{agent.name}: guide action succesfull victim is still in perception scene"
            )
            if not action_path and self.cfg.AUDIO_FEEDBACK:
                play_file("arrived_at_exit.mp3")

            return action_path
        else:
            self._log.debug(
                f"{agent.name}: guide action failed victim is not in perception scene, going back"
            )

            if self.cfg.AUDIO_FEEDBACK:
                play_file("guide_victim_out_of_view.mp3")

            agent.move_to_pos(
                krm.get_node_data_by_node(old_action_path[0][0])["pos"], agent.heading
            )
            agent.previous_pos = agent.get_localization()

            return old_action_path

    def check_if_victim_still_in_perception_scene(self, agent: AbstractAgent) -> bool:
        """
        Check if the victim is still in the perception scene.
        """
        return True
        # if self.cfg.SCENARIO == Scenario.REAL:
        #     wos = agent.look_for_world_objects_in_perception_scene()
        #     if not wos:
        #         return False
        #     for wo in wos:
        #         if wo == agent.assigned_victim:
        #             return True
        #     return False
        # else:
        #     return True

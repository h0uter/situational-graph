from src.config import cfg, Scenario
from src.shared.situations import Situations
from src.shared.world_object import WorldObject


class WorldObjectSpoofer:
    def __init__(self) -> None:
        self.world_object_list = []

        if cfg.SCENARIO == Scenario.SIM_VILLA:
            self.world_object_list = [
                WorldObject((-15.5, 14), Situations.UNKNOWN_VICTIM),
                # WorldObject((14, -14), "fire1"),
                # WorldObject((9.5, 8), "closed door1"),
                # WorldObject((13, 0), "victim2"),
                WorldObject((14, -14), Situations.UNKNOWN_VICTIM),
                WorldObject((-15.5, -14.5), Situations.UNKNOWN_VICTIM),
                # WorldObject((-2, 14), ObjectTypes.UNKNOWN_VICTIM),
                # WorldObject((-2, 12), "victim5"),
                WorldObject((0, 14), Situations.UNKNOWN_VICTIM),
                # # WorldObject((14, -14), "fire1"),
                # # WorldObject((9.5, 8), "closed door1"),
                # # WorldObject((13, 0), "victim2"),
                # WorldObject((14, -14), "victim2"),
                # WorldObject((-15.5, -14.5), "victim3"),
                # WorldObject((-2, 14), "victim4"),
                # # WorldObject((-2, 12), "victim5"),
                # WorldObject((0, 14), "victim5"),
            ]

    def spoof_world_objects_from_position(
        self, agent_pos: tuple[float, float]
    ) -> list[WorldObject]:

        # if line of sight with world object, return the world object
        # kinda waste of time to do line of sight check if the real robot does not need that....
        # to mimic the real fiducial server we should return an id and a transform...

        # TODO: add line of sight check

        DETECTION_MARGIN = 2.5
        world_objects_in_scene = list()
        for spoof in self.world_object_list:
            if (
                abs(agent_pos[0] - spoof.pos[0]) < DETECTION_MARGIN
                and abs(agent_pos[1] - spoof.pos[1]) < DETECTION_MARGIN
            ):
                world_objects_in_scene.append(spoof)
                self.world_object_list.remove(spoof)

        return world_objects_in_scene

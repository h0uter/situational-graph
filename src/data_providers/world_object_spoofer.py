from src.utils.config import Config, Scenario
from src.entities.world_object import WorldObject


class WorldObjectSpoofer:
    def __init__(self, cfg: Config) -> None:
        self.world_object_list = []

        if cfg.SCENARIO == Scenario.SIM_VILLA:
            self.world_object_list = [
                WorldObject((-15.5, 14), "victim1"),
                WorldObject((14, -14), "fire1"),
                WorldObject((9.5, 8), "closed door1"),
                WorldObject((13, 0), "victim2"),
            ]

    def spoof_world_objects_from_position(self, agent_pos: tuple[float, float]) -> list[WorldObject]:

        # if line of sight with world object, return the world object
        # kinda waste of time to do line of sight check if the real robot does not need that....
        # to mimic the real fiducial server we should return an id and a transform...

        margin = 3
        world_objects_in_scene = list()
        for spoof in self.world_object_list:
            if (
                abs(agent_pos[0] - spoof.pos[0]) < margin
                and abs(agent_pos[1] - spoof.pos[1]) < margin
            ):
                world_objects_in_scene.append(spoof)

        # if len(close_nodes) == 0:
        #     return []
        return world_objects_in_scene

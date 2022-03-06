from src.entities.abstract_agent import AbstractAgent
from src.data_providers.local_grid_image_spoofer import LocalGridImageSpoofer
from src.data_providers.world_object_spoofer import WorldObjectSpoofer
import numpy.typing as npt

from src.utils.config import Config


class SimulatedAgent(AbstractAgent):
    """
    The goal of this method is to
    - provide a simulated agent
    """

    def __init__(self, cfg: Config, name: int = 0) -> None:
        super().__init__(cfg, name)
        self.lgs = LocalGridImageSpoofer(cfg)
        self.world_object_spoofer = WorldObjectSpoofer(cfg)

    def move_to_pos(self, pos: tuple[float, float]) -> None:
        self.teleport_to_pos(pos)

    def get_local_grid_img(self) -> npt.NDArray:
        return self.lgs.sim_spoof_local_grid_from_img_world(self.pos)

    def get_localization(self) -> tuple[float, float]:
        return self.pos

    def teleport_to_pos(self, pos: tuple[float, float]) -> None:
        """
        Teleport the agent to a new position.

        :param pos: the position of the agent
        :return: None
        """
        self.previous_pos = self.pos
        self.pos = pos
        self.steps_taken += 1

    def look_for_world_objects_in_perception_scene(self) -> list:
        w_os = self.world_object_spoofer.spoof_world_objects_from_position(self.pos)
        return w_os

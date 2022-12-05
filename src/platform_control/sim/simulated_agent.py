import numpy.typing as npt

from src.platform_control.abstract_agent import AbstractAgent
from src.platform_control.sim.utils.local_grid_image_spoofer import LocalGridImageSpoofer
from src.platform_control.sim.utils.world_object_spoofer import WorldObjectSpoofer


class SimulatedAgent(AbstractAgent):
    """provide a simulated agent"""

    def __post_init__(self) -> None:
        self.lg_spoofer = LocalGridImageSpoofer()
        self.world_object_spoofer = WorldObjectSpoofer()

    def _get_local_grid_img(self) -> npt.NDArray:
        spoofed_local_grid_img = self.lg_spoofer.sim_spoof_local_grid_from_img_world(self.pos)
        return spoofed_local_grid_img

    def get_localization(self) -> tuple[float, float]:
        return self.pos

    def _move_to_pos_implementation(
        self, target_pos: tuple[float, float], target_heading: float
    ):
        self.__teleport_to_pos(target_pos)

    def __teleport_to_pos(self, pos: tuple[float, float]) -> None:
        """
        Teleport the agent to a new position.

        :param pos: the position of the agent
        :return: None
        """
        self.pos = pos  # teleport

    def look_for_world_objects_in_perception_scene(self) -> list:
        w_os = self.world_object_spoofer.spoof_world_objects_from_position(self.pos)
        return w_os

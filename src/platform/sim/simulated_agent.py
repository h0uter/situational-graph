from src.platform.abstract_agent import AbstractAgent
from src.platform.sim.local_grid_image_spoofer import LocalGridImageSpoofer
from src.platform.sim.world_object_spoofer import WorldObjectSpoofer
import numpy.typing as npt
from src.shared.capabilities import Capabilities


class SimulatedAgent(AbstractAgent):
    """provide a simulated agent"""

    def __init__(
        self, capabilities: set[Capabilities] = set(), name_idx: int = 0
    ) -> None:
        super().__init__(capabilities, name_idx)
        self.lg_spoofer = LocalGridImageSpoofer()
        self.world_object_spoofer = WorldObjectSpoofer()

    def _get_local_grid_img(self) -> npt.NDArray:
        return self.lg_spoofer.sim_spoof_local_grid_from_img_world(self.pos)

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

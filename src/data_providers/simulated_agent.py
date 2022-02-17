from src.data_providers.local_grid_image_spoofer import LocalGridImageSpoofer
from src.entities.abstract_agent import AbstractAgent
from src.utils.config import Config
import numpy.typing as npt


class SimulatedAgent(AbstractAgent):
    """
    The goal of this method is to
    - provide a simulated agent
    """

    def __init__(self, start_pos: tuple[float, float], cfg: Config, name: int = 0) -> None:
        super().__init__(start_pos, name=name)
        self.lgs = LocalGridImageSpoofer(cfg)
        # self.pos = start_pos

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
        

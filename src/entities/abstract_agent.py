from abc import ABC, abstractmethod
import numpy.typing as npt
import numpy as np
import logging

from src.utils.config import Config
from src.entities.krm import KRM
from src.utils.my_types import Node, NodeType


class AbstractAgent(ABC):
    """"This is the base agent class. The program does not know if it runs a simulated agent or a real one."""

    @abstractmethod
    def __init__(self, cfg: Config, name: int = 0) -> None:
        self.name = name
        self.cfg = cfg

        self.at_wp: Node
        self.pos = cfg.AGENT_START_POS
        self.heading = 0.0
        self.previous_pos = self.pos

        self.steps_taken: int = 0
        self._log = logging.getLogger(__name__)

    @abstractmethod
    def move_to_pos(self, pos: tuple) -> None:
        """
        Move the agent to a new position.

        :param pos: the position of the agent
        :return: None
        """
        pass

    @abstractmethod
    def get_local_grid_img(self) -> npt.NDArray:
        """
        Return the local grid image around the agent.

        :return: The local grid image.
        """
        pass

    @abstractmethod
    def get_localization(self) -> tuple:
        pass

    @abstractmethod
    def look_for_world_objects_in_perception_scene(self) -> list:
        """
        Look for world objects in the perception scene.

        :return: The world objects in the perception scene.
        """
        pass

    # perhaps something like this should go into robot services, to not murk the dependencies.
    def localize_to_waypoint(self, krm: KRM):
        loc_candidates = krm.get_nodes_of_type_in_margin(
            self.get_localization(), self.cfg.AT_WP_MARGIN, NodeType.WAYPOINT
        )

        if len(loc_candidates) == 0:
            self._log.warning(f"{self.name}: could not find a waypoint in the margin")
            # self.at_wp = None
        elif len(loc_candidates) == 1:
            self.at_wp = loc_candidates[0]

        elif len(loc_candidates) > 1:
            self._log.warning(
                f"{self.name}: found multiple waypoints in the margin, picking the first one"
            )
            self.at_wp = loc_candidates[0]

        assert self.at_wp is not None, "self.at_wp is None"

    def calc_heading_to_target(self, target_pos: tuple) -> float:
        """
        Calculate the heading to the target.

        :param target_pos: The target position.
        :return: The heading to the target in radians.
        """
        p1 = target_pos
        p2 = self.pos
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        ang = np.arctan2(dy, dx)
        heading = (ang) % (2 * np.pi)
        
        return heading

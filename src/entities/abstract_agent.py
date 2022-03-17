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
        self.prev_wp: Node
        self.pos = cfg.AGENT_START_POS
        self.heading = 0.0
        self.previous_pos = self.pos
        self.init = False
        self.assigned_victim = None

        self.steps_taken: int = 0
        self._log = logging.getLogger(__name__)

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

    @abstractmethod
    def move_to_pos_implementation(self, target_pos: tuple, target_heading: float):
        """
        Move the agent to a new position.

        :param pos: the position of the agent
        :return: None
        """
        pass

    # TODO: this should return a succes/ failure bool
    def move_to_pos(self, target_pos: tuple, heading=None) -> None:
        if not heading:
            target_heading = self.calc_heading_to_target(target_pos)
        else:
            target_heading = heading

        # self.previous_pos = self.pos
        # BUG: previous_pos never changes
        self.previous_pos = self.get_localization()
        print(f"self previous pos: {self.previous_pos}")

        self.move_to_pos_implementation(target_pos, target_heading)

        # TODO: check if we arrived to set prev_wp
        actual_pos = self.get_localization()
        print(f"actual pos: {actual_pos}")

        # this is to prevent the prev pos being messed up by a failed explore action
        if (
            abs(target_pos[0] - actual_pos[0]) <= self.cfg.ARRIVAL_MARGIN
            and abs(target_pos[1] - actual_pos[1]) <= self.cfg.ARRIVAL_MARGIN
        ):
            # SUCCESS
            self.prev_wp = self.at_wp
            # BUG: need to set self.pos for real agent.... do I need to?
            self.steps_taken += 1
            self.heading = target_heading
            self.pos = actual_pos

        else:
            # FAILURE
            self.move_to_pos_implementation(self.previous_pos, self.heading)
            # self.previous_pos = self.get_localization()  # can also put this in the condition
            self.pos = self.get_localization()  # dont make sense for sim agent.

    # perhaps something like this should go into robot services, to not murk the dependencies.
    def localize_to_waypoint(self, krm: KRM):
        loc_candidates = krm.get_nodes_of_type_in_margin(
            self.get_localization(), self.cfg.AT_WP_MARGIN, NodeType.WAYPOINT
        )

        if len(loc_candidates) == 0:
            self._log.error(
                f"{self.name}: could not find a waypoint in the margin to localize to"
            )
            # self.at_wp = None
        elif len(loc_candidates) == 1:
            self.at_wp = loc_candidates[0]

        elif len(loc_candidates) > 1:
            self._log.warning(
                f"{self.name}: found multiple waypoints in the margin {loc_candidates}, picking the first one ({loc_candidates[0]}) for localization"
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
        p2 = self.get_localization()
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        ang = np.arctan2(dy, dx)
        heading = (ang) % (2 * np.pi)

        return heading

    def set_init(self):
        self.init = True

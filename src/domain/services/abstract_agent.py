import logging
from abc import ABC, abstractmethod
from typing import Optional, Sequence

import numpy as np
import numpy.typing as npt
from src.configuration.config import Config
from src.domain import TOSG, Node, ObjectTypes, Plan, Task
from src.domain.entities.local_grid import LocalGrid
from src.domain.entities.world_object import WorldObject
from src.entrypoints.utils.event import post_event


class AbstractAgent(ABC):
    """ "This is the base agent class. The program does not know if it runs a simulated agent or a real one."""

    @abstractmethod
    def __init__(self, cfg: Config, name_idx: int = 0) -> None:
        self.name = name_idx
        self.cfg = cfg

        self.at_wp: Node
        self.prev_wp: Node
        self.pos = cfg.AGENT_START_POS
        self.heading = 0.0
        self.previous_pos = self.pos
        self.init_explore_step_completed = (
            False  # HACK: this is there to kickstart the exploration with a selfloop
        )

        self.task: Optional[Task] = None
        self.plan: Optional[Plan] = None

        self.steps_taken = 0
        self.algo_iterations = 0
        self._log = logging.getLogger(__name__)

    @property
    def target_node(self) -> Optional[Node]:
        if len(self.plan) >= 1:
            return self.plan[-1][1]
        else:
            self.plan.invalidate()
            return None

    def get_local_grid(self) -> LocalGrid:
        lg_img = self._get_local_grid_img()
        # save_something(lg_img, "lg_img")
        lg = LocalGrid(
            world_pos=self.get_localization(),
            img_data=lg_img,
            cfg=self.cfg,
        )
        post_event("new lg", lg)

        return lg

    @abstractmethod
    def _get_local_grid_img(self) -> npt.NDArray:
        """
        Return the local grid image around the agent.

        :return: The local grid image.
        """
        pass

    @abstractmethod
    def get_localization(self) -> tuple:
        pass

    @abstractmethod
    def look_for_world_objects_in_perception_scene(self) -> Sequence[WorldObject]:
        """
        Look for world objects in the perception scene.

        :return: The world objects in the perception scene.
        """
        pass

    @abstractmethod
    def _move_to_pos_implementation(self, target_pos: tuple, target_heading: float):
        """
        Move the agent to a new position.

        :param pos: the position of the agent
        :return: None
        """
        pass

    # TODO: this should return a succes/ failure bool
    def move_to_pos(self, target_pos: tuple, heading=None) -> bool:
        if not heading:
            target_heading = self.calc_heading_to_target(target_pos)
        else:
            target_heading = heading

        # self.previous_pos = self.pos
        # BUG: previous_pos never changes
        self.previous_pos = self.get_localization()
        # print(f"self previous pos: {self.previous_pos}")

        self._move_to_pos_implementation(target_pos, target_heading)

        # TODO: check if we arrived to set prev_wp
        actual_pos = self.get_localization()
        # print(f"actual pos: {actual_pos}")

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
            return True

        else:
            # FAILURE
            self._move_to_pos_implementation(self.previous_pos, self.heading)
            # self.previous_pos = self.get_localization()  # can also put this in the condition
            self.pos = self.get_localization()  # dont make sense for sim agent.
            return False

    # perhaps something like this should go into robot services, to not murk the dependencies.
    def localize_to_waypoint(self, krm: TOSG):
        loc_candidates = krm.get_nodes_of_type_in_margin(
            self.get_localization(), self.cfg.AT_WP_MARGIN, ObjectTypes.WAYPOINT
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

    def set_init_explore_step(self):
        self.init_explore_step_completed = True

    def clear_task(self):
        self.task = None

    def clear_plan(self):
        self.plan = None
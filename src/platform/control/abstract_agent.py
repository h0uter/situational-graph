import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Sequence

import numpy as np
import numpy.typing as npt

from src.config import cfg
from src.platform.autonomy.plan_model import PlanModel
from src.platform.state.local_grid import LocalGrid
from src.shared.node_and_edge import Node
from src.shared.task import Task
from src.shared.world_object import WorldObject


class AbstractAgent(ABC):
    """ "This is the base agent class. The program does not know if it runs a simulated agent or a real one."""

    def __init__(self, capabilities: set[Enum] = set(), name_idx: int = 0) -> None:
        self.capabilities = capabilities
        self.name = name_idx

        self.at_wp: Node
        self.prev_wp: Node
        self.pos = cfg.AGENT_START_POS
        self.heading = 0.0
        self.previous_pos = self.pos
        self.init_explore_step_completed = (
            False  # HACK: this is there to kickstart the exploration with a selfloop
        )

        self.task: Optional[Task] = None
        self.plan: Optional[PlanModel] = None

        self.steps_taken = 0
        self.algo_iterations = 0
        self._log = logging.getLogger(__name__)

        self.__post_init__()

    @abstractmethod
    def __post_init__(self) -> None:
        pass

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
            xy=self.get_localization(),
            img_data=lg_img,
        )

        return lg

    @abstractmethod
    def _get_local_grid_img(self) -> npt.NDArray:
        pass

    @abstractmethod
    def get_localization(self) -> tuple[float, float]:
        pass

    @abstractmethod
    def look_for_world_objects_in_perception_scene(self) -> Sequence[WorldObject]:
        pass

    @abstractmethod
    def _move_to_pos_implementation(
        self, target_pos: tuple[float, float], target_heading: float
    ):
        pass

    # TODO: this should return a succes/ failure bool
    def move_to_pos(
        self, target_pos: tuple[float, float], heading: float = None
    ) -> bool:
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
            abs(target_pos[0] - actual_pos[0]) <= cfg.ARRIVAL_MARGIN
            and abs(target_pos[1] - actual_pos[1]) <= cfg.ARRIVAL_MARGIN
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

    def calc_heading_to_target(self, target_pos: tuple[float, float]) -> float:
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

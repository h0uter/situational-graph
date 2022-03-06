from abc import ABC, abstractmethod
import numpy.typing as npt
import logging

from src.utils.config import Config
from src.utils.my_types import NodeType
from src.entities.knowledge_roadmap import KnowledgeRoadmap


class AbstractAgent(ABC):
    @abstractmethod
    def __init__(self, cfg: Config, name: int = 0) -> None:
        self.name = name
        self.at_wp = None
        self.pos = cfg.AGENT_START_POS
        self.previous_pos = self.pos
        self.cfg = cfg

        self.steps_taken = 0
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
    def localize_to_node(self, krm: KnowledgeRoadmap):
        loc_candidates = krm.get_nodes_of_type_in_margin(
            self.get_localization(), self.cfg.AT_WP_MARGIN, NodeType.WAYPOINT
        )

        if len(loc_candidates) == 0:
            self._log.warning(f"{self.name}: could not find a waypoint in the margin")
            return None
        elif len(loc_candidates) == 1:
            self.at_wp = loc_candidates[0]

        elif len(loc_candidates) > 1:
            self._log.warning(
                f"{self.name}: found multiple waypoints in the margin, picking the first one"
            )
            self.at_wp = loc_candidates[0]

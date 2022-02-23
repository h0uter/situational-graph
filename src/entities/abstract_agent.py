from abc import ABC, abstractmethod
import numpy.typing as npt


class AbstractAgent(ABC):
    @abstractmethod
    def __init__(self, start_pos: tuple[float, float], name: int = 0) -> None:
        # TODO: remove as much as possible
        self.name = name
        self.at_wp = name
        self.pos = start_pos
        self.previous_pos = self.pos

        # FIXME: this should not be in the agent
        self.steps_taken = 0

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

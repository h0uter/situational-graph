from abc import ABC, abstractmethod
from src.utils.config import Config

import logging


class AbstractAction(ABC):
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._log = logging.getLogger(__name__)

    @abstractmethod
    def run(self, agent, krm, action_path) -> list:
        # Execute a single action edge of the action path.
        # and return the remaining action_path.
        pass

from src.entities.abstract_agent import AbstractAgent
from src.entities.krm import KRM
from src.usecases.sar_mission import SARMission
from src.utils.config import Config


# TODO: currently this usecase is redundant with the abstract strategy
class ExplorationUsecase:
    def __init__(self, cfg: Config) -> None:
        self.exploration_strategy = SARMission(cfg)

    def run_usecase_step(self, agent: AbstractAgent, krm: KRM) -> bool:
        return self.exploration_strategy.main_loop(agent, krm)

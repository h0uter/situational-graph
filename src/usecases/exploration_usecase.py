from src.entities.abstract_agent import AbstractAgent
from src.entities.krm import KRM
# from src.usecases.archive.frontier_based_exploration_strategy import FrontierBasedExplorationStrategy
# from src.usecases.archive.sar_strategy import SARStrategy
from src.usecases.sar_mission import SARMission
from src.utils.config import Config


# TODO: currently this usecase is redundant with the abstract strategy
class ExplorationUsecase:
    def __init__(self, cfg: Config) -> None:
        # self.exploration_strategy = FrontierBasedExplorationStrategy(cfg)
        # self.exploration_strategy = SARStrategy(cfg)
        self.exploration_strategy = SARMission(cfg)

    def run_usecase_step(self, agent: AbstractAgent, krm: KRM) -> bool:
        return self.exploration_strategy.main_loop(agent, krm)

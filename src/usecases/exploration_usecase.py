from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.usecases.frontier_based_exploration_strategy import FrontierBasedExplorationStrategy
from src.usecases.sar_strategy import SARStrategy
from src.usecases.decomposed_sar_strategy import DecomposedSARStrategy
from src.utils.config import Config


# TODO: currently this usecase is redundant with the abstract strategy
class ExplorationUsecase:
    def __init__(self, cfg: Config) -> None:
        # self.exploration_strategy = FrontierBasedExplorationStrategy(cfg)
        # self.exploration_strategy = SARStrategy(cfg)
        self.exploration_strategy = DecomposedSARStrategy(cfg)

    def run_usecase_step(self, agent: AbstractAgent, krm: KnowledgeRoadmap) -> bool:
        return self.exploration_strategy.run_exploration_step(agent, krm)

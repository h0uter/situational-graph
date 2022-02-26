from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.usecases.frontier_based_exploration_strategy import FrontierBasedExplorationStrategy
from src.usecases.frontier_based_exploration_strategy2 import FrontierBasedExplorationStrategy2
from src.utils.config import Config


class ExplorationUsecase:
    def __init__(self, cfg: Config) -> None:
        # self.ExplorationStrategy = FrontierBasedExplorationStrategy(cfg)
        self.ExplorationStrategy = FrontierBasedExplorationStrategy2(cfg)

    def run_exploration_step(self, agent: AbstractAgent, krm: KnowledgeRoadmap):
        self.ExplorationStrategy.run_exploration_step(agent, krm)

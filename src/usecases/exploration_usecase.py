from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.usecases.frontier_based_exploration_strategy import FrontierBasedExplorationStrategy
from src.utils.config import Config


class ExplorationUsecase:
    def __init__(self, cfg: Config) -> None:
        self.ExplorationStrategy = FrontierBasedExplorationStrategy(cfg)

    def run_usecase_step(self, agent: AbstractAgent, krm: KnowledgeRoadmap) -> bool:
        _, _, completed = self.ExplorationStrategy.run_exploration_step(agent, krm)
        return completed

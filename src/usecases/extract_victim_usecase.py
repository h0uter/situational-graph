from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.abstract_agent import AbstractAgent

from src.usecases.frontier_based_exploration_strategy import FrontierBasedExplorationStrategy


class ExtractVictimUsecase():
    def __init__(self, cfg, extraction_endpoint_node=0):
        self.cfg = cfg
        self.extraction_endpoint_node = extraction_endpoint_node
        self.path = []
        self.completed = False

    def run_usecase_step(self, agent: AbstractAgent, krm: KnowledgeRoadmap) -> bool:

        if not self.path:
            self.path = krm.shortest_path(agent.at_wp, self.extraction_endpoint_node)

        if self.path:
            # HACK: fix dependencies
            hack_yolo = FrontierBasedExplorationStrategy(self.cfg)
            self.path = hack_yolo.path_execution(agent, krm, self.path)
            if not self.path:
                self.completed = True
                return True

        return False

from src.data_providers.local_grid_image_spoofer import LocalGridImageSpoofer
from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap


class ViewModel:
    def __init__(self, agent: AbstractAgent, krm: KnowledgeRoadmap, lg: LocalGridImageSpoofer) -> None:
        self.agent = agent
        self.krm = krm
        self.lg = lg

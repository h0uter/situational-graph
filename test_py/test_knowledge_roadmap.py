from src.entities.knowledge_roadmap import KnowledgeRoadmap

def test_get_node_by_pos():
    KRM = KnowledgeRoadmap([(55, 55)])
    assert 0 == KRM.get_node_by_pos((55, 55))

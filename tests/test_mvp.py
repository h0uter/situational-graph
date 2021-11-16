import unittest
from thesis_mvp import create_complete_nav_graph
from knowledge_road_map import KnowledgeRoadmap  

def hello_world():
    return "Hello World!"

class TestMVP(unittest.TestCase):

    def test2(self):
        self.assertEqual(hello_world(), "Hello World!")    

    def test_graph_size(self):
        data = [[0, 0], [2, 2], [4, 2], [4, 4], [4, 6], [2, 6], [2, 8],
            [2, 10], [4, 10], [6, 12], [8, 12], [10, 14], [12, 14]]

        graph = create_complete_nav_graph(data)
        self.assertEqual(len(graph), len(data))

    def test_get_node_by_pos(self):
        KRM = KnowledgeRoadmap((55, 55))
        
        self.assertEqual(0, KRM.get_node_by_pos((55, 55)))


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

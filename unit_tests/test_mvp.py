# import unittest
# from src.entities.knowledge_road_map import KnowledgeRoadmap  
# from src.entities.agent import Agent
# from src.data_providers.manual_graph_world import ManualGraphWorld, LatticeWorld
# from src.usecases.exploration import Exploration

# import pickle

# def hello_world():
#     return "Hello World!"

# class TestMVP(unittest.TestCase):

#     def test2(self):
#         self.assertEqual(hello_world(), "Hello World!")    

#     def test_get_node_by_pos(self):
#         KRM = KnowledgeRoadmap((55, 55))
#         self.assertEqual(0, KRM.get_node_by_pos((55, 55)))

#     def test_exploration_steps_villa(self):
#         ''' This test checks whether the amount of steps neccesary to explore the world is correct'''
        
#         world = ManualGraphWorld()
#         agent = Agent(debug=False)
#         exploration_use_case = Exploration(agent)

#         while agent.no_more_frontiers == False:
#             exploration_use_case.run_exploration_step(world)

#         # 68 is the amount of steps for the graph world
#         self.assertEqual(68, agent.steps_taken)

#     def test_exploration_steps_1642083709(self):
#         ''' This test checks whether the amount of steps neccesary to explore the world is correct'''
        
#         world = pickle.load( open( "src/data_providers/test_world_graphs/1642083709.9957886_generated_world_graph.p", "rb" ) )
#         # world = ManualGraphWorld()
#         agent = Agent(debug=False)
#         exploration_use_case = Exploration(agent)

#         while agent.no_more_frontiers == False:
#             exploration_use_case.run_exploration_step(world)

#         # 280 is the amount of steps for the graph world
#         self.assertEqual(280, agent.steps_taken)

#     def test_exploration_steps_1642089098(self):
#         ''' This test checks whether the amount of steps neccesary to explore the world is correct'''
        
#         world = pickle.load( open( "src/data_providers/test_world_graphs/1642089098.4996877_generated_world_graph.p", "rb" ) )
#         # world = ManualGraphWorld()
#         agent = Agent(debug=False)
#         exploration_use_case = Exploration(agent)

#         while agent.no_more_frontiers == False:
#             exploration_use_case.run_exploration_step(world)

#         # 280 is the amount of steps for the graph world
#         self.assertEqual(291, agent.steps_taken)

#     def test_graph_generator(self):
#         ''' this test checks whether the distance between nodes is always 4 meters.'''
#         pass

# if __name__ == '__main__':
#     unittest.main(argv=['first-arg-is-ignored'], exit=False)

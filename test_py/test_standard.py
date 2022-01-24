from knowledge_roadmap.entities.knowledge_road_map import KnowledgeRoadmap  
from knowledge_roadmap.entities.agent import Agent
from knowledge_roadmap.data_providers.manual_graph_world import ManualGraphWorld, LatticeWorld
from knowledge_roadmap.usecases.exploration import Exploration

from thesis_demos import exploration_with_sampling_viz

import pickle

def hello_world():
    return "Hello World!"

def test_2():
    assert hello_world() == "Hello World!"

def test_get_node_by_pos():
    KRM = KnowledgeRoadmap((55, 55))
    assert 0 == KRM.get_node_by_pos((55, 55))


def test_sampling_exploration_completion():
    assert True == exploration_with_sampling_viz(True)
    
# def 



# def test_exploration_steps_villa():
#     ''' This test checks whether the amount of steps neccesary to explore the world is correct'''
    
#     world = ManualGraphWorld()
#     agent = Agent(debug=False)
#     exploration_use_case = Exploration(agent)

#     while agent.no_more_frontiers == False:
#         exploration_use_case.run_exploration_step(world)

#     # 68 is the amount of steps for the graph world
#     assert 68 == agent.steps_taken

# def exploration_steps_on_graph(graph_name):
#     ''' This test checks whether the amount of steps neccesary to explore the world is correct'''
#     world = pickle.load( open( f"knowledge_roadmap/data_providers/test_world_graphs/{graph_name}_generated_world_graph.p", "rb" ) )
#     # world = ManualGraphWorld()
#     agent = Agent(debug=False)
#     exploration_use_case = Exploration(agent)

#     while agent.no_more_frontiers == False:
#         exploration_use_case.run_exploration_step(world)

#     return agent.steps_taken

# def test_exploration_steps_on_graph_a():
#     assert 291 == exploration_steps_on_graph("a")

# def test_exploration_steps_on_graph_b():
#     assert 288 == exploration_steps_on_graph("b")


import networkx as nx
from networkx.drawing.nx_pylab import draw
import matplotlib.pyplot as plt

from src.entities.knowledge_road_map import KnowledgeRoadmap
from src.entities.agent import Agent
from src.data_providers.world import *
from src.entrypoints.GUI import GUI
from src.usecases.exploration import Exploration

############################################################################################
# DEMONSTRATIONS
############################################################################################

def demo_instant_graph_from_waypoints(wp_data):
    ''' This demo instantly creates a graph from a list of waypoints'''
    KRM = KnowledgeRoadmap()

    KRM.init_plot()

    KRM.add_waypoints(wp_data)
    KRM.draw_current_krm() 
    plt.ioff()
    plt.show()

def demo_online_graph(wp_data):
    ''' 
    This demo creates and visualises a graph online 
    from an array of waypoint data
    '''
    KRM = KnowledgeRoadmap()
    KRM.init_plot()
    for wp in wp_data:
        KRM.add_waypoint(wp)
        KRM.draw_current_krm()

    plt.ioff()
    plt.show()

def demo_with_agent_drawn(wp_data):
    ''' 
    This demo creates and visualises a graph online 
    from an array of waypoint data
    '''
    agent = Agent()
    KRM = KnowledgeRoadmap((0, 0))
    KRM.init_plot()

    for wp in wp_data:
        KRM.add_waypoint(wp)
        agent.draw_agent(wp)
        KRM.draw_current_krm()

    plt.ioff()
    plt.show()

def demo_agent_driven():
    ''' This is the first demo where the agent takes actions to explore a world'''
    world = ManualGraphWorld()
    # world = LatticeWorld()
    gui = GUI()
    # gui.draw_world(world.world)
    agent = Agent(debug=False)
    exploration = Exploration(agent)
    # gui.run_and_vizualize_exploration(exploration, world)

    exploration.explore(world)
    # agent.explore_stepwise(world)
    # agent.explore(world)

    plt.ioff()
    plt.show()


def pure_exploration_usecase():

    world = ManualGraphWorld()
    gui = GUI()
    # gui.draw_world(world.world)
    agent = Agent(debug=False)
    exploration_use_case = Exploration(agent)

    # exploration_use_case.explore2(world)

    stepwise = False
    gui.init_plot(agent, agent.krm)
    while agent.no_more_frontiers == False:
        if not stepwise:
            exploration_use_case.run_exploration_step(world)

            # FIXME: this is the entrpoint for the gui
            gui.viz_krm(agent, agent.krm) # TODO: make the KRM independent of the agent
            # self.agent.krm.draw_current_krm()  # illustrate krm with new frontiers
            # agent.draw_agent(agent.pos)  # draw the agent on the world
            gui.draw_agent(agent.pos)
            plt.pause(0.05)
        # elif stepwise:
        #     # BUG:: matplotlib crashes after 10 sec if we block the execution like this.
        #     self.keypress = keyboard.read_key()
        #     if self.keypress:
        #         self.keypress = False
        #         self.exploration_procedure(world)

        # FIXME: this should be done using the GUI
    # self.agent.krm.draw_current_krm() # 


    plt.ioff()
    plt.show()

if __name__ == '__main__':

    # TODO: generalize this to a "sensor data stream" which is then processed by the agent.
    # outputs will be world objects and waypoints
    # TODO: how to emulate the sampling of frontier nodes?
    # world = GraphWorld()

    # demo_with_agent_drawn(world.structure)
    # demo_instant_graph_from_waypoints(wp_data)
    # demo_agent_driven()
    pure_exploration_usecase()
    # world = GraphWorldExperiment()
    
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import networkx as nx
import numpy as np

from knowledge_roadmap.entities.knowledge_road_map import KnowledgeRoadmap
from knowledge_roadmap.entities.agent import Agent
from knowledge_roadmap.entities.local_grid import LocalGrid


import matplotlib
matplotlib.use("Qt5agg")


class GUI():

    ''' 
    The goal of this class is to 
    - hanlle all visualizations, so that the logic can be tested headless.
    - take user input later on
    '''

    def __init__(self,  origin_x_offset, origin_y_offset ,map_img=None,) -> None:
        self.agent_drawing = None
        self.local_grid_drawing = None
        self.map_img = map_img
        self.initialized = False

        # FIXME: this has to be linked to the x_map_length_scale and y offset in the gui
        self.origin_x_offset = origin_x_offset
        # self.origin_x_offset = 17/2
        self.origin_y_offset = origin_y_offset
        # self.origin_y_offset = 13/2

    def draw_agent(self, pos: tuple, rec_len=7) -> None:
        '''
        Draw the agent on the world.
        
        :param pos: the position of the agent
        :param rec_len: the length of the rectangle that will be drawn around the agent, defaults to 7
        (optional)
        :return: None
        '''
        if self.agent_drawing != None:
            self.agent_drawing.remove()
        if self.local_grid_drawing != None:
            self.local_grid_drawing.remove()
        # self.agent_drawing = plt1.arrow(
        #     pos[0], pos[1], 0.3, 0.3, width=0.4, color='blue') # One day the agent will have direction
        self.agent_drawing = self.ax1.add_patch(plt.Circle(
            (pos[0], pos[1]), 1.2, fc='blue'))
        
        self.local_grid_drawing = self.ax1.add_patch(plt.Rectangle(
            (pos[0]-0.5*rec_len, pos[1]-0.5*rec_len), rec_len, rec_len, alpha=0.2, fc='blue'))

    def draw_local_grid(self, local_grid_img: list) -> None:
        '''
        Draw the local grid in the right axes.
        
        :param local_grid_img: the local grid image
        :return: None
        '''
        if not self.initialized:
            self.fig, (self.ax1, self.ax2) = plt.subplots(1,2, figsize=(15, 10), num=1)
            self.initialized = True
 
        self.ax2.cla()
        self.ax2.imshow(local_grid_img, origin='lower')
        self.ax2.set_aspect('equal', 'box')  # set the aspect ratio of the plot
        self.ax2.set_title('local grid')

    def preview_graph_world(self, world:object) -> None:
        '''This function is used to preview the underlying graph used as a simplified world to sample from.'''
        fig, ax = plt.subplots(figsize=(10, 10))

        if self.map_img is not None:
            ax.imshow(
                self.map_img, 
                extent=[-self.origin_x_offset, self.origin_x_offset, -self.origin_y_offset, self.origin_y_offset], 
                origin='lower')
            ax.set_xlim([-self.origin_x_offset, self.origin_x_offset])
            ax.set_ylim([-self.origin_y_offset, self.origin_y_offset])
        else:
            ax.set_xlim([-100, 100])
            ax.set_ylim([-100, 100])

        ax.set_xlabel('x', size=10)
        ax.set_ylabel('y', size=10)

        nx.draw_networkx_nodes(
                                world.graph, 
                                pos=nx.get_node_attributes(world.graph, 'pos'),
                                ax=ax, 
                                node_color='grey',
                                node_size=100)
        nx.draw_networkx_edges(
                                world.graph, 
                                pos=nx.get_node_attributes(world.graph, 'pos'), 
                                ax=ax, 
                                edge_color='grey')

        nx.draw_networkx_labels(
                                world.graph, 
                                pos=nx.get_node_attributes(world.graph, 'pos'), 
                                ax=ax, 
                                font_size=7)

        plt.axis('on')
        ax.tick_params(left=True, 
                            bottom=True,
                            labelleft=True, 
                            labelbottom=True)
        plt.show()

    def viz_krm(self, krm: KnowledgeRoadmap) -> None:
        '''
        Draws the current Knowledge Roadmap Graph.
        
        :param agent: the agent object
        :param krm: the Knowledge Roadmap object
        :return: None
        '''
        if not self.initialized:
            self.fig, (self.ax1, self.ax2) = plt.subplots(1,2, figsize=(15, 10), num=1)
            self.initialized = True

        # plt.figure(1)
        self.ax1.cla() # XXX: plt1.cla is the bottleneck in my performance.

        self.ax1.set_title('Online Construction of Knowledge Roadmap')
        self.ax1.set_xlabel('x', size=10)
        self.ax1.set_ylabel('y', size=10)

        if self.map_img  is not None:
            self.ax1.imshow(
                self.map_img, 
                extent=[-self.origin_x_offset, self.origin_x_offset, -self.origin_y_offset, self.origin_y_offset], 
                origin='lower',
                alpha=0.5
                )
        else:
            self.ax1.set_xlim([-70, 70])
            self.ax1.set_ylim([-70, 70])

        pos = nx.get_node_attributes(krm.graph, 'pos') # TODO: unclear variable name
        # filter the nodes and edges based on their type
        waypoint_nodes = dict((n, d['type'])
                                for n, d in krm.graph.nodes().items() if d['type'] == 'waypoint')
        frontier_nodes = dict((n, d['type'])
                                for n, d in krm.graph.nodes().items() if d['type'] == 'frontier')
        world_object_nodes = dict((n, d['type'])
                                for n, d in krm.graph.nodes().items() if d['type'] == 'world_object')

        world_object_edges = dict((e, d['type'])
                                for e, d in krm.graph.edges().items() if d['type'] == 'world_object_edge')
        waypoint_edges = dict((e, d['type'])
                                for e, d in krm.graph.edges().items() if d['type'] == 'waypoint_edge')
        frontier_edges = dict((e, d['type'])
                                for e, d in krm.graph.edges().items() if d['type'] == 'frontier_edge')

        '''draw the nodes, edges and labels separately'''
        nx.draw_networkx_nodes(
                                krm.graph, 
                                pos, 
                                nodelist=world_object_nodes.keys(),
                                ax=self.ax1, 
                                node_color='violet',
                                node_size=575
        )
        nx.draw_networkx_nodes(
                                krm.graph, 
                                pos, 
                                nodelist=frontier_nodes.keys(),
                                ax=self.ax1, 
                                node_color='green',
                                node_size=350
                                
        )
        nx.draw_networkx_nodes(
                                krm.graph, 
                                pos, 
                                nodelist=waypoint_nodes.keys(), 
                                ax=self.ax1, 
                                node_color='red', 
                                node_size=140
        )
        nx.draw_networkx_edges(
                                krm.graph, 
                                pos, 
                                ax=self.ax1, 
                                edgelist=waypoint_edges.keys(), 
                                edge_color='red'
        )
        nx.draw_networkx_edges(
                                krm.graph, 
                                pos, 
                                ax=self.ax1, 
                                edgelist=world_object_edges.keys(), 
                                edge_color='purple'
        )
        nx.draw_networkx_edges(
                                krm.graph, 
                                pos, 
                                ax=self.ax1, 
                                edgelist=frontier_edges.keys(), 
                                edge_color='green', 
                                width=4
        )

        nx.draw_networkx_labels(krm.graph, pos, ax=self.ax1, font_size=6)
        self.ax1.axis('on')  # turns on axis
        self.ax1.set_aspect('equal', 'box')  # set the aspect ratio of the plot
        self.ax1.tick_params(left=True, bottom=True,
                            labelleft=True, labelbottom=True)
        # self.fig.canvas.start_event_loop(0.001)


    def plot_unzoomed_world_coord(self, lg:LocalGrid) -> None:
        # # plt.figure(10)
        # # plt.cla()
        # # plt.ion()
        # print(plt.figure(1).get_axes()[0])

        # plt.imshow(self.data, origin='lower')
        print(f"world pos: {lg.world_pos} lg.length_in_m: {lg.length_in_m}")

        # TODO: emulate the local grid with this cmap alpha yada yada
        my_cmap = cm.jet
        my_cmap.set_under('k', alpha=0)

        # plt.imshow(
        self.ax1.imshow(
            lg.data, 
            origin='lower', 
            extent=[
                lg.world_pos[0]-lg.length_in_m/2, 
                lg.world_pos[0]+lg.length_in_m/2, 
                lg.world_pos[1]-lg.length_in_m/2, 
                lg.world_pos[1]+lg.length_in_m/2, 
            ],
            cmap=my_cmap, 
            interpolation='none', 
            clim=[0,0.5 ]
        )

        self.ax1.set_xlim([-self.origin_x_offset, self.origin_x_offset])
        self.ax1.set_ylim([-self.origin_y_offset, self.origin_y_offset])
        # plt.show()
        plt.pause(0.1)
        # plt.figure(1)




    def debug_logger(self,krm: KnowledgeRoadmap, agent: Agent) -> None:
        '''
        Prints debug statements.
        
        :return: None
        '''
        print("==============================")
        print(">>> " + nx.info(krm.graph))
        print(f">>> self.at_wp: {agent.at_wp}")
        print(f">>> movement: {agent.previous_pos} >>>>>> {agent.pos}")
        print(f">>> frontiers: {krm.get_all_frontiers_idxs()}")
        print("==============================")

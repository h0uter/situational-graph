import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
import networkx as nx
from PIL import Image
import streamlit as st


from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.simulated_agent import SimulatedAgent
from src.entities.abstract_agent import AbstractAgent
from src.entities.local_grid import LocalGrid
from src.utils.configuration import Configuration
from src.utils.coordinate_transforms import img_axes2world_axes


matplotlib.use("Qt5agg")


class Vizualizer:
    def __init__(self) -> None:
        self.agent_drawing = None
        self.local_grid_drawing = None
        self.initialized = False

        self.cfg = Configuration()
        self.origin_x_offset = self.cfg.TOTAL_MAP_LEN_M_X / 2
        self.origin_y_offset = self.cfg.TOTAL_MAP_LEN_M_Y / 2

        self.map_img = None
        if self.cfg.FULL_PATH:
            upside_down_map_img = Image.open(self.cfg.FULL_PATH)
            self.map_img = img_axes2world_axes(upside_down_map_img)

        self.streamlit_unit = None

    def init_fig(self):
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(
            2, 2, figsize=(10, 10), num=1
        )
        plt.ion()
        self.fig.tight_layout()
        self.initialized = True

    def draw_agent_and_sensor_range(self, pos: tuple, ax, rec_len=7) -> None:
        """
        Draw the agent on the world.
        
        :param pos: the position of the agent
        :param rec_len: the length of the rectangle that will be drawn around the agent, defaults to 7
        (optional)
        :return: None
        """
        # self.agent_drawing = plt1.arrow(
        #     pos[0], pos[1], 0.3, 0.3, width=0.4, color='blue') # One day the agent will have direction
        self.agent_drawing = ax.add_patch(plt.Circle((pos[0], pos[1]), 1.2, fc="blue"))

        self.local_grid_drawing = ax.add_patch(
            plt.Rectangle(
                (pos[0] - 0.5 * rec_len, pos[1] - 0.5 * rec_len),
                rec_len,
                rec_len,
                alpha=0.2,
                fc="blue",
            )
        )

    def vizualize_lg(self, lg: LocalGrid) -> None:
        """
        Draw the local grid on the right side of the figure
        
        :param lg: LocalGrid
        :type lg: LocalGrid
        """
        if not self.initialized:
            self.init_fig()

        # self.ax2.cla()
        self.ax2.imshow(lg.data, origin="lower")
        plt.plot(
            lg.data.shape[1] / 2,
            lg.data.shape[0] / 2,
            marker="o",
            markersize=10,
            color="red",
        )
        self.ax2.set_aspect("equal", "box")  # set the aspect ratio of the plot
        self.ax2.set_title("local grid")

    def draw_krm_graph(self, krm, ax):
        positions_of_all_nodes = nx.get_node_attributes(krm.graph, "pos")
        # filter the nodes and edges based on their type
        waypoint_nodes = dict(
            (n, d["type"])
            for n, d in krm.graph.nodes().items()
            if d["type"] == "waypoint"
        )
        frontier_nodes = dict(
            (n, d["type"])
            for n, d in krm.graph.nodes().items()
            if d["type"] == "frontier"
        )
        world_object_nodes = dict(
            (n, d["type"])
            for n, d in krm.graph.nodes().items()
            if d["type"] == "world_object"
        )
        world_object_edges = dict(
            (e, d["type"])
            for e, d in krm.graph.edges().items()
            if d["type"] == "world_object_edge"
        )
        waypoint_edges = dict(
            (e, d["type"])
            for e, d in krm.graph.edges().items()
            if d["type"] == "waypoint_edge"
        )
        frontier_edges = dict(
            (e, d["type"])
            for e, d in krm.graph.edges().items()
            if d["type"] == "frontier_edge"
        )

        """draw the nodes, edges and labels separately"""
        nx.draw_networkx_nodes(
            krm.graph,
            positions_of_all_nodes,
            nodelist=world_object_nodes.keys(),
            ax=ax,
            node_color="violet",
            node_size=575,
        )
        nx.draw_networkx_nodes(
            krm.graph,
            positions_of_all_nodes,
            nodelist=frontier_nodes.keys(),
            ax=ax,
            node_color="green",
            node_size=250,
        )
        nx.draw_networkx_nodes(
            krm.graph,
            positions_of_all_nodes,
            nodelist=waypoint_nodes.keys(),
            ax=ax,
            node_color="red",
            node_size=100,
        )
        nx.draw_networkx_edges(
            krm.graph,
            positions_of_all_nodes,
            ax=ax,
            edgelist=waypoint_edges.keys(),
            edge_color="red",
        )
        nx.draw_networkx_edges(
            krm.graph,
            positions_of_all_nodes,
            ax=ax,
            edgelist=world_object_edges.keys(),
            edge_color="purple",
        )
        nx.draw_networkx_edges(
            krm.graph,
            positions_of_all_nodes,
            ax=ax,
            edgelist=frontier_edges.keys(),
            edge_color="green",
            width=4,
        )

        nx.draw_networkx_labels(krm.graph, positions_of_all_nodes, ax=ax, font_size=6)

    def viz_krm_no_floorplan(self, krm: KnowledgeRoadmap, agent: AbstractAgent) -> None:
        """
        Draw the agent's perspective on the world, like RViz.
        
        :param krm: KnowledgeRoadmap
        :param agent: Agent
        :return: None
        """
        if not self.initialized:
            self.init_fig()

        self.ax1.cla()  # XXX: plt1.cla is the bottleneck in my performance.

        self.ax1.set_title("Online Construction of Knowledge Roadmap (RViz)")
        self.ax1.set_xlabel("x", size=10)
        self.ax1.set_ylabel("y", size=10)

        self.draw_krm_graph(krm, self.ax1)

        self.ax1.axis("on")  # turns on axis
        self.ax1.set_aspect("equal", "box")  # set the aspect ratio of the plot
        self.ax1.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

    def viz_krm_on_floorplan(self, krm: KnowledgeRoadmap) -> None:
        """ Like Gazebo """

        if not self.initialized:
            self.init_fig()

        self.ax2.cla()  # XXX: plt1.cla is the bottleneck in my performance.

        self.ax2.set_title("Groundtruth Knowledge Roadmap construction (Gazebo)")
        self.ax2.set_xlabel("x", size=10)
        self.ax2.set_ylabel("y", size=10)

        if self.map_img is not None:
            self.ax2.imshow(
                self.map_img,
                extent=[
                    -self.origin_x_offset,
                    self.origin_x_offset,
                    -self.origin_y_offset,
                    self.origin_y_offset,
                ],
                origin="lower",
                alpha=0.25,
            )
        else:
            self.ax2.set_xlim([-70, 70])
            self.ax2.set_ylim([-70, 70])

        self.draw_krm_graph(krm, self.ax2)
        self.ax2.axis("on")  # turns on axis
        self.ax2.set_aspect("equal", "box")  # set the aspect ratio of the plot
        self.ax2.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

    def draw_lg_unzoomed_in_world_coord(self, lg: LocalGrid) -> None:
        """
        It plots the local grid on the world map.
        
        :param lg: LocalGrid
        :type lg: LocalGrid
        """
        # TODO: emulate the local grid with this cmap alpha yada yada
        # my_cmap = cm.jet
        # my_cmap.set_under('k', alpha=0)

        self.ax2.imshow(
            lg.data,
            origin="lower",
            extent=[
                lg.world_pos[0] - lg.length_in_m / 2,
                lg.world_pos[0] + lg.length_in_m / 2,
                lg.world_pos[1] - lg.length_in_m / 2,
                lg.world_pos[1] + lg.length_in_m / 2,
            ],
            # cmap=my_cmap,
            interpolation="none",
            clim=[0, 0.5],
        )

        self.ax2.set_xlim([-self.origin_x_offset, self.origin_x_offset])
        self.ax2.set_ylim([-self.origin_y_offset, self.origin_y_offset])

    def draw_shortcut_collision_lines(
        self, lg: LocalGrid, krm: KnowledgeRoadmap
    ) -> None:

        if not self.initialized:
            self.init_fig()

        close_nodes = krm.get_nodes_of_type_in_margin(
            lg.world_pos, self.cfg.LG_LENGTH_IN_M / 2, "waypoint"
        )
        points = [krm.get_node_data_by_idx(node)["pos"] for node in close_nodes]

        if points:
            self.ax4.cla()

            self.ax4.set_title("Local grid sampling of shortcuts")
            self.ax4.imshow(
                lg.data,
                origin="lower",
                extent=[
                    lg.world_pos[0] - lg.length_in_m / 2,
                    lg.world_pos[0] + lg.length_in_m / 2,
                    lg.world_pos[1] - lg.length_in_m / 2,
                    lg.world_pos[1] + lg.length_in_m / 2,
                ],
            )
            for point in points:
                at_cell = lg.length_num_cells / 2, lg.length_num_cells / 2
                to_cell = lg.world_coords2cell_idxs(point)

                self.ax4.plot(
                    [lg.world_pos[0], point[0]],
                    [lg.world_pos[1], point[1]],
                    color="orange",
                )
                self.ax4.plot(
                    point[0], point[1], marker="o", markersize=10, color="red",
                )

                _, collision_point = lg.is_collision_free_straight_line_between_cells(
                    at_cell, to_cell
                )
                if collision_point:
                    self.ax4.plot(
                        collision_point[0],
                        collision_point[1],
                        marker="X",
                        color="red",
                        markersize=20,
                    )

            self.ax4.plot(
                lg.world_pos[0],
                lg.world_pos[1],
                marker="o",
                markersize=10,
                color="blue",
            )

    def figure_update(self, krm, agent, lg):
        self.draw_shortcut_collision_lines(lg, krm)

        self.viz_krm_on_floorplan(krm)
        self.draw_lg_unzoomed_in_world_coord(lg)
        self.draw_agent_and_sensor_range(
            agent.pos, self.ax2, rec_len=self.cfg.LG_LENGTH_IN_M
        )

        self.viz_krm_no_floorplan(krm, agent)
        self.draw_agent_and_sensor_range(
            agent.pos, self.ax1, rec_len=self.cfg.LG_LENGTH_IN_M
        )

        plt.pause(0.001)

    def debug_logger(self, krm: KnowledgeRoadmap, agent: AbstractAgent) -> None:
        """
        Prints debug statements.
        
        :return: None
        """
        print("==============================")
        print(">>> " + nx.info(krm.graph))
        print(f">>> self.at_wp: {agent.at_wp}")
        print(f">>> movement: {agent.previous_pos} >>>>>> {agent.pos}")
        print(f">>> frontiers: {krm.get_all_frontiers_idxs()}")
        print("==============================")

    def preview_graph_world(self, world) -> None:
        """This function is used to preview the underlying graph used as a simplified world to sample from."""
        fig, ax = plt.subplots(figsize=(10, 10))

        if self.map_img is not None:
            ax.imshow(
                self.map_img,
                extent=[
                    -self.origin_x_offset,
                    self.origin_x_offset,
                    -self.origin_y_offset,
                    self.origin_y_offset,
                ],
                origin="lower",
            )
            ax.set_xlim([-self.origin_x_offset, self.origin_x_offset])
            ax.set_ylim([-self.origin_y_offset, self.origin_y_offset])
        else:
            ax.set_xlim([-100, 100])
            ax.set_ylim([-100, 100])

        ax.set_xlabel("x", size=10)
        ax.set_ylabel("y", size=10)

        nx.draw_networkx_nodes(
            world.graph,
            pos=nx.get_node_attributes(world.graph, "pos"),
            ax=ax,
            node_color="grey",
            node_size=100,
        )
        nx.draw_networkx_edges(
            world.graph,
            pos=nx.get_node_attributes(world.graph, "pos"),
            ax=ax,
            edge_color="grey",
        )

        nx.draw_networkx_labels(
            world.graph,
            pos=nx.get_node_attributes(world.graph, "pos"),
            ax=ax,
            font_size=7,
        )

        plt.axis("on")
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        plt.show()

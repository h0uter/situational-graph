import networkx as nx
import uuid

from knowledge_roadmap.entities.agent import Agent
from knowledge_roadmap.entities.knowledge_roadmap import KnowledgeRoadmap
from knowledge_roadmap.entities.local_grid import LocalGrid
from config import Configuration

class ExplorationUsecase:
    def __init__(
        self,
        agent: Agent,
        len_of_map: float,
        lg_num_cells: int,
        lg_length_in_m,
        debug=False,
    ) -> None:
        self.agent = agent
        self.consumable_path = None
        self.selected_frontier_idx = None
        self.init = False
        self.debug = debug
        self.len_of_entire_map = len_of_map
        self.lg_num_cells = lg_num_cells
        self.lg_length_in_m = lg_length_in_m

        # Hyper parameters
        self.N_samples = Configuration().N_samples
        self.frontier_sample_radius_num_cells = self.lg_num_cells / 2

        # TODO: fix scaling
        self.prune_radius = Configuration().prune_radius
        # self.prune_radius = self.lg_length_scale * 0.25
        # self.shortcut_radius = 5

    ############################################################################################
    ### ENTRYPOINT FOR GUIDING EXPLORATION WITH SEMANTICS ###
    #############################################################################################
    def evaluate_frontiers(
        self, agent: Agent, frontier_idxs: list, krm: KnowledgeRoadmap
    ) -> int:
        """ 
        Evaluate the frontiers and return the best one.
        this is the entrypoint for exploiting semantics        
        """
        shortest_path_by_node_count = float("inf")
        selected_frontier_idx = None

        for frontier_idx in frontier_idxs:
            candidate_path = nx.shortest_path(
                krm.graph, source=agent.at_wp, target=frontier_idx
            )
            # choose the last shortest path among equals
            # if len(candidate_path) <= shortest_path_by_node_count:
            #  choose the first shortest path among equals
            if len(candidate_path) < shortest_path_by_node_count:
                shortest_path_by_node_count = len(candidate_path)
                selected_frontier_idx = candidate_path[-1]

        return selected_frontier_idx

    #############################################################################################

    def select_target_frontier(self, agent: Agent, krm: KnowledgeRoadmap) -> int:
        """ using the KRM, obtain the optimal frontier to visit next"""
        frontier_idxs = krm.get_all_frontiers_idxs()
        if len(frontier_idxs) > 0:
            target_frontier = self.evaluate_frontiers(agent, frontier_idxs, krm)

            return target_frontier
        else:
            agent.no_more_frontiers = True
            return None, None

    def find_path_to_selected_frontier(
        self, agent: Agent, target_frontier: int, krm: KnowledgeRoadmap
    ) -> list:
        """
        Find the shortest path from the current waypoint to the target frontier.

        :param target_frontier: the frontier that we want to reach
        :return: The path to the selected frontier.
        """
        path = nx.shortest_path(krm.graph, source=agent.at_wp, target=target_frontier)
        return path

    def real_sample_step(
        self, agent: Agent, krm: KnowledgeRoadmap, lg: LocalGrid,
    ) -> None:
        frontiers_cells = lg.sample_frontiers_on_cellmap(
            radius=self.frontier_sample_radius_num_cells,
            num_frontiers_to_sample=self.N_samples,
        )
        for frontier_cell in frontiers_cells:
            frontier_pos_global = lg.cell_idx2world_coords(frontier_cell)
            krm.add_frontier(frontier_pos_global, agent.at_wp)

    def sample_waypoint(self, agent: Agent, krm: KnowledgeRoadmap) -> None:
        """
        Sample a new waypoint at current agent pos, and add an edge connecting it to prev wp.
        this should be sampled from the pose graph eventually
        """
        wp_at_previous_pos = krm.get_node_by_pos(agent.previous_pos)
        krm.add_waypoint(agent.pos, wp_at_previous_pos)
        agent.at_wp = krm.get_node_by_pos(agent.pos)

    def get_nodes_of_type_in_radius(
        self, pos: tuple, radius: float, node_type: str, krm: KnowledgeRoadmap
    ) -> list:
        """
        Given a position, a radius and a node type, return a list of nodes of that type that are within the radius of the position.

        :param pos: the position of the agent
        :param radius: the radius of the circle
        :param node_type: the type of node to search for
        :return: The list of nodes that are close to the given position.
        """
        close_nodes = []
        for node in krm.graph.nodes:
            data = krm.get_node_data_by_idx(node)
            if data["type"] == node_type:
                node_pos = data["pos"]
                if (
                    abs(pos[0] - node_pos[0]) < radius
                    and abs(pos[1] - node_pos[1]) < radius
                ):
                    close_nodes.append(node)
        return close_nodes

    def prune_frontiers(self, krm: KnowledgeRoadmap) -> None:
        """obtain all the frontier nodes in krm in a certain radius around the current position"""

        waypoints = krm.get_all_waypoint_idxs()

        for wp in waypoints:
            wp_pos = krm.get_node_data_by_idx(wp)["pos"]
            close_frontiers = self.get_nodes_of_type_in_radius(
                wp_pos, self.prune_radius, "frontier", krm
            )
            for frontier in close_frontiers:
                krm.remove_frontier(frontier)

    def find_shortcuts_between_wps(self, lg: LocalGrid, krm: KnowledgeRoadmap, agent: Agent):
        close_nodes = krm.get_nodes_of_type_in_margin(
            lg.world_pos, self.lg_length_in_m / 2, "waypoint"
        )
        points = []
        for node in close_nodes:
            if node != agent.at_wp:
                points.append(krm.get_node_data_by_idx(node)["pos"])

        if points:
            for point in points:
                at_cell = lg.length_num_cells / 2, lg.length_num_cells / 2
                to_cell = lg.world_coords2cell_idxs(point)
                is_collision_free, _ = lg.is_collision_free_straight_line_between_cells(
                    at_cell, to_cell
                )
                if is_collision_free:
                    from_wp = agent.at_wp
                    to_wp = krm.get_node_by_pos(point)
                    krm.graph.add_edge(
                        from_wp, to_wp, type="waypoint_edge", id=uuid.uuid4()
                    )

    def perform_path_step(self, agent: Agent, path:list, krm:KnowledgeRoadmap) -> list or None:
        '''
        Execute a single step of the path.
        '''
        # if agent.debug:
        #     print(f"the path {path} length is {len(path)}")
        if len(path) > 1:
            node_data = krm.get_node_data_by_idx(path[0])
            agent.teleport_to_pos(node_data['pos'])
            path.pop(0)
            return path

        elif len(path) == 1:
            selected_frontier_data = krm.get_node_data_by_idx(
                path[0])
            agent.teleport_to_pos(selected_frontier_data['pos'])
            if self.debug:
                print(f"SELECTED FRONTIER POS {selected_frontier_data['pos']}")
            return None


    def run_exploration_step(
        self, agent: Agent, krm: KnowledgeRoadmap, lg: LocalGrid,
    ) -> None or bool:
        if not self.init:
            self.real_sample_step(agent, krm, lg)
            self.init = True

        elif krm.graph.nodes[krm.get_node_by_pos(self.agent.pos)]["type"] == "frontier":
            if self.debug:
                print(f"1. step: frontier processing")
            """now we have visited the frontier we can remove it from the KRM and sample a waypoint in its place"""
            krm.remove_frontier(self.selected_frontier_idx)
            self.selected_frontier_idx = None

            self.sample_waypoint(agent, krm)
            self.real_sample_step(agent, krm, lg)
            self.prune_frontiers(krm)
            self.find_shortcuts_between_wps(lg, krm, agent)

        elif self.consumable_path:
            if self.debug:
                print(f"2. step: execute consumable path")
            self.consumable_path = self.perform_path_step( 
                agent, self.consumable_path, krm
            )
        elif not self.selected_frontier_idx:
            """if there are no more frontiers, exploration is done"""
            self.selected_frontier_idx = self.select_target_frontier(agent, krm)
            if agent.no_more_frontiers:
                print("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
                print(
                    f"It took {self.agent.steps_taken} steps to complete the exploration."
                )
                return True

            if self.debug:
                print(f"3. step: select target frontier and find path")
            self.consumable_path = self.find_path_to_selected_frontier(
                agent, self.selected_frontier_idx, krm
            )

        # if self.agent.debug:
        #     self.agent.debug_logger()

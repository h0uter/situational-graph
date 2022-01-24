import uuid
import networkx as nx

class KnowledgeRoadmap():
    '''
    An agent implements a Knowledge Roadmap to keep track of the 
    world beliefs which are relevant for navigating during his mission.
    A KRM is a graph with 3 distinct node and corresponding edge types.
    - Waypoint Nodes:: correspond to places the robot has been and can go to.
    - Frontier Nodes:: correspond to places the robot has not been but expects it can go to.
    - World Object Nodes:: correspond to actionable items the robot has seen.
    '''

    # TODO: adress local vs global KRM
    def __init__(self, start_pos=(0, 0)):
        # TODO: this leads to hella ugly krm.KRM notation everywhere
        # perhaps krm should just be the graph and, this should be a KRM_manager?
        self.KRM = nx.Graph() # Knowledge Road Map

        # TODO: start node like this is lame
        self.KRM.add_node(0, pos=start_pos, type="waypoint", id=uuid.uuid4())
        self.next_wp_idx = 1
        self.next_frontier_idx = 1000
        self.next_wo_idx = 200

    def add_waypoint(self, pos, prev_wp):
        ''' adds new waypoints and increments wp the idx'''
        self.KRM.add_node(self.next_wp_idx, pos=pos, type="waypoint", id=uuid.uuid4())
        self.KRM.add_edge(self.next_wp_idx, prev_wp, type="waypoint_edge", id=uuid.uuid4())
        self.next_wp_idx += 1

    def add_waypoints(self, wp_array):
        ''' adds waypoints to the graph'''
        for wp in wp_array:
            self.add_waypoint(wp)

    def add_world_object(self, pos, label):
        ''' adds a world object to the graph'''
        self.KRM.add_node(label, pos=pos, type="world_object", id=uuid.uuid4())
        self.KRM.add_edge(self.next_wp_idx-1, label, type="world_object_edge", id=uuid.uuid4())

    # TODO: remove the agent_at_wp parameter requirement
    def add_frontier(self, pos, agent_at_wp):
        ''' adds a frontier to the graph'''
        self.KRM.add_node(self.next_frontier_idx, pos=pos,
                        type="frontier", id=uuid.uuid4())
        self.KRM.add_edge(agent_at_wp, self.next_frontier_idx,
                          type="frontier_edge", id=uuid.uuid4())
        self.next_frontier_idx += 1

    def remove_frontier(self, target_frontier_idx):
        ''' removes a frontier from the graph'''
        target_frontier = self.get_node_data_by_idx(target_frontier_idx)
        if target_frontier['type'] == 'frontier':
            self.KRM.remove_node(target_frontier_idx)  

    def get_node_by_pos(self, pos):
        ''' returns the node idx at the given position '''
        for node in self.KRM.nodes():
            if self.KRM.nodes[node]['pos'] == pos:
                return node

    def get_node_by_UUID(self, UUID):
        ''' returns the node idx with the given UUID '''
        for node in self.KRM.nodes():
            if self.KRM.nodes[node]['id'] == UUID:
                return node

    def get_node_data_by_idx(self, idx):
        ''' returns the node corresponding to the given index '''
        return self.KRM.nodes[idx]

    def get_all_waypoints(self):
        ''' returns all waypoints in the graph'''
        return [self.KRM.nodes[node] for node in self.KRM.nodes() if self.KRM.nodes[node]['type'] == 'waypoint']

    def get_all_waypoint_idxs(self):
        ''' returns all frontier idxs in the graph'''
        return [node for node in self.KRM.nodes() if self.KRM.nodes[node]['type'] == 'waypoint']

    def get_all_frontiers_idxs(self):
        ''' returns all frontier idxs in the graph'''
        return [node for node in self.KRM.nodes() if self.KRM.nodes[node]['type'] == 'frontier']


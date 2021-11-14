import uuid

class GraphManager():
    def __init__(self):
        self.test = None

    def create_waypoint_node(self, graph, pos):
        graph.add_node(uuid.uuid4(), pos=pos, type="waypoint")

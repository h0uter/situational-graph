from uuid import uuid4

OBJECTIVES = {}


class Task:
    def __init__(self, edge_uuid, objective_id):
        self.uuid = uuid4()
        self.edge_uuid = edge_uuid
        self.objective_id = objective_id

    def reward(self):
        # return OBJECTIVES[self.objective_id]
        return 100

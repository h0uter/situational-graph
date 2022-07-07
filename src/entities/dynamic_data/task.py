from uuid import uuid4


OBJECTIVES = {}


class Task:
    def __init__(self, edge_id, objective_id):
        self.id = uuid4()
        self.edge_id = edge_id
        self.objective_id = objective_id

    def reward(self):
        # return OBJECTIVES[self.objective_id]
        return 100

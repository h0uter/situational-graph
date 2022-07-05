from src.entities.abstract_agent import AbstractAgent
from src.entities.krm import KRM
from src.usecases.actions.abstract_behavior import AbstractBehavior
from src.utils.config import Config


class GotoBehavior(AbstractBehavior):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def run(self, agent: AbstractAgent, krm: KRM, action_path) -> list:
        if len(action_path) < 1:
            raise Exception(
                f"{agent.name}: Trying to perform action_path step with empty action_path {action_path}."
            )

        node_data = krm.get_node_data_by_node(action_path[0][1])
        agent.move_to_pos(node_data["pos"])
        agent.localize_to_waypoint(krm)

        action_path.pop(0)
        return action_path

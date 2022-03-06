from src.usecases.actions.abstract_action import AbstractAction
from src.utils.config import Config
from src.utils.my_types import NodeType


class Goto(AbstractAction):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def run(self, agent, krm, action_path):
        # Execute a single action edge of the action path.

        if len(action_path) >= 2:
            # node_data = krm.get_node_data_by_idx(action_path[0])
            node_data = krm.get_node_data_by_idx(action_path[1])
            agent.move_to_pos(node_data["pos"])
            # FIXME: this can return none if world object nodes are included in the graph.
            # can just give them infinite weight... should solve it by performing shortest action_path over a subgraph.
            # BUG: can still randomly think the agent is at a world object if it is very close to the frontier.
            agent.at_wp = krm.get_nodes_of_type_in_margin(
                agent.pos, self.cfg.AT_WP_MARGIN, NodeType.WAYPOINT
            )[0]
            action_path.pop(0)
            return action_path

        else:
            # self._logger.warning(
            #     f"trying to perform action_path step with empty action_path {action_path}"
            # )
            raise Exception(
                f"{agent.name}: Trying to perform action_path step with empty action_path {action_path}."
            )

from typing import Sequence

from src.config import cfg
from src.domain import TOSG
from src.shared.object_types import Situations
from src.usecases.shared.behaviors.actions.find_shortcuts_between_wps_on_lg import (
    add_shortcut_edges_between_wps_on_lg,
)
from src.planning.tosg import TOSG
from src.usecases.sar.sar_affordances import SAR_AFFORDANCES
from src.usecases.usecase import Usecase

"""This is a usecase to obtain the task swithc results."""


class TaskSwitchUsecase(Usecase):
    def run(self):
        cfg.AGENT_START_POS = (6.5, -14)
        agents, tosg, usecases, viz_listener = self.init_entities()
        self.common_setup(tosg, agents, start_poses=[agent.pos for agent in agents])

        self.setup(tosg)
        for agent in agents:
            lg = agent.get_local_grid()
            add_shortcut_edges_between_wps_on_lg(lg, tosg, agent)
        """setup the specifics of the usecase"""
        # FIXME: so the task is added to the list but not selected.
        for agent in agents:
            agent.set_init_explore_step()

        success = self.main_loop(agents, tosg, usecases, viz_listener)
        return success

    def setup(self, tosg: TOSG):
        X1 = 7.5
        X2 = 11

        NODE_POSITIONS = [
            (X1, -13),
            (X1, -9),
            (X1, -5),
            (X1, -1),
            (X2, -1),
            (X2, -5),
            (X2, -9),
            (X2, -13),
        ]

        def node_adder(node_positions: Sequence[tuple[float, float]]):
            node_list = []
            for node_position in node_positions:
                new_node = tosg.add_waypoint_node(node_position)
                node_list.append(new_node)
            return node_list

        node_list = node_adder(NODE_POSITIONS)

        for i, node in enumerate(node_list):
            if i == 0:
                continue
            else:
                tosg.add_waypoint_diedge(node_list[i - 1], node_list[i])

        orig_task_pos = (X1, 3)
        tosg.add_node_with_task_and_edges_from_affordances(
            # node_list[3], ObjectTypes.FRONTIER, new_task_pos, SAR_AFFORDANCES
            node_list[3],
            Situations.UNKNOWN_VICTIM,
            orig_task_pos,
            SAR_AFFORDANCES,
        )

        switch_task_pos = (X2 + 3, -9)
        tosg.add_node_with_task_and_edges_from_affordances(
            # node_list[3], ObjectTypes.FRONTIER, new_task_pos, SAR_AFFORDANCES
            node_list[6],
            Situations.UNKNOWN_VICTIM,
            switch_task_pos,
            SAR_AFFORDANCES,
        )

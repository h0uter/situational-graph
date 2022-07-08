from enum import Enum, auto
import logging
from abc import ABC, abstractmethod
from tkinter import E
from typing import Literal, Optional, Sequence, Tuple

from src.entities.abstract_agent import AbstractAgent
from src.entities.tosg import TOSG
from src.entities.plan import Plan
from src.utils.config import Config
from src.entities.dynamic_data.task import Task
from src.utils.my_types import Edge, EdgeType, Node
from src.usecases.behaviors.goto_behavior import GotoBehavior
from src.usecases.behaviors.explore_behavior import ExploreBehavior
from src.entities.static_data.objective import Objective


def select_optimal_task(
    agent: AbstractAgent, tosgraph: TOSG, tasks: Sequence[Task]
) -> Optional[Task]:
    # this should be a method of the agent
    pass


def find_plan(agent: AbstractAgent, tosgraph: TOSG, task: Task) -> Plan:
    """Find a plan for the agent."""
    pass


def execute_edge(
    agent: AbstractAgent, tosgraph: TOSG, plan: Plan, tasks: Sequence[Task]
) -> Tuple[Plan, Sequence[Task]]:
    """Execute the plan."""
    pass


class PlanningPipeline:
    def __init__(self, cfg: Config, tosg: TOSG, agent) -> None:
        self.cfg = cfg
        self.completed = False
        self.plan: Plan = Plan()
        # self.target_node: Optional[Node] = None
        self._log = logging.getLogger(__name__)

        self.initialize(tosg, agent)

    @property
    def target_node(self) -> Optional[Node]:
        if len(self.plan) >= 1:
            return self.plan[-1][1]
        else:
            # raise ValueError("edge sequence is empty")
            self.plan.invalidate
            return None

    # HACK: initialization should add this edge to the tasks,
    # FIXME: this is the start, here I will add the tasks and see them work instantly
    def initialize(self, tosg: TOSG, agent):
        # Add a frontier edge self loop on the start node to ensure a exploration sampling action
        edge_uuid = tosg.add_my_edge(0, 0, EdgeType.EXPLORE_FT_EDGE)

        tosg.tasks.append(Task(edge_uuid, Objective.EXPLORE))

        # spoof the task selection, just select the first one.
        init_explore_task = tosg.tasks[0]
        agent.task = init_explore_task
        # obtain the plan which corresponds to this edge.
        init_explore_edge_uuid = init_explore_task.edge_uuid
        init_explore_edge = tosg.get_edge_by_UUID(init_explore_edge_uuid)

        self.plan.edge_sequence = [init_explore_edge]
        self._log.debug(f"target node: {self.target_node}")

        # we also need a target node, what is the role of the plan and the target node both?
        # self.target_node = 0

    # CONTEXT
    def main_loop(self, agent: AbstractAgent, tosg: TOSG) -> bool:
        something_was_done_flag = False

        # target_node = agent.task.get_target_node(krm)


        # either we are not removing the task and we keep doing the same thing...
        # we are not sampling continuously over and over again
        # we select 0 and we cannot find a path to get there

        if self.target_node is None:
            self._log.debug(f"{agent.name}: No task selected for the agent. Setting one.")
            # self.target_node = self.target_selection(agent, krm)
            selected_task = self.task_selection(agent, tosg)

            print([task.get_target_node(tosg) for task in tosg.tasks])

            agent.task = selected_task
            something_was_done_flag = True

        if not self.plan.valid:
            self._log.debug(f"{agent.name}: task : {agent.task}")
            target_node = agent.task.get_target_node(tosg)
            self._log.debug(
                f"{agent.name}: No plan. Finding one to {target_node}."
            )
            edge_sequence = self.path_generation(agent, tosg, target_node)
            self.plan.edge_sequence = edge_sequence

            something_was_done_flag = True

        if len(self.plan) >= 1:
            self._log.debug(f"{agent.name}: Action path set. Executing one.")
            mutated_plan = self.plan_execution(agent, tosg, self.plan.edge_sequence)
            self.plan.edge_sequence = mutated_plan

            self._log.debug(f"{agent.name}: mutated plan {mutated_plan}")

            if len(mutated_plan) == 0:
                self._log.debug(f"{agent.name}: plan execution finished.")
                self.destroy_task(agent, tosg)

            something_was_done_flag = True

        # only ever have to check completion here
        if self.check_completion(tosg):
            self._log.debug(f"{agent.name}: Exploration completed.")
            self.completed = True

        if not something_was_done_flag:
            logging.warning("No exploration step taken")

        return self.completed

    def destroy_task(self, agent: AbstractAgent, tosg: TOSG):
        self._log.debug(f"{agent.name}:  has a task  {agent.task}")
        # if agent.task:
        #     for task in tosg.tasks:
        #         if task.uuid == agent.task.uuid:
        #             tosg.tasks.remove(agent.task)
        #             break

        if agent.task:
            if agent.task in tosg.tasks:
                tosg.tasks.remove(agent.task)
                # agent.task = None
        self._log.debug(f"{agent.name}: destroying task  {agent.task}")

        #     if agent.task.uuid in [task.uuid for task in tosg.tasks]:
        #         tosg.tasks.remove(agent.task)

        agent.clear_task()
        # self.plan.invalidate()

    def check_target_available(self, krm: TOSG) -> bool:
        num_targets = 0
        num_frontiers = len(krm.get_all_frontiers_idxs())
        num_targets += num_frontiers
        num_targets += len(krm.get_all_world_object_idxs())

        if num_targets < 1:
            return False
        else:
            return True

    # def clear_target(self) -> None:
    #     self.target_node = None

    def check_target_still_valid(self, krm: TOSG, target_node: Optional[Node]) -> bool:
        if target_node is None:
            return False
        return krm.check_node_exists(target_node)

    # def task_selection(self, agent: AbstractAgent, tosg: TOSG) -> Optional[Node]:
    def task_selection(self, agent: AbstractAgent, tosg: TOSG) -> Optional[Task]:

        highest_utility = 0
        optimal_task = None

        tosg.remove_invalid_tasks()

        print(len([task.uuid for task in tosg.tasks]), " tasks uuid")
        print(len(tosg.tasks), " tasks array")

        for task in tosg.tasks:
            print(f"evaluating the utility of tasks: {task}")
            task_target_node = task.get_target_node(tosg)
            if not task_target_node:
                continue

            path_cost = tosg.shortest_path_len(agent.at_wp, task_target_node)

            def calc_utility(reward: float, path_cost: float) -> float:
                if path_cost == 0:
                    return float("inf")
                else:
                    return reward / path_cost

            utility = calc_utility(task.reward, path_cost)

            if utility > highest_utility:
                highest_utility = utility
                optimal_task = task

        # return optimal_task.get_edge(tosg)
        self._log.debug(f"{agent.name}: Selected task: {optimal_task}")
        return optimal_task

        # - [x] obtain list of all task edges
        # - for each task edge check its utility
        # - select the task edge with the highest utility.
        # - return the associated task

        # return target_node

    def path_generation(
        self, agent: AbstractAgent, krm: TOSG, target_node: Node
    ) -> Sequence[Optional[Edge]]:

        # FIXME: lets make the plan check its own validity
        if not self.check_target_still_valid(krm, target_node):
            self._log.warning(
                f"path_execution()::{agent.name}:: Target is no longer valid."
            )
            return []

        self._log.debug(f"{agent.name}: target_node: {target_node}")
        node_path = krm.shortest_path(agent.at_wp, target_node)  # type: ignore

        if node_path:
            node_path = list(node_path)
            edge_path = krm.node_list_to_edge_list(node_path)
            return edge_path
        else:
            self._log.warning(f"{agent.name}: path_generation(): no path found")
            return []

    # this is the plan executor, maybe make it its own class.
    def plan_execution(
        self, agent: AbstractAgent, krm: TOSG, edge_path: Sequence[Edge]
    ) -> Sequence[Optional[Edge]]:
        if not self.check_target_still_valid(krm, self.target_node):
            self._log.warning(
                f"path_execution()::{agent.name}:: Target is no longer valid."
            )
            # self.clear_target()
            self.destroy_task(agent, krm)

            return []

        self._log.debug(f"{agent.name}: action_path: {edge_path}")
        # print(f"action_path: {action_path}")
        # current_edge_type = krm.graph.edges[action_path[0], action_path[1]]["type"]
        # current_edge_type = krm.graph.edges[action_path[0]]["type"]
        current_edge_type = krm.get_type_of_edge_triplet(edge_path[0])
        self._log.debug(f"{agent.name}: current_edge_type: {current_edge_type}")

        if current_edge_type == EdgeType.EXPLORE_FT_EDGE:
            # action_path = ExploreBehavior(self.cfg).run(agent, krm, action_path)
            edge_path = ExploreBehavior(self.cfg).execute_pipeline(
                agent, krm, edge_path
            )
            # self.clear_target()
            self.destroy_task(agent, krm)
            return []


            # either a reset function
            # or pass and return the action path continuously

        elif current_edge_type == EdgeType.GOTO_WP_EDGE:
            # action_path = GotoBehavior(self.cfg).run(agent, krm, action_path)
            edge_path = GotoBehavior(self.cfg).execute_pipeline(agent, krm, edge_path)
            # if len(action_path) < 2:
            if len(edge_path) < 1:
                # self.clear_target()
                self.destroy_task(agent, krm)

                return []
            else:
                return edge_path

        return edge_path

    def check_completion(self, krm: TOSG) -> bool:
        num_of_frontiers = len(krm.get_all_frontiers_idxs())
        if num_of_frontiers < 1:
            return True
        else:
            return False

    """Target Selection"""
    ############################################################################################
    # ENTRYPOINT FOR GUIDING EXPLORATION WITH SEMANTICS ########################################
    ############################################################################################

    # FIXME: task selector, needs to use list of tasks
    def evaluate_potential_targets_based_on_path_cost(
        self, agent: AbstractAgent, target_idxs: list, krm: TOSG
    ) -> Optional[Node]:

        shortest_path_len = float("inf")
        selected_target_idx: Optional[Node] = None

        for target_idx in target_idxs:
            candidate_path_len: float = krm.shortest_path_len(agent.at_wp, target_idx)  # type: ignore

            if candidate_path_len < shortest_path_len and candidate_path_len != 0:
                shortest_path_len = candidate_path_len
                selected_target_idx = target_idx

        self._log.debug(
            f"{agent.name}: Shortest path found is: {candidate_path_len} for {selected_target_idx}."
        )

        if not selected_target_idx:
            self._log.error(
                f"{agent.name} at {agent.at_wp}: 1/2 No frontier can be selected from {len(target_idxs)} frontiers (0 candidate paths).\n {agent.name} at {agent.at_wp}: 2/2So either im at a node not connected to the krm or my target is not connected to the krm."
            )
            return

        assert selected_target_idx is not None

        return selected_target_idx

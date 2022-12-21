import time

from src.config import cfg
from src.core import event_system
from src.core.topics import Topics
from src.mission_autonomy.mission_initializer import MissionInitializer
from src.mission_autonomy.task_allocator import TaskAllocator
from src.operator.feedback_pipeline import (
    feedback_pipeline_completion,
    feedback_pipeline_init,
    feedback_pipeline_single_step,
)
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.platform_autonomy.platform_runner import PlatformRunnerMessage
from src.shared.situational_graph import SituationalGraph
from src.shared.task import Task


class MissionRunner:
    def __init__(
        self,
        agents: list[AbstractAgent],
        situational_graph: SituationalGraph,
        initializer: MissionInitializer,
    ):
        self.step = 0
        self.mission_completed = False
        self.operator_task_queue: list[Task] = []

        self.task_allocator = TaskAllocator()
        initializer.initialize_mission(agents, situational_graph)

        self.start, self.tosg_stats, self.my_logger = feedback_pipeline_init()

        # TODO: subscribe to operator task events.
        event_system.subscribe(Topics.OPERATOR_TASK, self.handle_operator_task_event)

    def mission_main_loop(
        self, agents: list[AbstractAgent], situational_graph: SituationalGraph
    ):

        """Main Logic Loop"""
        while True:
            while not self.mission_completed:
                self.inner_loop(
                    agents,
                    situational_graph,
                )

            feedback_pipeline_completion(
                self.step,
                agents,
                situational_graph,
                self.tosg_stats,
                self.my_logger,
                self.start,
            )




    def inner_loop(
        self,
        agents: list[AbstractAgent],
        situational_graph: SituationalGraph,
    ):
        step_start_time = time.perf_counter()

        # NAVIGATION: my window event will put something in a queue here that will result in that task being done first.
        # and also to lock the goto task in place
        if len(self.operator_task_queue) > 0:
            print(f"task queue: {self.operator_task_queue}")

        for agent_idx in range(len(agents)):
            agent = agents[agent_idx]

            if agent.init_explore_step_completed:
                filtered_situational_graph = situational_graph.get_filtered_graph(agent.capabilities)

                for task in self.operator_task_queue:
                    if task not in situational_graph.tasks:
                        situational_graph.tasks.append(task)

                # HACK: this if statement does not have correct logic
                if len(self.operator_task_queue) > 0 and agent.task is None:
                    """Operator task allocation"""
                    agent.task = self.operator_task_queue.pop(0)

                elif len(self.operator_task_queue) == 0 and agent.task is None:
                    """Autonomous task allocation"""
                    agent.task = self.task_allocator.single_agent_task_selection(
                        agent.at_wp, filtered_situational_graph
                    )

            # if agent.task:
            # print(f"Agent {agent_idx} is executing task {agent.task}")
            data = PlatformRunnerMessage(agent, situational_graph)
            event_system.post_event(Topics.RUN_PLATFORM, data)

            self.mission_completed = situational_graph.check_if_tasks_exhausted()

        feedback_pipeline_single_step(
            self.step,
            step_start_time,
            agents,
            situational_graph,
            self.tosg_stats,
            self.my_logger,
        )
        self.step += 1

    def handle_operator_task_event(self, data: Task):
        print(f"Operator task event received: {data}")
        self.operator_task_queue.append(data)
        self.mission_completed = False

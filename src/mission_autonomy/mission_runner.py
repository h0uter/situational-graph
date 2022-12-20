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
        tosg: SituationalGraph,
        initializer: MissionInitializer,
    ):
        self.step = 0
        self.mission_completed = False
        self.operator_task_queue: list[Task] = []

        self.task_allocator = TaskAllocator()
        initializer.initialize_mission(agents, tosg)

        self.start, self.tosg_stats, self.my_logger = feedback_pipeline_init()

        # TODO: subscribe to operator task events.
        event_system.subscribe(Topics.OPERATOR_TASK, self.handle_operator_task_event)

    def mission_main_loop(self, agents: list[AbstractAgent], tosg: SituationalGraph):

        """Main Logic Loop"""
        while True:

            while (not self.mission_completed) and self.step < cfg.MAX_STEPS:
                self.inner_loop(
                    agents,
                    tosg,
                )

            feedback_pipeline_completion(
                self.step,
                agents,
                tosg,
                self.tosg_stats,
                self.my_logger,
                self.start,
            )

        # krm_stats.save()
        return self.mission_completed

    def inner_loop(
        self,
        agents: list[AbstractAgent],
        tosg: SituationalGraph,
    ):
        step_start_time = time.perf_counter()

        # NAVIGATION: my window event will put something in a queue here that will result in that task being done first.
        # and also to lock the goto task in place
        if len(self.operator_task_queue) > 0:
            print(f"task queue: {self.operator_task_queue}")

        for agent_idx in range(len(agents)):
            agent = agents[agent_idx]

            if agent.init_explore_step_completed:
                filtered_tosg = tosg.get_filtered_graph(agent.capabilities)

                for task in self.operator_task_queue:
                    if task not in tosg.tasks:
                        tosg.tasks.append(task)

                # HACK: this if statement does not have correct logic
                if len(self.operator_task_queue) > 0 and agent.task is None:
                    """Operator task allocation"""
                    agent.task = self.operator_task_queue.pop(0)

                elif len(self.operator_task_queue) == 0 and agent.task is None:
                    """Autonomous task allocation"""
                    agent.task = self.task_allocator.single_agent_task_selection(
                        agent.at_wp, filtered_tosg
                    )

            # if agent.task:
            # print(f"Agent {agent_idx} is executing task {agent.task}")
            data = PlatformRunnerMessage(agent, tosg)
            event_system.post_event(Topics.RUN_PLATFORM, data)

            self.mission_completed = tosg.check_if_tasks_exhausted()

        feedback_pipeline_single_step(
            self.step,
            step_start_time,
            agents,
            tosg,
            self.tosg_stats,
            self.my_logger,
        )
        self.step += 1

    def handle_operator_task_event(self, data: Task):
        print(f"Operator task event received: {data}")
        self.operator_task_queue.append(data)
        self.mission_completed = False

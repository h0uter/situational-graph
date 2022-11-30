import time
from abc import abstractmethod
from typing import Sequence

import src.utils.event as event
from src.config import Scenario, cfg
from src.execution_autonomy.abstract_behavior import AbstractBehavior
from src.usecases.operator.utils.vizualisation_listener import VizualisationListener
from src.mission_autonomy.online_planner import OnlinePlanner
from src.platform_control.abstract_agent import AbstractAgent
from src.platform_control.real.spot_agent import SpotAgent
from src.platform_control.sim.simulated_agent import SimulatedAgent
from src.mission_autonomy.situational_graph import SituationalGraph
from src.shared.capabilities import Capabilities
from src.usecases.sar.sar_affordances import SAR_AFFORDANCES
from src.usecases.sar.sar_behaviors import SAR_BEHAVIORS
from src.usecases.utils.feedback import (feedback_pipeline_completion,
                                         feedback_pipeline_init,
                                         feedback_pipeline_single_step)


class Usecase:
    def main_loop(
        self,
        agents: list[AbstractAgent],
        tosg: SituationalGraph,
        planner: OnlinePlanner,
        viz_listener: VizualisationListener,
    ):

        step, start, tosg_stats, my_logger = feedback_pipeline_init()

        # # HACK: for the task switch usecase
        # for agent in agents:
        #     agent: SimulatedAgent
        #     agent.lg_spoofer.set_map(cfg.MAP_PATH_TASK_SWITCH)
        #     viz_listener.viz.set_map(cfg.MAP_PATH_TASK_SWITCH)

        """ Main Logic Loop"""
        mission_completed = False
        while (not mission_completed) and step < cfg.MAX_STEPS:
            step_start = time.perf_counter()

            for agent_idx in range(len(agents)):
                if planner.pipeline(agents[agent_idx], tosg):
                    """pipeline returns true if there are no more tasks."""
                    mission_completed = True
                    my_logger.info(f"Agent {agent_idx} completed exploration")
                    break

            feedback_pipeline_single_step(
                step, step_start, agents, tosg, tosg_stats, planner, my_logger
            )
            step += 1
            # time.sleep(2.5)

            # # HACK: debug stuff to show the method can exploit new shortcuts in the world
            # # what I should do instead is make his part of the usecase
            # MAP_SWITCHED = False
            # for agent in agents:
            #     agent.algo_iterations += 1
            #     if not MAP_SWITCHED and cfg.SCENARIO is not Scenario.REAL:
            #         if agent.algo_iterations > 150:
            #             agent: SimulatedAgent
            #             agent.lg_spoofer.set_map(cfg.MAP_PATH2)
            #             viz_listener.viz.set_map(cfg.MAP_PATH2)
            #             MAP_SWITCHED = True

        feedback_pipeline_completion(
            step, agents, tosg, tosg_stats, planner, my_logger, start
        )

        # krm_stats.save()
        return mission_completed

    def init_entities(self):
        a1_capabilities = {Capabilities.CAN_ASSESS}
        if cfg.SCENARIO == Scenario.REAL:
            agents = [SpotAgent(a1_capabilities)]
        else:
            agents = [
                SimulatedAgent(a1_capabilities)
            ]  # make the first agent only posses the capabilities
            agents.extend([SimulatedAgent(set(), i) for i in range(1, cfg.NUM_AGENTS)])

        tosg = SituationalGraph()

        domain_behaviors = SAR_BEHAVIORS
        affordances = SAR_AFFORDANCES
        # planner = OfflinePlanner(domain_behaviors, affordances)
        planner = OnlinePlanner(domain_behaviors, affordances)

        viz_listener = VizualisationListener()
        viz_listener.setup_event_handler()

        return agents, tosg, planner, viz_listener

    # base file
    def common_setup(self, tosg: SituationalGraph, agents: Sequence[AbstractAgent], start_poses):
        """Add a waypoint to the tosg for each agent, but check for duplicates"""
        duplicate_start_poses = []
        for start_pos in start_poses:
            if start_pos not in duplicate_start_poses:
                tosg.add_waypoint_node(start_pos)
                duplicate_start_poses.append(start_pos)

        """setup vizualisation of start poses"""
        for agent in agents:
            agent.get_local_grid()
            # agent.localize_to_waypoint(tosg)
            AbstractBehavior._localize_to_waypoint(agent, tosg)  # HACK: not ideal but this removes dependency of agent on tosg
            event.post_event("viz point", agent.pos)  # viz start position

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def setup(self):
        pass

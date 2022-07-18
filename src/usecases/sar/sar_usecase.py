import time
from typing import Sequence

import src.entrypoints.utils.event as event
from src.configuration.config import Config, Scenario
from src.data_providers.real.spot_agent import SpotAgent
from src.data_providers.sim.simulated_agent import SimulatedAgent
from src.domain import TOSG, OfflinePlanner
from src.domain.services.abstract_agent import AbstractAgent
from src.domain.services.online_planner import OnlinePlanner
from src.entrypoints.utils.vizualisation_listener import VizualisationListener
from src.usecases.sar.sar_affordances import SAR_AFFORDANCES
from src.usecases.sar.sar_behaviors import SAR_BEHAVIORS
from src.usecases.utils.feedback import (
    feedback_pipeline_completion,
    feedback_pipeline_init,
    feedback_pipeline_single_step,
)
from src.utils.sanity_checks import check_no_duplicate_wp_edges

from src.usecases.shortcut_task_switch_result import setup_task_switch_result


def run_sar_usecase(cfg: Config):
    agents, tosg, usecases, viz_listener = init_entities(cfg)
    success = run_demo(cfg, agents, tosg, usecases, viz_listener)
    return success


def run_task_switch_usecase(cfg: Config):
    agents, tosg, usecases, viz_listener = init_entities(cfg)
    setup_task_switch_result(tosg)
    success = run_demo(cfg, agents, tosg, usecases, viz_listener)
    return success


def init_entities(cfg: Config):
    if cfg.SCENARIO == Scenario.REAL:
        agents = [SpotAgent(cfg)]
    else:
        agents = [SimulatedAgent(cfg, i) for i in range(cfg.NUM_AGENTS)]

    tosg = TOSG(cfg, start_poses=[agent.pos for agent in agents])

    for agent in agents:
        agent.initialize(tosg)

    domain_behaviors = SAR_BEHAVIORS
    affordances = SAR_AFFORDANCES
    # planner = OfflinePlanner(cfg, domain_behaviors, affordances)
    planner = OnlinePlanner(cfg, domain_behaviors, affordances)

    viz_listener = VizualisationListener(cfg)
    viz_listener.setup_event_handler()

    """setup"""
    for agent in agents:
        agent.localize_to_waypoint(tosg)
        event.post_event("viz point", agent.pos)  # viz start position

    return agents, tosg, planner, viz_listener


def run_demo(
    cfg: Config,
    agents: Sequence[AbstractAgent],
    tosg: TOSG,
    planner: OfflinePlanner,
    viz_listener: VizualisationListener,
):

    step, start, tosg_stats, my_logger = feedback_pipeline_init(cfg)

    """ Main Logic Loop"""
    mission_completed = False
    while not mission_completed and step < cfg.MAX_STEPS:
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

        # HACK: debug stuff to show the method can exploit new shortcuts in the world
        # what I should do instead is make his part of the usecase
        MAP_SWITCHED = False
        for agent in agents:
            agent.algo_iterations += 1
            if not MAP_SWITCHED and cfg.SCENARIO is not Scenario.REAL:
                if agent.algo_iterations > 150:
                    agent: SimulatedAgent
                    agent.lg_spoofer.set_map(cfg.MAP_PATH2)
                    viz_listener.viz.set_map(cfg.MAP_PATH2)
                    MAP_SWITCHED = True

    feedback_pipeline_completion(
        cfg, step, agents, tosg, tosg_stats, planner, my_logger, start
    )

    # krm_stats.save()
    return mission_completed

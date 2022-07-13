import time
from typing import Sequence

import matplotlib
import src.entrypoints.utils.event as event
from src.configuration.config import Config, PlotLvl, Scenario
from src.data_providers.real.spot_agent import SpotAgent
from src.data_providers.sim.simulated_agent import SimulatedAgent
from src.domain import TOSG, Planner
from src.domain.abstract_agent import AbstractAgent
from src.entrypoints.utils.vizualisation_listener import VizualisationListener
from src.usecases.sar_affordances import SAR_AFFORDANCES
from src.usecases.sar_behaviors import SAR_BEHAVIORS
from src.usecases.utils.feedback import (
    feedback_pipeline_completion,
    feedback_pipeline_init,
    feedback_pipeline_single_step,
)
from src.utils.sanity_checks import check_no_duplicate_wp_edges

# the configuration is just the:
# objects
# behaviors
# objectives
# --> affordances


def run_sar_mission(cfg: Config):
    agents, krm, usecases = init_entities(cfg)
    success = run_demo(cfg, agents, krm, usecases)
    return success


# make different versions of this function for different scenarios
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
    planner = Planner(cfg, domain_behaviors, affordances)

    VizualisationListener(cfg).setup_event_handler()

    """setup"""
    for agent in agents:
        agent.localize_to_waypoint(tosg)
        event.post_event("viz point", agent.pos)  # viz start position

    return agents, tosg, planner


# TODO: move this to usecases
def run_demo(
    cfg: Config,
    agents: Sequence[AbstractAgent],
    tosg: TOSG,
    planner: Planner,
):

    step, start, tosg_stats, my_logger = feedback_pipeline_init(cfg)

    """ Main Logic Loop"""
    mission_completed = False
    while not mission_completed and step < cfg.MAX_STEPS:
        step_start = time.perf_counter()

        for agent_idx in range(len(agents)):
            if planner.pipeline(agents[agent_idx], tosg):
                mission_completed = True
                my_logger.info(f"Agent {agent_idx} completed exploration")
                break

            check_no_duplicate_wp_edges(tosg)

        feedback_pipeline_single_step(
            step, step_start, agents, tosg, tosg_stats, planner, my_logger
        )
        step += 1

    feedback_pipeline_completion(
        cfg, step, agents, tosg, tosg_stats, planner, my_logger, start
    )

    # krm_stats.save()
    return mission_completed


def benchmark_func():
    cfg = Config(
        plot_lvl=PlotLvl.NONE,
        num_agents=1,
        scenario=Scenario.SIM_MAZE_MEDIUM,
        max_steps=400,
    )

    run_sar_mission(cfg)

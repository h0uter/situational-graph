import logging
import time
from typing import Sequence

import matplotlib

import src.entrypoints.utils.event as event
from src.data_providers.real.spot_agent import SpotAgent
from src.data_providers.sim.simulated_agent import SimulatedAgent
from src.domain.abstract_agent import AbstractAgent
from src.domain.services.tosg import TOSG
from src.entrypoints.utils.vizualisation_listener import VizualisationListener
from src.domain.services.planner import Planner
from src.utils.audio_feedback import play_file
from src.configuration.config import Config, PlotLvl, Scenario
from src.utils.krm_stats import TOSGStats
from src.utils.sanity_checks import check_no_duplicate_wp_edges

from src.usecases.sar_behaviors import SAR_BEHAVIORS


def main(cfg: Config):
    agents, krm, usecases = init_entities(cfg)
    success = run_demo(cfg, agents, krm, usecases)
    return success


def init_entities(cfg: Config):
    if cfg.SCENARIO == Scenario.REAL:
        agents = [SpotAgent(cfg)]
    else:
        agents = [SimulatedAgent(cfg, i) for i in range(cfg.NUM_AGENTS)]

    tosg = TOSG(cfg, start_poses=[agent.pos for agent in agents])
    domain_behaviors = SAR_BEHAVIORS
    planning_pipelines = [Planner(cfg, tosg, agents[i], domain_behaviors) for i in range(cfg.NUM_AGENTS)]

    VizualisationListener(cfg).setup_event_handler()

    """setup"""
    for agent in agents:
        agent.localize_to_waypoint(tosg)
        event.post_event("viz point", agent.pos)  # viz start position

    return agents, tosg, planning_pipelines


def run_demo(
    cfg: Config,
    agents: Sequence[AbstractAgent],
    tosg: TOSG,
    planning_pipelines: Sequence[Planner],
):

    """Logging start."""
    step, start = 0, time.perf_counter()  # timing
    tosg_stats = TOSGStats()  # statistics logging object
    my_logger = logging.getLogger(__name__)
    my_logger.info(f"starting exploration demo {cfg.SCENARIO=}")
    if cfg.AUDIO_FEEDBACK:
        play_file("commencing_search.mp3")  # audio announcement of start

    """ Main Logic Loop"""
    while (
        not any(mission.completed is True for mission in planning_pipelines)
        and step < cfg.MAX_STEPS
    ):
        step_start = time.perf_counter()

        for agent_idx in range(len(agents)):
            if planning_pipelines[agent_idx].pipeline(agents[agent_idx], tosg):
                my_logger.info(f"Agent {agent_idx} completed exploration")
                break
            check_no_duplicate_wp_edges(tosg)

        feedback_pipeline_single_step(
            step, step_start, agents, tosg, tosg_stats, planning_pipelines, my_logger
        )
        step += 1

    feedback_pipeline_completion(
        step, agents, tosg, tosg_stats, planning_pipelines, my_logger, start
    )

    # krm_stats.save()
    # FIXME: make this check the tasks and remove this completed property
    return any(mission.completed is True for mission in planning_pipelines)


def feedback_pipeline_single_step(
    step, step_start, agents, tosg, tosg_stats, planning_pipelines, my_logger
):
    """Data collection"""
    step_duration = time.perf_counter() - step_start
    tosg_stats.update(tosg, step_duration)

    """ Visualisation """
    my_logger.debug(f"{step} ------------------------ {step_duration:.4f}s")
    event.post_event(
        "figure update",
        {"krm": tosg, "agents": agents, "usecases": planning_pipelines},
    )

    if step % 50 == 0:
        s = f"sim step = {step} took {step_duration:.4f}s, with {agents[0].steps_taken} move actions"
        my_logger.info(s)


def feedback_pipeline_completion(
    step, agents, tosg, tosg_stats, planning_pipelines, my_logger, start
):
    """Results"""
    my_logger.info(
        f"""
    !!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!
    {cfg.SCENARIO} took {step} sim steps
    with {agents[0].steps_taken} move actions
    and {time.perf_counter()-start:.2f}s to complete the exploration.
        """
    )

    if cfg.AUDIO_FEEDBACK:
        play_file("exploration_complete.mp3")

    event.post_event(
        "figure final result",
        {"krm": tosg, "agents": agents, "usecases": planning_pipelines},
    )

    if cfg.PLOT_LVL <= PlotLvl.STATS_ONLY:
        tosg_stats.plot_krm_stats()


def benchmark_func():
    cfg = Config(
        plot_lvl=PlotLvl.NONE,
        num_agents=1,
        scenario=Scenario.SIM_MAZE_MEDIUM,
        max_steps=400,
    )

    main(cfg)


if __name__ == "__main__":
    # matplotlib.use("Qt5agg")

    cfg = Config()
    # cfg = Config(scenario=Scenario.SIM_VILLA_ROOM)
    # cfg = Config(num_agents=5, scenario=Scenario.SIM_MAZE_MEDIUM)
    # cfg = Config(num_agents=2)
    # cfg = Config(num_agents=10, scenario=Scenario.SIM_MAZE_MEDIUM)
    # cfg = Config(plot_lvl=PlotLvl.NONE)
    # cfg = Config(scenario=Scenario.SIM_VILLA_ROOM, plot_lvl=PlotLvl.RESULT_ONLY)
    # cfg = Config(scenario=Scenario.SIM_MAZE)
    # cfg = Config(scenario=Scenario.SIM_VILLA, vizualiser=Vizualiser.MATPLOTLIB)
    # cfg = Config(plot_lvl=PlotLvl.RESULT_ONLY, scenario=Scenario.SIM_MAZE_MEDIUM)

    # cfg = Config(scenario=Scenario.REAL, vizualiser=Vizualiser.MATPLOTLIB)
    # cfg = Config(scenario=Scenario.REAL)

    # cfg = Config(PlotLvl.NONE, World.SIM_MAZE, num_agents=10)
    # cfg = Config(scenario=Scenario.SIM_VILLA, num_agents=10)
    # cfg = Config(scenario=Scenario.SIM_MAZE_MEDIUM)
    # cfg = Config(scenario=Scenario.SIM_MAZE_MEDIUM, vizualiser=Vizualiser.MATPLOTLIB)
    # cfg = Config(vizualiser=Vizualiser.MATPLOTLIB)

    main(cfg)
    # benchmark_func()

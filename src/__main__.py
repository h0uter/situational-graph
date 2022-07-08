import logging
import time
from typing import Sequence

import matplotlib

# from src.usecases.sar_mission import SARMission
import src.utils.event as event
from src.data_providers.real.spot_agent import SpotAgent
from src.data_providers.sim.simulated_agent import SimulatedAgent
from src.entities.abstract_agent import AbstractAgent
from src.entities.tosg import TOSG
from src.entrypoints.vizualisation_listener import VizualisationListener
from src.usecases.planning_pipeline import PlanningPipeline
from src.utils.audio_feedback import play_file
from src.utils.config import Config, PlotLvl, Scenario, Vizualiser
from src.utils.krm_stats import TOSGStats
from src.utils.sanity_checks import check_no_duplicate_wp_edges


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
    planning_pipelines = [PlanningPipeline(cfg, tosg, agents[i]) for i in range(cfg.NUM_AGENTS)]
    
    VizualisationListener(cfg).setup_event_handler()

    """setup"""
    for agent in agents:
        agent.localize_to_waypoint(tosg)
        event.post_event("viz point", agent.pos)  # viz start position

    return agents, tosg, planning_pipelines


# TODO: cleanup all the stuff not neccesary to understand the code high level
def run_demo(
    cfg: Config,
    agents: Sequence[AbstractAgent],
    tosg: TOSG,
    planning_pipelines: Sequence[PlanningPipeline],
):

    step, start = 0, time.perf_counter()
    tosg_stats = TOSGStats()
    my_logger = logging.getLogger(__name__)

    if cfg.AUDIO_FEEDBACK:
        play_file("commencing_search.mp3")

    """ Main Logic"""
    my_logger.info(f"starting exploration demo {cfg.SCENARIO=}")
    while (
        not any(mission.completed is True for mission in planning_pipelines)
        and step < cfg.MAX_STEPS
    ):
        step_start = time.perf_counter()

        for agent_idx in range(len(agents)):
            if planning_pipelines[agent_idx].main_loop(agents[agent_idx], tosg):
                my_logger.info(f"Agent {agent_idx} completed exploration")
                break
            check_no_duplicate_wp_edges(tosg)

        my_logger.debug(f"{tosg.tasks=}")

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

        step += 1

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

    # krm_stats.save()

    return any(mission.completed is True for mission in planning_pipelines)


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

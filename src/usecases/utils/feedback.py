import logging
import time
from src.configuration.config import PlotLvl, cfg
from src.domain.services.abstract_agent import AbstractAgent
from src.domain.services.tosg import TOSG

import src.entrypoints.utils.event as event
from src.utils.audio_feedback import play_file
from src.utils.krm_stats import TOSGStats


def feedback_pipeline_init():
    """Logging start."""
    step, start = 0, time.perf_counter()  # timing
    tosg_stats = TOSGStats()  # statistics logging object
    my_logger = logging.getLogger(__name__)
    my_logger.info(f"starting exploration demo {cfg.SCENARIO=}")
    if cfg.AUDIO_FEEDBACK:
        play_file("commencing_search.mp3")  # audio announcement of start
    return step, start, tosg_stats, my_logger


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
    step: int, agents: list[AbstractAgent], tosg: TOSG, tosg_stats, planning_pipelines, my_logger, start
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

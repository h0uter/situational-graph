import logging
import time
from dataclasses import dataclass

import src.core.event_system as event_system
from src.config import cfg
from src.shared.situational_graph import SituationalGraph
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.core.topics import Topics
from src.platform_autonomy.control.audio_feedback import play_file
from src.logging.tosg_stats import TOSGStats


@dataclass
class MissionViewModel:
    """A view model for the mission."""
    situational_graph: SituationalGraph
    agents: list[AbstractAgent]
    usecases: list


def feedback_pipeline_init():
    """Logging start."""
    start = time.perf_counter()  # timing
    tosg_stats = TOSGStats()  # statistics logging object
    tosg_stats.setup_event_handlers()
    my_logger = logging.getLogger(__name__)
    my_logger.info(f"starting exploration demo {cfg.SCENARIO=}")
    if cfg.AUDIO_FEEDBACK:
        play_file("commencing_search.mp3")  # audio announcement of start
    return start, tosg_stats, my_logger


def feedback_pipeline_single_step(
    step, step_start, agents, tosg, tosg_stats, usecases, my_logger
):
    """Data collection"""
    step_duration = time.perf_counter() - step_start
    tosg_stats.update(tosg, step_duration)

    """ Visualisation """
    my_logger.debug(f"{step} ------------------------ {step_duration:.4f}s")

    event_system.post_event(
        Topics.MISSION_VIEW_UPDATE,
        MissionViewModel(situational_graph=tosg, agents=agents, usecases=usecases),
    )

    if step % 50 == 0:
        s = f"sim step = {step} took {step_duration:.4f}s, with {agents[0].steps_taken} move actions"
        my_logger.info(s)


def feedback_pipeline_completion(
    step: int,
    agents: list[AbstractAgent],
    tosg: SituationalGraph,
    tosg_stats,
    usecases,
    my_logger,
    start,
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

    event_system.post_event(
        Topics.MISSION_VIEW_UPDATE_FINAL,
        MissionViewModel(situational_graph=tosg, agents=agents, usecases=usecases),
    )

    # if cfg.PLOT_LVL <= PlotLvl.STATS_ONLY:
    #     tosg_stats.plot_krm_stats()

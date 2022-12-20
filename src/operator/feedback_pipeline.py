import logging
import time
from dataclasses import dataclass

from src.config import cfg
from src.core import event_system
from src.core.topics import Topics
from src.core.logging.tosg_stats import TOSGStats
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.platform_autonomy.control.audio_feedback import play_file
from src.shared.situational_graph import SituationalGraph


@dataclass
class MissionViewModel:
    """The key datastructures used to vizualise mission progress."""
    situational_graph: SituationalGraph
    agents: list[AbstractAgent]


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
    step, step_start, agents, situational_graph, tosg_stats, my_logger
):
    """Data collection"""
    step_duration = time.perf_counter() - step_start
    tosg_stats.update(situational_graph, step_duration)

    """ Visualisation """
    my_logger.debug(f"{step} ------------------------ {step_duration:.4f}s")

    event_system.post_event(
        Topics.VIEW__MISSION_UPDATE,
        MissionViewModel(situational_graph=situational_graph, agents=agents),
    )

    if step % 50 == 0:
        s = f"sim step = {step} took {step_duration:.4f}s, with {agents[0].steps_taken} move actions"
        my_logger.info(s)


def feedback_pipeline_completion(
    step: int,
    agents: list[AbstractAgent],
    situational_graph: SituationalGraph,
    tosg_stats,
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

    # if cfg.AUDIO_FEEDBACK:
    #     play_file("exploration_complete.mp3")

    event_system.post_event(
        Topics.VIEW__MISSION_UPDATE_FINAL,
        MissionViewModel(situational_graph=situational_graph, agents=agents),
    )

    # if cfg.PLOT_LVL <= PlotLvl.STATS_ONLY:
    #     tosg_stats.plot_krm_stats()

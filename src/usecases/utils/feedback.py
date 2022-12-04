from dataclasses import dataclass
import logging
import time
from src.platform_state.local_grid import LocalGrid
from src.shared.topics import Topics

import src.utils.event as event
from src.config import cfg
from src.platform_control.abstract_agent import AbstractAgent
from src.mission_autonomy.situational_graph import SituationalGraph
from src.utils.audio_feedback import play_file
from src.utils.tosg_stats import TOSGStats

@dataclass
class MissionViewModel:
    """A view model for the mission."""
    situational_graph: SituationalGraph
    agents: list[AbstractAgent]
    usecases: list


def feedback_pipeline_init():
    """Logging start."""
    step, start = 0, time.perf_counter()  # timing
    tosg_stats = TOSGStats()  # statistics logging object
    tosg_stats.setup_event_handlers()
    my_logger = logging.getLogger(__name__)
    my_logger.info(f"starting exploration demo {cfg.SCENARIO=}")
    if cfg.AUDIO_FEEDBACK:
        play_file("commencing_search.mp3")  # audio announcement of start
    return step, start, tosg_stats, my_logger


def feedback_pipeline_single_step(
    step, step_start, agents, tosg, tosg_stats, usecases, my_logger
):
    """Data collection"""
    step_duration = time.perf_counter() - step_start
    tosg_stats.update(tosg, step_duration)

    """ Visualisation """
    my_logger.debug(f"{step} ------------------------ {step_duration:.4f}s")

    event.post_event(
        str(Topics.MISSION_VIEW_UPDATE),
                MissionViewModel(
            situational_graph=tosg, agents=agents, usecases=usecases
        )
    )

    if step % 50 == 0:
        s = f"sim step = {step} took {step_duration:.4f}s, with {agents[0].steps_taken} move actions"
        my_logger.info(s)


def feedback_pipeline_completion(
    step: int, agents: list[AbstractAgent], tosg: SituationalGraph, tosg_stats, usecases, my_logger, start
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
        str(Topics.MISSION_VIEW_UPDATE_FINAL),
        MissionViewModel(
            situational_graph=tosg, agents=agents, usecases=usecases
        )
    )

    # XXX dont plot krm stats
    # if cfg.PLOT_LVL <= PlotLvl.STATS_ONLY:
    #     tosg_stats.plot_krm_stats()

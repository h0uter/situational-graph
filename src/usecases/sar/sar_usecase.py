import time
from typing import Sequence

import src.entrypoints.utils.event as event
from src.configuration.config import Config, Scenario
from src.data_providers.real.spot_agent import SpotAgent
from src.data_providers.sim.simulated_agent import SimulatedAgent
from src.domain import TOSG, OfflinePlanner
from src.domain.entities.behaviors import Behaviors
from src.domain.entities.objectives import Objectives
from src.domain.entities.plan import Plan
from src.domain.entities.task import Task
from src.domain.services.abstract_agent import AbstractAgent
from src.domain.services.behaviors.actions.find_shortcuts_between_wps_on_lg import (
    add_shortcut_edges_between_wps_on_lg,
)
from src.domain.services.online_planner import OnlinePlanner
from src.entrypoints.utils.vizualisation_listener import VizualisationListener
from src.usecases.sar.sar_affordances import SAR_AFFORDANCES
from src.usecases.sar.sar_behaviors import SAR_BEHAVIORS
from src.usecases.shortcut_task_switch_result import setup_tosg_for_task_switch_result
from src.usecases.utils.feedback import (
    feedback_pipeline_completion,
    feedback_pipeline_init,
    feedback_pipeline_single_step,
)


def run_demo(
    cfg: Config,
    agents: Sequence[AbstractAgent],
    tosg: TOSG,
    planner: OnlinePlanner,
    viz_listener: VizualisationListener,
):

    step, start, tosg_stats, my_logger = feedback_pipeline_init(cfg)

    # # HACK: for the task switch usecase
    # for agent in agents:
    #     agent: SimulatedAgent
    #     agent.lg_spoofer.set_map(cfg.MAP_PATH_TASK_SWITCH)
    #     viz_listener.viz.set_map(cfg.MAP_PATH_TASK_SWITCH)

    """ Main Logic Loop"""
    mission_completed = False
    while (not mission_completed) or step < cfg.MAX_STEPS:
        step_start = time.perf_counter()
        # print(f">>> task list is {tosg.tasks}")

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
        cfg, step, agents, tosg, tosg_stats, planner, my_logger, start
    )

    # krm_stats.save()
    return mission_completed


def setup_usecase_common(tosg: TOSG, agents: Sequence[AbstractAgent], start_poses):
    """Add a waypoint to the tosg for each agent, but check for duplicates"""
    duplicate_start_poses = []
    for start_pos in start_poses:
        if start_pos not in duplicate_start_poses:
            tosg.add_waypoint_node(start_pos)
            duplicate_start_poses.append(start_pos)

    """setup vizualisation of start poses"""
    for agent in agents:
        agent.get_local_grid()
        agent.localize_to_waypoint(tosg)
        event.post_event("viz point", agent.pos)  # viz start position


def setup_exploration_usecase(tosg: TOSG, agents: Sequence[AbstractAgent]):
    """Manually set first task to exploring current position."""
    # for the demo I dont need this setup, I can instead manually craft the graph.
    for agent in agents:

        # Add an explore self edge on the start node to ensure a exploration sampling action
        edge = tosg.add_edge_of_type(agent.at_wp, agent.at_wp, Behaviors.EXPLORE)
        tosg.tasks.append(Task(edge, Objectives.EXPLORE_ALL_FTS))

        # spoof the task selection, just select the first one.
        agent.task = tosg.tasks[0]

        # obtain the plan which corresponds to this edge.
        init_explore_edge = agent.task.edge

        agent.plan = Plan([init_explore_edge])


def run_sar_usecase(cfg: Config):
    agents, tosg, usecases, viz_listener = init_entities(cfg)
    setup_usecase_common(tosg, agents, start_poses=[agent.pos for agent in agents])

    """setup the specifics of the usecase"""
    setup_exploration_usecase(tosg, agents)

    success = run_demo(cfg, agents, tosg, usecases, viz_listener)
    return success


def run_task_switch_usecase(cfg: Config):
    cfg.AGENT_START_POS = (6.5, -14)
    agents, tosg, usecases, viz_listener = init_entities(cfg)
    setup_usecase_common(tosg, agents, start_poses=[agent.pos for agent in agents])

    setup_tosg_for_task_switch_result(tosg)
    for agent in agents:
        lg = agent.get_local_grid()
        add_shortcut_edges_between_wps_on_lg(lg, tosg, agent, cfg)
    """setup the specifics of the usecase"""
    # FIXME: so the task is added to the list but not selected.
    for agent in agents:
        agent.set_init_explore_step()
    success = run_demo(cfg, agents, tosg, usecases, viz_listener)
    return success


def init_entities(cfg: Config):
    if cfg.SCENARIO == Scenario.REAL:
        agents = [SpotAgent(cfg)]
    else:
        agents = [SimulatedAgent(cfg, i) for i in range(cfg.NUM_AGENTS)]

    tosg = TOSG(cfg)

    domain_behaviors = SAR_BEHAVIORS
    affordances = SAR_AFFORDANCES
    # planner = OfflinePlanner(cfg, domain_behaviors, affordances)
    planner = OnlinePlanner(cfg, domain_behaviors, affordances)

    viz_listener = VizualisationListener(cfg)
    viz_listener.setup_event_handler()

    return agents, tosg, planner, viz_listener

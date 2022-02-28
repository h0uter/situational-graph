import logging
import time
from typing import Sequence


import matplotlib
from src.data_providers.simulated_agent import SimulatedAgent
from src.data_providers.spot_agent import SpotAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.abstract_agent import AbstractAgent
import src.utils.event as event
from src.usecases.exploration_usecase import ExplorationUsecase
from src.utils.config import Config, PlotLvl, Scenario, Vizualiser
from src.entrypoints.vizualisation_listener import VizualisationListener


############################################################################################
# DEMONSTRATIONS
############################################################################################


def init_entities(cfg: Config):
    if cfg.SCENARIO == Scenario.REAL:
        agents = [SpotAgent()]
    else:
        agents = [
            SimulatedAgent(cfg.AGENT_START_POS, cfg, i) for i in range(cfg.NUM_AGENTS)
        ]

    krm = KnowledgeRoadmap(start_poses=[agent.pos for agent in agents])
    exploration_usecases = [ExplorationUsecase(cfg) for i in range(cfg.NUM_AGENTS)]

    VizualisationListener(
        cfg
    ).setup_viz_event_handler()  # setup the listener for vizualisation

    return agents, krm, exploration_usecases


def perform_exploration_demo(
    cfg: Config,
    agents: Sequence[AbstractAgent],
    krm: KnowledgeRoadmap,
    exploration_usecases: Sequence[ExplorationUsecase],
):
    step = 0
    start = time.perf_counter()
    my_logger = logging.getLogger(__name__)

    for agent in agents:
        exploration_usecases[agent.name].exploration_strategy.localize_agent_to_wp(
            agent, krm
        )

    """ Main Logic"""
    # TODO: this condition should be checked for any of the agents
    # while exploration_usecases[0].ExplorationStrategy.exploration_completed is False:
    while not any(
        exploration_usecase.exploration_strategy.exploration_completed is True
        for exploration_usecase in exploration_usecases
    ):
        step_start = time.perf_counter()

        for agent_idx in range(len(agents)):
            if exploration_usecases[agent_idx].run_usecase_step(agents[agent_idx], krm):
                my_logger.info(f"Agent {agent_idx} completed exploration")
                break

        """ Visualisation """
        my_logger.debug("--------------------------------------------------------")
        event.post_event(
            "figure update",
            {"krm": krm, "agents": agents, "usecases": exploration_usecases},
        )

        if step % 50 == 0:
            s = f"sim step = {step} took {time.perf_counter() - step_start:.4f}s, with {agents[0].steps_taken} move actions"
            my_logger.info(s)
        step += 1

    # TODO: move this to the usecase, close to the data
    my_logger.info(
        f"""
    !!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!
    It took {step} sim steps
    with {agents[0].steps_taken} move actions
    and {time.perf_counter()-start:.2f}s to complete the exploration.
        """
    )

    event.post_event(
        "figure final result",
        {"krm": krm, "agents": agents, "usecases": exploration_usecases},
    )

    return exploration_usecases[0].exploration_strategy.exploration_completed


def main(cfg: Config):
    agents, krm, exploration_usecases = init_entities(cfg)
    success = perform_exploration_demo(cfg, agents, krm, exploration_usecases)
    return success


def benchmark_func():
    # cfg = Config(plot_lvl=PlotLvl.NONE)
    cfg = Config(
        plot_lvl=PlotLvl.NONE,
        num_agents=15,
        # scenario=Scenario.SIM_MAZE_MEDIUM
    )
    main(cfg)


if __name__ == "__main__":
    matplotlib.use("Qt5agg")

    cfg = Config()
    # cfg = Config(scenario=Scenario.SIM_VILLA_ROOM)
    # cfg = Config(num_agents=5, scenario=Scenario.SIM_MAZE_MEDIUM)
    # cfg = Config(num_agents=2)
    # cfg = Config(num_agents=3, scenario=Scenario.SIM_MAZE_MEDIUM)
    # cfg = Config(plot_lvl=PlotLvl.NONE)
    # cfg = Config(scenario=Scenario.SIM_VILLA_ROOM, plot_lvl=PlotLvl.RESULT_ONLY)
    # cfg = Config(scenario=Scenario.SIM_MAZE)
    # cfg = Config(scenario=Scenario.SIM_VILLA, vizualiser=Vizualiser.MATPLOTLIB)
    # cfg = Config(plot_lvl=PlotLvl.RESULT_ONLY, scenario=Scenario.SIM_MAZE_MEDIUM)

    # cfg = Config(scenario=Scenario.REAL, vizualiser=Vizualiser.MATPLOTLIB)

    # cfg = Config(PlotLvl.NONE, World.SIM_MAZE, num_agents=10)
    # cfg = Config(scenario=Scenario.SIM_VILLA, num_agents=10)
    # cfg = Config(scenario=Scenario.SIM_MAZE_MEDIUM)
    # cfg = Config(scenario=Scenario.SIM_MAZE_MEDIUM, vizualiser=Vizualiser.MATPLOTLIB)
    # cfg = Config(vizualiser=Vizualiser.MATPLOTLIB)

    main(cfg)

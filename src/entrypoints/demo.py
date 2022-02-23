import logging
import time

from typing import Sequence

import matplotlib
from src.entities.abstract_agent import AbstractAgent
from src.entrypoints.abstract_vizualisation import AbstractVizualisation
from src.data_providers.simulated_agent import SimulatedAgent
from src.data_providers.spot_agent import SpotAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entrypoints.mpl_vizualisation import MplVizualisation
from src.entrypoints.vedo_vizualisation import VedoVisualisation
from src.usecases.exploration_usecase import ExplorationUsecase
from src.utils.config import Config, PlotLvl, Vizualiser, World

# from src.utils.saving_objects import save_something

############################################################################################
# DEMONSTRATIONS
############################################################################################


def init_entities(cfg: Config):
    if cfg.WORLD == World.REAL:
        agents = [SpotAgent()]
        exploration_usecases = [ExplorationUsecase(cfg)]
    else:
        agents = [
            SimulatedAgent(cfg.AGENT_START_POS, cfg, i) for i in range(cfg.NUM_AGENTS)
        ]
        exploration_usecases = [ExplorationUsecase(cfg) for i in range(cfg.NUM_AGENTS)]

    if cfg.VIZUALISER == Vizualiser.MATPLOTLIB:
        gui = MplVizualisation(cfg)
    else:
        gui = VedoVisualisation(cfg)

    # TODO: fixme this is ugly
    start_poses = [agent.pos for agent in agents]
    krm = KnowledgeRoadmap(start_poses=start_poses)

    return gui, agents, krm, exploration_usecases


def perform_exploration_demo(
    cfg: Config,
    gui: AbstractVizualisation,
    agents: Sequence[AbstractAgent],
    krm: KnowledgeRoadmap,
    exploration_usecases: Sequence[ExplorationUsecase],
):
    step = 0
    start = time.perf_counter()
    my_logger = logging.getLogger(__name__)

    lg = None
    while exploration_usecases[0].no_frontiers is False:
        step_start = time.perf_counter()
        for agent_idx in range(len(agents)):

            # FIXME: this is to allow plotting the local grid with matplotlib for multiple agent
            if agent_idx == 0:
                # TODO: one exploration usecase should be enough, maybe not
                lg = exploration_usecases[agent_idx].run_exploration_step(
                    agents[agent_idx], krm
                )
            else:
                exploration_usecases[agent_idx].run_exploration_step(
                    agents[agent_idx], krm
                )

        if cfg.PLOT_LVL == PlotLvl.ALL or cfg.PLOT_LVL == PlotLvl.INTERMEDIATE_ONLY:
            gui.figure_update(krm, agents, lg)

        if step % 50 == 0:
            my_logger.info(
                f"sim step = {step} took {time.perf_counter() - step_start:.4f}s"
            )
        step += 1

    my_logger.info("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
    my_logger.info(
        f"It took {agents[0].steps_taken} move actions and {time.perf_counter()-start:.2f}s  to complete the exploration."
    )
    if cfg.PLOT_LVL == PlotLvl.RESULT_ONLY or cfg.PLOT_LVL == PlotLvl.ALL:
        gui.figure_final_result(krm, agents, lg)

    # save_something(krm, 'krm_1302.p')

    return exploration_usecases[0].no_frontiers


def main(cfg: Config):
    gui, agents, krm, exploration_usecases = init_entities(cfg)
    success = perform_exploration_demo(cfg, gui, agents, krm, exploration_usecases)
    return success


if __name__ == "__main__":
    matplotlib.use("Qt5agg")

    cfg = Config()
    # cfg = Config(plot_lvl=PlotLvl.NONE)
    # cfg = Config(world=World.SIM_VILLA_ROOM, plot_lvl=PlotLvl.RESULT_ONLY)
    # cfg = Config(world=World.SIM_MAZE)
    # cfg = Config(world=World.SIM_VILLA, vizualiser=Vizualiser.MATPLOTLIB)
    # cfg = Config(plot_lvl=PlotLvl.RESULT_ONLY, world=World.SIM_MAZE_MEDIUM)
    # cfg = Config(world=World.REAL, vizualiser=Vizualiser.MATPLOTLIB)
    # cfg = Config(PlotLvl.NONE, World.SIM_MAZE, num_agents=10)
    # cfg = Config(world=World.SIM_VILLA, num_agents=10)
    # cfg = Config(world=World.SIM_MAZE_MEDIUM)
    # cfg = Config(world=World.SIM_MAZE_MEDIUM, vizualiser=Vizualiser.MATPLOTLIB)

    main(cfg)

import logging
import time

from src.data_providers.simulated_agent import SimulatedAgent
from src.data_providers.spot_agent import SpotAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entrypoints.mpl_vizualisation import MplVizualisation
from src.entrypoints.vedo_vizualisation import VedoVisualisation
from src.usecases.exploration_usecase import ExplorationUsecase
from src.utils.config import Config, PlotLvl, World, Vizualiser
# from src.utils.saving_objects import save_something

import matplotlib

############################################################################################
# DEMONSTRATIONS
############################################################################################


def init_entities(cfg: Config):

    agents = []
    exploration_usecases = []
    num_agents = 5
    if cfg.WORLD == World.REAL:
        agents = [SpotAgent()]
    else:
        for i in range(num_agents):
            agents.append(SimulatedAgent(start_pos=(-3, 0), cfg=cfg, name=i))
            exploration_usecases.append(ExplorationUsecase(cfg))

    if cfg.VIZUALISER == Vizualiser.MATPLOTLIB:
        gui = MplVizualisation(cfg)
    else:
        gui = VedoVisualisation(cfg)
    start_poses = [agent.pos for agent in agents]
    krm = KnowledgeRoadmap(start_poses=start_poses)

    return gui, agents, krm, exploration_usecases


# def main(cfg: Config):
def main(cfg: Config):
    step = 0
    start = time.perf_counter()
    my_logger = logging.getLogger(__name__)

    gui, agents, krm, exploration_usecases = init_entities(cfg)

    while exploration_usecases[0].no_frontiers is False:
        step_start = time.perf_counter()
        for i in range(len(agents)):

            lg = None
            exploration_usecases[i].run_exploration_step(agents[i], krm)

        if cfg.PLOT_LVL == PlotLvl.ALL or cfg.PLOT_LVL == PlotLvl.INTERMEDIATE_ONLY:
            gui.figure_update(krm, agents, lg)

        if step % 50 == 0:
            my_logger.info(
                f"sim step = {step} took {time.perf_counter() - step_start:.4f}s"
            )
        step += 1

    my_logger.info("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
    my_logger.info(
        f"It took {agent.steps_taken} move actions and {time.perf_counter()-start:.2f}s  to complete the exploration."
    )
    if cfg.PLOT_LVL == PlotLvl.RESULT_ONLY or cfg.PLOT_LVL == PlotLvl.ALL:
        gui.figure_final_result(krm, agent, lg)

    # save_something(krm, 'krm_1302.p')

    return exploration_usecase[0].no_frontiers


if __name__ == "__main__":
    matplotlib.use("Qt5agg")

    # cfg = Config()
    # cfg = Config(plot_lvl=PlotLvl.NONE)
    # cfg = Config(world=World.SIM_VILLA_ROOM, plot_lvl=PlotLvl.RESULT_ONLY)
    # cfg = Config(world=World.SIM_MAZE)
    cfg = Config(world=World.SIM_MAZE_MEDIUM)
    # cfg = Config(plot_lvl=PlotLvl.RESULT_ONLY, world=World.SIM_MAZE_MEDIUM)
    # cfg = Config(world=World.REAL)

    main(cfg)

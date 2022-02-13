import logging
import time

import matplotlib.pyplot as plt
from src.data_providers.simulated_agent import SimulatedAgent
from src.data_providers.spot_agent import SpotAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entrypoints.mpl_vizualisation import MplVizualisation
from src.usecases.exploration_usecase import ExplorationUsecase
from src.utils.config import Config, PlotLvl, World

############################################################################################
# DEMONSTRATIONS
############################################################################################


def init_entities(cfg: Config):

    if cfg.world == World.REAL:
        agent = SpotAgent(start_pos=cfg.AGENT_START_POS)
    else:
        agent = SimulatedAgent(start_pos=cfg.AGENT_START_POS)

    gui = MplVizualisation()
    krm = KnowledgeRoadmap(start_pos=agent.pos)
    exploration_usecase = ExplorationUsecase()

    return gui, agent, krm, exploration_usecase


def main(cfg: Config):
    step = 0
    my_logger = logging.getLogger(__name__)

    gui, agent, krm, exploration_usecase = init_entities(cfg)

    while exploration_usecase.no_frontiers is False:
        start = time.perf_counter()

        lg = exploration_usecase.run_exploration_step(agent, krm)

        if cfg.plot_lvl == PlotLvl.ALL or cfg.plot_lvl == PlotLvl.INTERMEDIATE_ONLY:
            gui.figure_update(krm, agent, lg)

        my_logger.info(f"sim step = {step} took {time.perf_counter() - start:.4f}s")
        step += 1

    if cfg.plot_lvl == PlotLvl.RESULT_ONLY or cfg.plot_lvl == PlotLvl.ALL:
        plt.ioff()
        plt.show()

    return exploration_usecase.no_frontiers


if __name__ == "__main__":
    cfg = Config()
    # cfg = Config(plot_lvl=PlotLvl.NONE)

    main(cfg)

import logging
import time

import matplotlib.pyplot as plt
from src.data_providers.simulated_agent import SimulatedAgent
from src.data_providers.spot_agent import SpotAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entrypoints.mpl_vizualisation import MplVizualisation
from src.entrypoints.vedo_vizualisation import VedoVisualisation
from src.usecases.exploration_usecase import ExplorationUsecase
from src.utils.config import Config, PlotLvl, World
from src.utils.saving_objects import save_something

import matplotlib

############################################################################################
# DEMONSTRATIONS
############################################################################################


def init_entities(cfg: Config):

    if cfg.WORLD == World.REAL:
        agent = SpotAgent()
    else:
        agent = SimulatedAgent(start_pos=cfg.AGENT_START_POS, cfg=cfg)

    # gui = MplVizualisation(cfg)
    gui = VedoVisualisation(cfg)
    krm = KnowledgeRoadmap(start_pos=agent.pos)
    exploration_usecase = ExplorationUsecase(cfg)

    return gui, agent, krm, exploration_usecase


# def main(cfg: Config):
def main(cfg: Config):
    step = 0
    start = time.perf_counter()
    my_logger = logging.getLogger(__name__)

    gui, agent, krm, exploration_usecase = init_entities(cfg)

    while exploration_usecase.no_frontiers is False:
        step_start = time.perf_counter()

        lg = exploration_usecase.run_exploration_step(agent, krm)

        if cfg.PLOT_LVL == PlotLvl.ALL or cfg.PLOT_LVL == PlotLvl.INTERMEDIATE_ONLY:
            gui.figure_update(krm, agent, lg)
            # PLT = vedo_krm(krm, agent, cfg)

        if step % 10 == 0: my_logger.info(f"sim step = {step} took {time.perf_counter() - step_start:.4f}s")
        step += 1

    # if self.no_frontiers:
    my_logger.info("!!!!!!!!!!! EXPLORATION COMPLETED !!!!!!!!!!!")
    my_logger.info(
        f"It took {agent.steps_taken} move actions and {time.perf_counter()-start:.2f}s  to complete the exploration."
    )
    if cfg.PLOT_LVL == PlotLvl.RESULT_ONLY or cfg.PLOT_LVL == PlotLvl.ALL:
        # plt.ioff()
        # plt.show()
        gui.figure_final_result()
        # PLT.show(interactive=True)

    # save_something(krm, 'krm_1302.p')

    return exploration_usecase.no_frontiers


if __name__ == "__main__":
    matplotlib.use("Qt5agg")

    # cfg = Config()
    # cfg = Config(plot_lvl=PlotLvl.NONE)
    # cfg = Config(world=World.SIM_VILLA_ROOM)
    # cfg = Config(world=World.SIM_MAZE)
    cfg = Config(world=World.SIM_MAZE_MEDIUM)
    # cfg = Config(plot_lvl=PlotLvl.NONE, world=World.SIM_MAZE_MEDIUM)
    # cfg = Config(world=World.REAL)

    main(cfg)

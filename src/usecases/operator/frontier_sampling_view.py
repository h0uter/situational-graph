import vedo
import numpy as np

from src.shared.topics import Topics
from src.platform_state.local_grid import FrontierSamplingViewModel
from src.utils.event import subscribe

from src.config import cfg


class FrontierSamplingDebugView:
    def __init__(self):
        self.factor = 1 / cfg.LG_CELL_SIZE_M

        self.plt = vedo.Plotter(
            axes=13,
            interactive=False,
            resetcam=True,
            title=str(Topics.FRONTIER_SAMPLING),
            pos=(0, 1500),
            size=(800,800)
        )
        self.plt.show(resetcam=True)

        subscribe(str(Topics.FRONTIER_SAMPLING), self.viz_frontier_sampling)

    def viz_frontier_sampling(self, data: FrontierSamplingViewModel):
        actors = []
        self.plt.clear()
        
        # lg_actor = vedo.Picture(data.local_grid_img, flip=True)  # vizualises according to numpy convention top left is zero, zero. (rr, cc) = (-y, x)
        lg_actor = vedo.Picture(data.local_grid_img, flip=False)
        # lg_actor = vedo.Picture(np.rot90(data.local_grid_img, axes=(0, 1)), flip=False)
        actors.append(lg_actor)

        centre = int(lg_actor.dimensions()[0] / 2), int(lg_actor.dimensions()[1] / 2)

        agent_actor = vedo.Point(centre, r=10, c="b")
        actors.append(agent_actor)

        if data.new_frontier_cells:
            for ft in data.new_frontier_cells:
                ft_actor = vedo.Point(ft, r=25, c="g")
                ft_actor = vedo.Line(centre, ft, c="g", lw=10)
                actors.append(ft_actor)

        if data.collision_cells:
            for cp in data.collision_cells:
                cp_point_actor = vedo.Cross3D(
                    cp, s=0.3 * self.factor, c="p"
                )
                actors.append(cp_point_actor)

        self.plt.show(actors, resetcam=True)

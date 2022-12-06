import numpy as np
import vedo

from src.config import cfg
from src.platform_state.frontier_sampling_strategies import FrontierSamplingViewModel
from src.shared.topics import Topics
from src.shared.event_system import subscribe


class FrontierSamplingDebugView:
    def __init__(self):
        self.factor = 1 / cfg.LG_MTR_PER_CELL

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
        
        # lg_actor = vedo.Picture(data.local_grid_img, flip=False)
        # BUG: this vizualises correct, still dont understand why 2022-12-6
        lg_actor = vedo.Picture(np.rot90(data.local_grid_img, axes=(0, 1)), flip=False) # BUG: this vizualises correct, still dont understand why 2022-12-6
        actors.append(lg_actor)

        centre = int(lg_actor.dimensions()[0] / 2), int(lg_actor.dimensions()[1] / 2)

        agent_actor = vedo.Point(centre, r=20, c="cyan")
        actors.append(agent_actor)

        if data.new_frontier_cells:
            for ft in data.new_frontier_cells:
                ft_line_actor = vedo.Line(centre, ft, c="g", lw=10)
                actors.append(ft_line_actor)
                ft_actor = vedo.Point(ft, r=45, c="g")
                actors.append(ft_actor)

        if data.collision_cells:
            for cp in data.collision_cells:
                cp_point_actor = vedo.Cross3D(
                    cp, s=0.1 * self.factor, c="p"
                )
                actors.append(cp_point_actor)

        self.plt.show(actors, resetcam=True)

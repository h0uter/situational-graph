import vedo

from src.shared.topics import Topics
from src.usecases.shared.behaviors.explore_behavior import FrontierSamplingViewModel
from src.utils.event import subscribe


class FrontierSamplingDebugView:
    def __init__(self):
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
        
        data.local_grid_img[5, 1:50] = 1  # this is still indexed y, x from the top

        lg_actor = vedo.Picture(data.local_grid_img, flip=True)  # vizualises according to numpy convention top left is zero, zero. (rr, cc) = (-y, x)
        # lg_actor = vedo.Picture(data.local_grid_img, flip=False)
        actors.append(lg_actor)

        centre = int(lg_actor.dimensions()[0] / 2), int(lg_actor.dimensions()[1] / 2)

        agent_actor = vedo.Point(centre, r=10, c="b")
        actors.append(agent_actor)

        if data.new_frontier_cells:
            for ft in data.new_frontier_cells:

                # frontier_cells = (ft[1], ft[0])
                frontier_cells = ft
                ft_actor = vedo.Point(frontier_cells, r=25, c="g")
                ft_actor = vedo.Line(centre, frontier_cells, c="g", lw=10)
                actors.append(ft_actor)

        self.plt.show(actors, resetcam=True)

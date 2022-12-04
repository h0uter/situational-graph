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
        )
        self.plt.show(resetcam=True)

        subscribe(str(Topics.FRONTIER_SAMPLING), self.viz_frontier_sampling)

    def viz_frontier_sampling(self, data: FrontierSamplingViewModel):
        actors = []
        self.plt.clear()

        # lg_actor = vedo.Picture(local_grid.data, flip=True)
        lg_actor = vedo.Picture(data.local_grid_img, flip=False)
        actors.append(lg_actor)

        centre = int(lg_actor.dimensions()[0] / 2), int(lg_actor.dimensions()[1] / 2)

        agent_actor = vedo.Point(centre, r=10, c="b")
        actors.append(agent_actor)

        if data.new_frontier_cells:
            for ft in data.new_frontier_cells:

                # frontier_cells = (ft[1], ft[0])
                frontier_cells = ft
                ft_actor = vedo.Point(frontier_cells, r=20, c="g")
                ft_actor = vedo.Line(centre, frontier_cells, c="g")
                actors.append(ft_actor)

        self.plt.show(actors, resetcam=True)

import numpy.typing as npt
import vedo

from src.config import cfg
from src.platform_state.local_grid import LocalGrid


class LocalGridView:
    def __init__(self):
        self.factor = 1 / cfg.LG_CELL_SIZE_M

        self.plt2 = vedo.Plotter(
            axes=13,
            interactive=False,
            resetcam=True,
            title="wp_shortcuts",
            # size=(3456, 2000),
        )
        self.plt2.show(resetcam=True)
        self.plt3 = vedo.Plotter(
            axes=13,
            interactive=False,
            resetcam=True,
            title="frontier_sampling",
        )
        self.plt2.show(resetcam=True)

    def viz_waypoint_shortcuts(
        self, local_grid: LocalGrid, collision_points=None, candidate_shortcut_wps=None
    ):
        actors = []
        self.plt2.clear()

        lg_actor = vedo.Picture(local_grid.data, flip=True)
        actors.append(lg_actor)

        centre = int(lg_actor.dimensions()[0] / 2), int(lg_actor.dimensions()[1] / 2)

        agent_actor = vedo.Point(centre, r=10, c="b")
        actors.append(agent_actor)

        if candidate_shortcut_wps:
            for wp in candidate_shortcut_wps:
                wp_actor = vedo.Point(wp, r=10, c="r")
                actors.append(wp_actor)
                wp_line_actor = vedo.Line(centre, (wp[0], wp[1]), c="g", lw=5)
                actors.append(wp_line_actor)

        if collision_points:
            for cp in collision_points:
                cp_point_actor = vedo.Cross3D(
                    (cp[0], cp[1]), s=0.3 * self.factor, c="p"
                )
                actors.append(cp_point_actor)

        self.plt2.show(actors, resetcam=True)

    def viz_frontier_sampling(self, local_grid_img: npt.NDArray, frontier_points=None):
        actors = []
        self.plt3.clear()

        # lg_actor = vedo.Picture(local_grid.data, flip=True)
        lg_actor = vedo.Picture(local_grid_img, flip=False)
        actors.append(lg_actor)

        centre = int(lg_actor.dimensions()[0] / 2), int(lg_actor.dimensions()[1] / 2)

        agent_actor = vedo.Point(centre, r=10, c="b")
        actors.append(agent_actor)

        if frontier_points:
            for ft in frontier_points:

                # frontier_cells = (ft[1], ft[0])
                frontier_cells = ft
                ft_actor = vedo.Point(frontier_cells, r=20, c="g")
                ft_actor = vedo.Line(centre, frontier_cells, c="g")
                actors.append(ft_actor)

        self.plt3.show(actors, resetcam=True)

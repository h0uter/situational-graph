import vedo

from src.config import cfg
from src.shared.topics import Topics
from src.usecases.shared.behaviors.actions.find_shortcuts_between_wps_on_lg import (
    WaypointShortcutViewModel,
)
from src.usecases.shared.behaviors.explore_behavior import FrontierSamplingViewModel
from src.utils.event import subscribe


class LocalGridView:
    def __init__(self):
        self.factor = 1 / cfg.LG_CELL_SIZE_M

        self.plt2 = vedo.Plotter(
            axes=13,
            interactive=False,
            resetcam=True,
            title="wp_shortcuts",
        )
        self.plt2.show(resetcam=True)
        self.plt3 = vedo.Plotter(
            axes=13,
            interactive=False,
            resetcam=True,
            title="frontier_sampling",
        )
        self.plt2.show(resetcam=True)

        # setup event handlers
        subscribe(str(Topics.SHORTCUT_CHECKING), self.viz_waypoint_shortcuts)
        subscribe(str(Topics.FRONTIER_SAMPLING), self.viz_frontier_sampling)

    def viz_waypoint_shortcuts(self, data: WaypointShortcutViewModel):
        actors = []
        self.plt2.clear()

        lg_actor = vedo.Picture(data.local_grid.data, flip=True)
        actors.append(lg_actor)

        centre = int(lg_actor.dimensions()[0] / 2), int(lg_actor.dimensions()[1] / 2)

        agent_actor = vedo.Point(centre, r=10, c="b")
        actors.append(agent_actor)

        if data.shortcut_candidate_cells:
            for wp in data.shortcut_candidate_cells:
                wp_actor = vedo.Point(wp, r=10, c="r")
                actors.append(wp_actor)
                wp_line_actor = vedo.Line(centre, (wp[0], wp[1]), c="g", lw=5)
                actors.append(wp_line_actor)

        if data.collision_cells:
            for cp in data.collision_cells:
                cp_point_actor = vedo.Cross3D(
                    (cp[0], cp[1]), s=0.3 * self.factor, c="p"
                )
                actors.append(cp_point_actor)

        self.plt2.show(actors, resetcam=True)

    def viz_frontier_sampling(self, data: FrontierSamplingViewModel):
        actors = []
        self.plt3.clear()

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

        self.plt3.show(actors, resetcam=True)

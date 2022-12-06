import vedo

from src.config import cfg
from src.shared.topics import Topics
from src.usecases.shared.behaviors.actions.find_shortcuts_between_wps_on_lg import (
    WaypointShortcutViewModel,
)
from src.utils.event import subscribe


class WaypointShortcutDebugView:
    def __init__(self):
        self.factor = 1 / cfg.LG_CELL_SIZE_M

        self.plt = vedo.Plotter(
            axes=13,
            interactive=False,
            resetcam=True,
            title=str(Topics.SHORTCUT_CHECKING),
            pos=(0, 500),
            size=(800,800)
        )
        self.plt.show(resetcam=True)

        subscribe(str(Topics.SHORTCUT_CHECKING), self.viz_waypoint_shortcuts)

    def viz_waypoint_shortcuts(self, data: WaypointShortcutViewModel):
        actors = []
        self.plt.clear()

        # lg_actor = vedo.Picture(data.local_grid.data, flip=True)  # XXX: flip=True is important
        lg_actor = vedo.Picture(data.local_grid.data, flip=False)  # XXX: flip=True is important
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

        self.plt.show(actors, resetcam=True)

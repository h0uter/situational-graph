import numpy as np
import vedo

from src.config import cfg
from src.core.topics import Topics
from src.platform.autonomy.behaviors.actions.find_shortcuts_between_wps_on_lg import \
    WaypointShortcutViewModel
from src.core.event_system import subscribe


class WaypointShortcutDebugView:
    def __init__(self):
        self.factor = 1 / cfg.LG_MTR_PER_CELL

        self.plt = vedo.Plotter(
            axes=13,
            interactive=False,
            resetcam=True,
            title=str(Topics.SHORTCUT_CHECKING),
            pos=(0, 0),
            size=(1000, 1000),
        )
        self.plt.show(resetcam=True)

        subscribe(str(Topics.SHORTCUT_CHECKING), self.viz_waypoint_shortcuts)

    def viz_waypoint_shortcuts(self, data: WaypointShortcutViewModel):
        actors = []
        self.plt.clear()

        # lg_actor = vedo.Picture(data.local_grid.data, flip=False)
        # BUG: this vizualises correct, still dont understand why 2022-12-6
        lg_actor = vedo.Picture(np.rot90(data.local_grid.img_data, axes=(0, 1)), flip=False)
        actors.append(lg_actor)

        centre = int(lg_actor.dimensions()[0] / 2), int(lg_actor.dimensions()[1] / 2)

        agent_actor = vedo.Point(centre, r=20, c="cyan")
        actors.append(agent_actor)

        if data.shortcut_candidate_cells:
            for wp in data.shortcut_candidate_cells:
                wp_line_actor = vedo.Line(centre, wp, c="g", lw=10)
                actors.append(wp_line_actor)
                wp_actor = vedo.Point(wp, r=45, c="FireBrick")
                actors.append(wp_actor)

        if data.collision_cells:
            for cp in data.collision_cells:
                cp_point_actor = vedo.Cross3D(cp, s=0.3 * self.factor, c="p")
                actors.append(cp_point_actor)

        self.plt.show(actors, resetcam=True)

import vedo

from src.platform.control.sim.spoofers.local_grid_image_spoofer import ImageMapViewModel
from src.core.topics import Topics
from src.core.event_system import subscribe


class ImageMapDebugView:
    def __init__(self):
        self.plt = vedo.Plotter(
            axes=13,
            interactive=True,
            resetcam=True,
            title=str(Topics.IMAGE_MAPDEBUG_VIEW),
            pos=(0, 1000),
            N=3,
            size=(3500, 3000),
        )
        self.plt.show(resetcam=True)

        subscribe(str(Topics.IMAGE_MAPDEBUG_VIEW), self.viz_image_map)

    def viz_image_map(self, data: ImageMapViewModel):

        # # upside_down_map_img_data_actor = vedo.Picture(data.upside_down_map_img_data, flip=True)
        # data.upside_down_map_img_data[5:10, 5:50] = 1
        # upside_down_map_img_data_actor = vedo.Picture(data.upside_down_map_img_data)
        # self.plt.at(0).show(upside_down_map_img_data_actor, resetcam=True)

        # # map_img_rotated_actor = vedo.Picture(data.map_img_rotated, flip=True)
        # data.map_img_rotated[5:10, 5:50] = 1
        # map_img_rotated_actor = vedo.Picture(data.map_img_rotated)
        # self.plt.at(1).show(map_img_rotated_actor, resetcam=True)

        # # map_img_axes_alligned_actor = vedo.Picture(
        # #     data.map_img_axes_alligned, flip=True
        # # )
        # data.map_img_axes_alligned[5:10, 5:50] = 1
        # map_img_axes_alligned_actor = vedo.Picture(data.map_img_axes_alligned)
        # self.plt.at(2).show(map_img_axes_alligned_actor, resetcam=True)

        if self.plt.escaped:
            exit()

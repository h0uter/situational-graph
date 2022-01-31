import numpy as np

def img_axes2world_axes(upside_down_map_img):
    map_img_rotated = np.rot90(upside_down_map_img, axes=(1, 0))
    map_img_axes_alligned = np.swapaxes(map_img_rotated, 0, 1)

    return map_img_axes_alligned

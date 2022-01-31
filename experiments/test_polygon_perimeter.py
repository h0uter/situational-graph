from skimage.draw import polygon_perimeter
import numpy as np
img = np.zeros((10, 10), dtype=np.uint8)
rr, cc = polygon_perimeter([5, -1, 5, 10],
                           [-1, 5, 11, 5],
                           shape=img.shape, clip=True)
img[rr, cc] = 1
print(img)
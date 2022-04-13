from matplotlib import pyplot as plt
from src.utils.saving_data_objects import load_something, save_something
import skimage as sk
import numpy as np


def main():
    # lg_img = load_something("lg_img_20220312-162142")
    # lg_img = load_something("lg_img_20220312-162143")
    # lg_img = load_something("lg_img_20220312-162144")
    lg_img = load_something("lg_img_20220312-162146")
    plt.imshow(lg_img)
    plt.show()

    # which function to use depends on how the photo is formatted
    down_sampled_img = sk.measure.block_reduce(lg_img, (10, 10, 1), np.min)
    plt.imshow(down_sampled_img)
    plt.show()


def algo():
    pass
    # init grid
    # invalidate nodes according to obstacles and existing nodes
    # determine optimal frontiers (closest to the edges)
    # find paths to the frontiers
    # sample intermediate frontiers to allow taking corners.
    # so a frontier can be a frontier path...


if __name__ == "__main__":
    main()

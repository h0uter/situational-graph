import time

import matplotlib.pyplot as plt

from src.platform_autonomy.control.real.spot_agent import SpotAgent


### Test functions
def plot_local_grid(grid_img: list):
    # plt.ion()
    plt.imshow(grid_img, origin="lower")
    # plt.pause(0.001)

    plt.show()


def move_demo_usecase():
    spot = SpotAgent(set())

    spot.get_localization()
    time.sleep(5)
    x = 2
    y = 0
    heading = 0.0
    print("I m going to walk")

    spot.move_body_frame((x, y), heading)
    time.sleep(15)
    spot.get_localization()
    print("I have arrived")
    spot.move_body_frame((-x, -y), heading)
    print("Returning")
    spot.get_localization()
    time.sleep(15)


def move_vision_demo_usecase():
    spot = SpotAgent()

    spot.get_localization()
    time.sleep(5)
    x_goal = 0
    y_goal = 0
    heading = 0.0
    print("I m going to walk")
    # spot.move_vision_frame((x_goal,y_goal))
    spot.move_vision_frame((4, 0), np.pi / 2)
    time.sleep(10)
    spot.move_vision_frame((3, 4))

    time.sleep(25)
    spot.get_localization()
    print("I have arrived")
    spot.move_vision_frame((-x_goal, y_goal), 0.0)
    print("Returning")
    spot.get_localization()
    time.sleep(15)


def move_to_sampled_point_usecase():
    spot = SpotAgent()
    time.sleep(7)
    plt.ion()
    plt.show()

    spot.get_localization()
    while True:

        plt.clf()
        grid_img = get_local_grid(spot)
        # plot_local_grid(grid_img)
        plt.imshow(grid_img, origin="lower")
        time.sleep(1)

        lg = LocalGrid((0, 0), grid_img, 3.84, 0.03)
        print(lg)
        frontiers = lg.los_sample_frontiers_on_cellmap(60, 50)
        print(frontiers)

        plt.imshow(grid_img, origin="lower")
        # plt.imshow(grid_img)
        plt.plot(frontiers[:, 0], frontiers[:, 1], "X")
        # plt.show()
        plt.pause(5)

        x, y, z = spot.get_localization()

        x_goal = x + (frontiers[0, 0] - 64) * 0.03
        y_goal = y + (frontiers[0, 1] - 64) * 0.03
        print(f"ima at {x}, {y}, moving to: {x_goal}, {y_goal}")

        spot.move_vision_frame((x_goal, y_goal))
        time.sleep(5)


def movement_square_VISION_test(spot):
    spot.move_vision_frame((0, -6), 0)
    time.sleep(10)
    spot.move_vision_frame((3.5, -6), 0)
    time.sleep(10)
    spot.move_vision_frame((3.5, 0), 0)
    time.sleep(10)
    spot.move_vision_frame((0, 0), 0)
    time.sleep(10)


def movement_square_ODOM_test(spot):
    # spot.move_odom_frame((0, -6), 0)
    spot.move_odom_frame((6, 0), 0)
    time.sleep(10)
    # spot.move_odom_frame((3.5, -6), 0)
    spot.move_odom_frame((6, 3.5), 0)
    time.sleep(10)
    # spot.move_odom_frame((3.5, 0), 0)
    spot.move_odom_frame((0, 3.5), 0)
    time.sleep(10)
    # spot.move_odom_frame((0, 0), 0)
    spot.move_odom_frame((0, 0), 0)
    time.sleep(10)


if __name__ == "__main__":
    # move_demo_usecase()
    # move_vision_demo_usecase()
    # move_to_sampled_point_usecase()

    spot = SpotAgent(set())

    # movement_square_VISION_test(spot)
    # movement_square_ODOM_test(spot)

    spot.move_odom_frame((0, 0), np.pi)

import matplotlib.pyplot as plt
from skimage import draw
import numpy as np

class LocalGrid:
    def __init__(
        self, world_pos: tuple, data: list, length_in_m: float, cell_size_in_m: float
    ):
        self.world_pos = world_pos
        self.data = data
        self.length_in_m = length_in_m
        self.cell_size_in_m = cell_size_in_m
        self.length_num_cells = int(self.length_in_m / self.cell_size_in_m)

        self.pixel_occupied_treshold = 220

        try:
            assert self.data.shape[0:2] == (
                self.length_num_cells,
                self.length_num_cells,
            )
        except:
            print(
                f"ERROR: data.shape = {self.data.shape[0:2]}, length_num_cells = {self.length_num_cells}"
            )
            raise ValueError(
                "The data does not match what is specified in the attributes."
            )

    def is_inside(self, world_pos: tuple) -> bool:
        """
        Check if the world position is inside the local grid.
        """
        if world_pos[0] < self.world_pos[0] - self.length_in_m / 2:
            return False
        if world_pos[0] > self.world_pos[0] + self.length_in_m / 2:
            return False
        if world_pos[1] < self.world_pos[1] - self.length_in_m / 2:
            return False
        if world_pos[1] > self.world_pos[1] + self.length_in_m / 2:
            return False
        return True

    def world_coords2cell_idxs(self, coords: tuple) -> tuple:
        """
        Convert the world coordinates to the cell indices of the local grid.
        """
        x_idx = int(
            (coords[0] - self.world_pos[0] + self.length_in_m / 2) / self.cell_size_in_m
        )
        y_idx = int(
            (coords[1] - self.world_pos[1] + self.length_in_m / 2) / self.cell_size_in_m
        )
        return x_idx, y_idx

    def cell_idx2world_coords(self, idxs: tuple) -> tuple:
        """
        Convert the cell indices to the world coordinates.
        """
        x_coord = (
            self.world_pos[0] + idxs[1] * self.cell_size_in_m - self.length_in_m / 2
        )
        y_coord = (
            self.world_pos[1] + idxs[0] * self.cell_size_in_m - self.length_in_m / 2
        )
        return x_coord, y_coord

    def cell_idxs2world_coords(self, idxs: tuple) -> tuple:
        """
        Convert the cell indices to the world coordinates.
        """
        x_coords = []
        y_coords = []
        for i in range(len(idxs[0])):
            x_coords.append(
                self.world_pos[0] + idxs[1][i] * self.cell_size_in_m - self.length_in_m / 2
            )
            y_coords.append(
                self.world_pos[1] + idxs[0][i] * self.cell_size_in_m - self.length_in_m / 2
            )
        return x_coords, y_coords

    def plot_line_to_points_in_world_coord(self, points: list ) -> None:
        plt.figure(10)
        plt.cla()
        plt.ion()

        plt.imshow(
            self.data,
            origin="lower",
            extent=[
                self.world_pos[0] - self.length_in_m / 2,
                self.world_pos[0] + self.length_in_m / 2,
                self.world_pos[1] - self.length_in_m / 2,
                self.world_pos[1] + self.length_in_m / 2,
            ],
        )
        for point in points:
            # print(f"point = {point}")
            at_cell = self.length_num_cells / 2, self.length_num_cells / 2
            to_cell = self.world_coords2cell_idxs(point)

            self.collision_check_line_between_cells(at_cell, to_cell)
            # rr, cc = self.get_cells_under_line(at_cell, to_cell)
            
            # xx, yy = self.cell_idxs2world_coords((cc, rr))

            # plt.plot(xx, yy, "g")
            plt.plot([self.world_pos[0],point[0]], [self.world_pos[1],point[1]], "g")
            # self.collision_check_line_between_cells(self.world_pos, point)

        plt.show()
        plt.pause(0.001)
        plt.figure(1)

    def get_cells_under_line(self, a: tuple, b: tuple) -> tuple:
        # TODO: check if x and y is correct
        rr, cc = draw.line(int(a[0]), int(a[1]), int(b[0]), int(b[1]))

        return rr, cc

    # TODO: add robot size as parameter to the collision check.
    def collision_check_line_between_cells(self, at: tuple, to: tuple) -> bool:
        '''
        If the path goes through an obstacle, report collision.

        :param data: the occupancy grid
        :param at: the starting point of the line segment
        :param to: the goal location
        :param local_grid_adapter: a LocalGridAdapter object
        :return: A boolean value.
        '''
        rr, cc = self.get_cells_under_line(at, to)
        # print("rrcc",rr,cc)
        # for cell in path, if one of them is an obstacle, resample
        # plt.figure(12)
        # plt.imshow(self.data, origin="lower")
        # plt.figure(10)
        for r, c in zip(rr, cc):
            # if np.less(self.data[r, c], [self.pixel_occupied_treshold, self.pixel_occupied_treshold, self.pixel_occupied_treshold, self.pixel_occupied_treshold]).any():
            if np.less(self.data[c, r], [self.pixel_occupied_treshold, self.pixel_occupied_treshold, self.pixel_occupied_treshold, self.pixel_occupied_treshold]).any():
                # print(f" self.data[r, c] = {self.data[r, c]}")
                # x = c
                # x = self.world_pos[0] + c
                # y = r
                # y = self.world_pos[1] + y
                # self.plot_collision_cell_map(data, r, c, to, at)
                # plt.plot(r, c, marker='s', color='red', markersize=10)
                x, y = self.cell_idx2world_coords((c, r))
                # print(f"Collision at x:{x}, y:{y}")
                # print(f"Collision at r:{r}, c:{c}")
                plt.plot(x, y, marker='s', color='red', markersize=10)
                return False
        return True
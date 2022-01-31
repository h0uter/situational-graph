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

    def viz_collision_line_to_points_in_world_coord(self, points: list ) -> None:
        
        # ax2 = plt.subplot(1,2,2)

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
            at_cell = self.length_num_cells / 2, self.length_num_cells / 2
            to_cell = self.world_coords2cell_idxs(point)

            # rr, cc = self.get_cells_under_line(at_cell, to_cell)
            # xx, yy = self.cell_idxs2world_coords((cc, rr))
            # plt.plot(xx, yy, "g")

            # ax2.plot([self.world_pos[0],point[0]], [self.world_pos[1],point[1]], "g")
            plt.plot([self.world_pos[0],point[0]], [self.world_pos[1],point[1]], color="orange")
            plt.plot(
                point[0],
                point[1],
                marker="o",
                markersize=10,
                color="red",
            )
            self.is_collision_free_straight_line_between_cells(at_cell, to_cell)
        
        plt.plot(
            self.world_pos[0],
            self.world_pos[1],
            marker="o",
            markersize=10,
            color="blue",
        )

        fig = plt.gcf()
        fig.axes[1].set_title("local grid sampling of shortcuts")

        plt.show()
        plt.pause(0.001)
        # plt.figure(1)

    def get_cells_under_line(self, a: tuple, b: tuple) -> tuple:
        rr, cc = draw.line(int(a[0]), int(a[1]), int(b[0]), int(b[1]))

        return rr, cc

    # TODO: add robot size as parameter to the collision check.
    def is_collision_free_straight_line_between_cells(self, at: tuple, to: tuple) -> bool:
        rr, cc = self.get_cells_under_line(at, to)
        for r, c in zip(rr, cc):
            if np.less(self.data[c, r], [self.pixel_occupied_treshold, self.pixel_occupied_treshold, self.pixel_occupied_treshold, self.pixel_occupied_treshold]).any():
                x, y = self.cell_idx2world_coords((c, r))
                plt.plot(x, y, marker='X', color='red', markersize=20)
                return False
        return True

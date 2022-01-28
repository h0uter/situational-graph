import matplotlib.pyplot as plt
from skimage import draw


class LocalGrid:
    def __init__(
        self, world_pos: tuple, data: list, length_in_m: float, cell_size_in_m: float
    ):
        self.world_pos = world_pos
        self.data = data
        self.length_in_m = length_in_m
        self.cell_size_in_m = cell_size_in_m
        self.length_num_cells = int(self.length_in_m / self.cell_size_in_m)

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

    def cell_idxs2world_coords(self, idxs: tuple) -> tuple:
        """
        Convert the cell indices to the world coordinates.
        """
        x_coord = (
            self.world_pos[0] + idxs[0] * self.cell_size_in_m - self.length_in_m / 2
        )
        y_coord = (
            self.world_pos[1] + idxs[1] * self.cell_size_in_m - self.length_in_m / 2
        )
        return x_coord, y_coord

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
            rr, cc = self.get_cells_under_line(
                point, (self.world_pos[0], self.world_pos[1])
            )
            plt.plot(rr, cc, "r")

        plt.show()
        plt.pause(0.001)
        plt.figure(1)

    def get_cells_under_line(self, a: tuple, b: tuple) -> tuple:
        # TODO: check if x and y is correct
        rr, cc = draw.line(int(a[0]), int(a[1]), int(b[0]), int(b[1]))

        return rr, cc

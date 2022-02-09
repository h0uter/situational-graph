from matplotlib import pyplot as plt
from skimage import draw
import numpy as np
# import numpy.typing as npt

from config import Configuration

class LocalGrid:

    def __init__(
        self, world_pos: tuple, data: list, length_in_m: float, cell_size_in_m: float
        # self, world_pos: tuple, data: npt.ArrayLike, length_in_m: float, cell_size_in_m: float
    ):

        self.world_pos = world_pos
        self.data = data
        self.length_in_m = length_in_m
        self.cell_size_in_m = cell_size_in_m
        self.length_num_cells = int(self.length_in_m / self.cell_size_in_m)

        self.pixel_occupied_treshold = 220
        self.sample_ring_width = Configuration().sample_ring_width

        if not self.data.shape[0:2] == (self.length_num_cells, self.length_num_cells):
            print(
                f"ERROR: data.shape = {self.data.shape[0:2]}, length_num_cells = {self.length_num_cells}"
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

    # TODO: optimize this function for speed
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

    def get_cells_under_line(self, a: tuple, b: tuple) -> tuple:
        rr, cc = draw.line(int(a[0]), int(a[1]), int(b[0]), int(b[1]))

        return rr, cc

    # TODO: add robot size as parameter to the collision check.
    def is_collision_free_straight_line_between_cells(self, at: tuple, to: tuple) -> bool:

        type_of_img = "spot_obstacle_map"

        if type_of_img == "spot_obstacle_map":
            # FIXME: spot obstacle map has rr and cc flipped somehow
            rr, cc = self.get_cells_under_line(at, to)
            # print(f"rr: {rr}")
            # print(f"cc: {cc}")
            for r, c in zip(rr, cc):
                # if np.less(self.data[c, r][0:2], [self.pixel_occupied_treshold, self.pixel_occupied_treshold]).any():
                # if np.greater(self.data[c, r][0:2], [self.pixel_occupied_treshold, self.pixel_occupied_treshold]).any():
                if np.greater(self.data[r, c][0:2], [self.pixel_occupied_treshold, self.pixel_occupied_treshold]).any():
                    x, y = self.cell_idx2world_coords((c, r))
                    collision_point = (x, y)
                    print(f"collision at : {collision_point}")
                    # collision at : (0.0, 0.0)

                    return False, collision_point
            return True, None
        else:
            rr, cc = self.get_cells_under_line(at, to)
            for r, c in zip(rr, cc):
                if np.less(self.data[c, r], [self.pixel_occupied_treshold, self.pixel_occupied_treshold, self.pixel_occupied_treshold, self.pixel_occupied_treshold]).any():
                    x, y = self.cell_idx2world_coords((c, r))
                    collision_point = (x, y)

                    return False, collision_point
            return True, None


    def sample_cell_around_other_cell(self, x: int, y: int, radius: int) -> tuple:
        sample_valid = False

        while not sample_valid:
            r = radius * np.sqrt(np.random.uniform(low=1 -
                                                   self.sample_ring_width, high=1))
            theta = np.random.random() * 2 * np.pi

            x_sample = int(x + r * np.cos(theta))
            y_sample = int(y + r * np.sin(theta))
            # print("samples taken")
            # plt.plot(x, y, "ro")
            # plt.plot(x_sample, y_sample, 'go')
            # plt.show()

            sample_valid, _ = self.is_collision_free_straight_line_between_cells(
                at=(x, y),
                to=(x_sample, y_sample),
            )

        return x_sample, y_sample

    def sample_frontiers_on_cellmap(self, radius: int, num_frontiers_to_sample: int) -> list:
        '''
        Given a local grid, sample N points around a given point, and return the sampled points.
        '''
        candidate_frontiers = []
        while len(candidate_frontiers) < num_frontiers_to_sample:
            x_center = self.length_num_cells // 2
            y_center = self.length_num_cells // 2

            #debugs
            # plt.plot(x_center, y_center)

            x_sample, y_sample = self.sample_cell_around_other_cell(
                x_center,
                y_center,
                radius=radius,
            )

            candidate_frontiers.append((y_sample, x_sample))
            # candidate_frontiers.append((x_sample, y_sample))

        candidate_frontiers = np.array(candidate_frontiers).astype(np.int)

        return candidate_frontiers

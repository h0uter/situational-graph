from copy import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from skimage import draw

from knowledge_roadmap.entities.agent import Agent

EMPTY_CELL = 0
OBSTACLE_CELL = 1
FRONTIER_CELL = 2
GOAL_CELL = 3
MOVE_CELL = 4

class Sampler():
    def __init__(self, cell_size, num_cells, debug_mode=False) -> None:
        self.cell_size = cell_size
        self.num_cells = num_cells
        self.init = False
        self.debug = debug_mode

    def init_plot(self, data) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.ion()

        ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=1)
        ax.set_xticks(np.arange(0.5, data.shape[0], 1))
        ax.set_yticks(np.arange(0.5, data.shape[0], 1))
        plt.tick_params(axis='both', which='both', bottom=False,   
                    left=False, labelbottom=False, labelleft=False) 

        EMPTY_CELL = 0
        OBSTACLE_CELL = 1
        FRONTIER_CELL = 2
        GOAL_CELL = 3
        MOVE_CELL = 4

        self.cmap = colors.ListedColormap(['white', 'black', 'green', 'red', 'blue'])
        self.bounds = [EMPTY_CELL, OBSTACLE_CELL, FRONTIER_CELL, GOAL_CELL, MOVE_CELL, MOVE_CELL + 1]
        self.norm = colors.BoundaryNorm(self.bounds, self.cmap.N)
        # DONT fuck with extent it causes aliasing problems
        plt.imshow( 
            data, 
            cmap = self.cmap , 
            norm= self.norm,
            )

        plt.show()
        plt.pause(0.001)

    def draw_grid(self, data) -> None:
        if not self.init:
            self.init_plot(data)
            self.init = True

        plt.imshow( 
            data, 
            cmap = self.cmap , 
            norm = self.norm,
            origin='lower',
            )
        plt.show()
        plt.pause(0.001)

    def draw_line(self, x1, y1, x2, y2) -> None:
        plt.plot([x1, x2], [y1, y2], marker='s', color='blue')


    def get_cells_under_line(self, point_a, point_b):  
        # TODO: check if x and y is correct
        rr, cc = draw.line(point_a[0], point_a[1], point_b[0], point_b[1])

        return rr, cc

    def pix_idx2world_coord(self, img, x_idx, y_idx):
            # FIXME: this has to be linked to the x and y offset in the gui
            x_map_length_scale = 300
            y_map_length_scale = 300

            Nx_pix = img.shape[0]
            Ny_pix = img.shape[1]

            x_origin_meter_offset = x_map_length_scale // 2
            y_origin_meter_offset = y_map_length_scale // 2

            x_meter_per_pix = x_map_length_scale / Nx_pix
            y_meter_per_pix = y_map_length_scale / Ny_pix

            x_meter = x_idx * x_meter_per_pix
            y_meter = y_idx * y_meter_per_pix
            
            return x_meter, y_meter

    def plot_collision(self, data, r, c, to, at):
        plt.figure(9)
        x_meter, y_meter = self.pix_idx2world_coord(data, c, r)

        plt.cla()
        plt.ion()
        plt.imshow(data, origin='lower')
        *at_meters, = self.pix_idx2world_coord(data, at[1], at[0])
        *to_meters, = self.pix_idx2world_coord(data, to[1], to[0])
        print(at_meters)
        plt.plot([at_meters[0], to_meters[0]], [at_meters[1], to_meters[1]], color='green')
        plt.plot(x_meter, y_meter, marker='s', color='red', markersize=10)
        plt.pause(0.001)
        plt.figure(1)

    # TODO: add robot size as parameter to the collision check.
    def collision_check(self, data, at, to):
        rr, cc = self.get_cells_under_line(at, to)
        
        # for cell in path, if one of them is an obstacle, resample
        for r, c in zip(rr, cc):
            if np.less(data[r,c], [230, 230, 230, 230]).any():
                if self.debug:
                    print(f"Collision at {r}, {c}")
                    self.plot_collision(data, r, c, to, at)

                return False  
        return True

    def sample_point_around_other_point(self, x, y, radius, data):
        valid_sample = False

        while not valid_sample:
            r = radius * np.sqrt(np.random.uniform(low=1, high=2.2))
            theta = np.random.random() * 2 * np.pi

            x_sample = int(x + r * np.cos(theta))
            y_sample = int(y + r * np.sin(theta))

            valid_sample = self.collision_check(data=data, at=(x, y), to=(x_sample, y_sample))

        return x_sample, y_sample

    def sample_frontiers(self, local_grid, grid_size, radius=90, num_frontiers_to_sample=5) -> list:
        candidate_frontiers = []
        while len(candidate_frontiers) < num_frontiers_to_sample:
            x_center = grid_size
            y_center = grid_size

            x_sample, y_sample = self.sample_point_around_other_point(x_center, y_center, radius=radius, data=local_grid)
            
            # BUG: why the hell is this y,x ....
            x_sample, y_sample = self.pix_idx2world_coord(local_grid, y_sample, x_sample)
            
            candidate_frontiers.append((x_sample, y_sample))
        
        return candidate_frontiers
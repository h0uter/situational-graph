from copy import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from skimage import draw

from src.entities.agent import Agent

EMPTY_CELL = 0
OBSTACLE_CELL = 1
FRONTIER_CELL = 2
GOAL_CELL = 3
MOVE_CELL = 4

class Sampler():


    def __init__(self, cell_size, num_cells) -> None:
        self.cell_size = cell_size
        self.num_cells = num_cells
        self.init = False

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

            # x_meter = r * x_meter_per_pix + x_origin_meter_offset
            x_meter = x_idx * x_meter_per_pix
            # y_meter = c * y_meter_per_pix + y_origin_meter_offset
            y_meter = y_idx * y_meter_per_pix
            
            return x_meter, y_meter

    # TODO: add robot size as parameter to the collision check.
    def collision_check(self, data, at, to):
        rr, cc = self.get_cells_under_line(at, to)
        
        # for cell in path, if one of them is an obstacle, resample
        for r, c in zip(rr, cc):
            # if data[r,c] == 1 :
            # if np.less(data[r,c], [230, 230, 230, 230]).any():
            if np.less(data[r,c], [100, 100, 100, 100]).any():
                # print(f" hello data {data[r,c]}")
                # print(f"Collision at {r}, {c}")

                # x_meter, y_meter = self.pix_idx2world_coord(data, c, r)
                # x_meter, y_meter = self.pix_idx2world_coord(data, r, c)
                # print(f"Collision at {x_meter}, {y_meter} meters")

                # plt.figure(6)
                # plt.cla()
                # plt.ion()
                # plt.imshow(data, origin='lower')
                # *at_meters, = self.pix_idx2world_coord(data, at[0], at[1])
                # # *to_meters, = self.pix_idx2world_coord(data, to[0], to[1])
                # *to_meters, = self.pix_idx2world_coord(data, to[1], to[0])
                # print(at_meters)
                # plt.plot([at_meters[0], to_meters[0]], [at_meters[1], to_meters[1]], color='green')
                # plt.plot(x_meter, y_meter, marker='s', color='red', markersize=10)
                # # plt.show()
                # # plt.figure(9)
                # # data2 = copy(data)
                # # data2[0:100, 5:10, 0] = 250
                # # data2[0:100, 5:10, 1] = 0
                # # data2[0:100, 5:10, 2] = 0
                # # plt.imshow(data2, origin='lower')
                # # x_meter1, y_meter1 = self.pix_idx2world_coord(data, 5, 100)
                # # x_meter2, y_meter2 = self.pix_idx2world_coord(data, 200, 100)

                # # plt.plot([x_meter1, x_meter2], [y_meter1, y_meter2], color='blue')
                # # plt.show()
                # # plt.pause(0.001)
                # plt.figure(1)

                return False  


        return True


    def sample_point_around_other_point(self, x, y, radius, data):
        valid_sample = False
        inner_radius = radius // 2
        while not valid_sample:

            r = radius * np.sqrt(np.random.uniform(low=1, high=2.2))
            theta = np.random.random() * 2 * np.pi

            x_sample = int(x + r * np.cos(theta))
            y_sample = int(y + r * np.sin(theta))
            print(f"x_sample {x_sample} y_sample {y_sample}")

            # # x_sample = np.random.randint(low=x-radius, high=x+radius) 
            # x_sample = x + np.random.randint(low=inner_radius, high=radius) * np.random.choice([-1, 1])
            # # y_sample = np.random.randint(low=y-radius, high=y+radius) 
            # y_sample = y + np.random.randint(low=inner_radius, high=radius) * np.random.choice([-1, 1])
            
            valid_sample = self.collision_check(data=data, at=(x, y), to=(x_sample, y_sample))

        # plt.figure(6)
        # plt.clf()
        # plt.imshow(data, origin='lower')
        # plt.plot([x, x_sample], [y, y_sample], marker='s', color='green')
        # plt.show()
        # plt.pause(0.001)
        return x_sample, y_sample

    def sample_frontiers(self, agent: Agent, local_grid, grid_size, cell_size=1) -> list:
        candidate_frontiers = []
        while len(candidate_frontiers) < 20:
            corrected_x = grid_size
            # corrected_x = agent.pos[0] + grid_size
            corrected_y = grid_size
            # corrected_y = agent.pos[1] + grid_size
            # corrected_x, corrected_y = self.pix_idx2world_coord(local_grid, agent.pos[0], agent.pos[1])
            # corrected_x = int(corrected_x)
            # corrected_y = int(corrected_y)
            # x_sample, y_sample = self.sample_point_around_other_point(agent.pos[0], agent.pos[1], radius=100, data=local_grid)
            x_sample, y_sample = self.sample_point_around_other_point(corrected_x, corrected_y, radius=60, data=local_grid)
            # x_sample, y_sample = self.pix_idx2world_coord(local_grid, x_sample, y_sample)
            x_sample, y_sample = self.pix_idx2world_coord(local_grid, y_sample, x_sample)
            
            candidate_frontiers.append((x_sample, y_sample))
        
        # THESE FRONTIERS ARE WRONG
        return candidate_frontiers


# if __name__ == '__main__':

    # EMPTY_CELL = 0
    # OBSTACLE_CELL = 1
    # FRONTIER_CELL = 2
    # GOAL_CELL = 3
    # MOVE_CELL = 4
    
#     cell_size = 1
#     num_cells = 150
#     two_times_num_cells = int(num_cells*2)
#     # x_prev, y_prev = num_cells, num_cells
#     x_prev, y_prev = 5, 5

#     empty_data = np.zeros((two_times_num_cells, two_times_num_cells))
#     data = empty_data

#     # add a boundary to the local grid
#     rr, cc = draw.rectangle_perimeter((2,2), (two_times_num_cells-5, two_times_num_cells-5), shape=data.shape)
#     data[rr,cc] = 1

#     local_grid = GridPlotter(cell_size, num_cells)
#     local_grid.draw_grid(data)


#     for i in range(10):
#         x_sample, y_sample = local_grid.sample_point_around_other_point(x_prev, y_prev, radius=20, data=data)
#         print(f"Sampled point: {x_sample}, {y_sample}")
#         # local_grid.draw_line(x_prev, y_prev, x_sample, y_sample)
#         # x_prev, y_prev = x_sample, y_sample
#         data[y_sample, x_sample] = FRONTIER_CELL

#     plt.ioff()
#     plt.plot(x_prev, y_prev, marker='s', color='red', linestyle='none')
#     local_grid.draw_grid(data)



#     # while True:

#     #     x, y = local_grid.sample_point_around_other_point(x_prev, y_prev, 5, data)
#     #     # local_grid.collision_check(data, (x_prev, y_prev), (x, y))
#     #     # data[0,0] = 5
#     #     plt.plot(x, y, marker='s', color='red', linestyle='none')
#     #     local_grid.draw_grid(data)
#     #     # local_grid.collision_check(data, (x_prev, y_prev), (x, y))
#     #     data[y,x] = 3
#     #     x_prev, y_prev = x, y



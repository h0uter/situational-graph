import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from skimage import draw

EMPTY_CELL = 0
OBSTACLE_CELL = 1
FRONTIER_CELL = 2
GOAL_CELL = 3
MOVE_CELL = 4

class GridPlotter():


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
        rr, cc = draw.line(point_a[0], point_a[1], point_b[0], point_b[1])

        return rr, cc


    # TODO: add robot size as parameter to the collision check.
    def collision_check(self, data, at, to):
        rr, cc = self.get_cells_under_line(at, to)

        # for cell in path, if one of them is an obstacle, resample
        for r, c in zip(rr, cc):
            if data[r,c] == 1 :
                print(f"Collision at {r}, {c}")
                return False  

        plt.plot(rr, cc, marker='s', color='green')

        return True


    def sample_point_around_other_point(self, x, y, radius, data):
        valid_sample = False
        while not valid_sample:
            x_sample = np.random.randint(low=x-radius, high=x+radius)
            y_sample = np.random.randint(low=y-radius, high=y+radius)
            valid_sample = self.collision_check(data=data, at=(x_sample, y_sample), to=(x, y))

        return x_sample, y_sample

if __name__ == '__main__':
    
    cell_size = 1
    num_cells = 15
    two_times_num_cells = int(num_cells*2)
    # x_prev, y_prev = num_cells, num_cells
    x_prev, y_prev = 5, 5

    empty_data = np.zeros((two_times_num_cells, two_times_num_cells))
    data = empty_data

    # add a boundary to the local grid
    rr, cc = draw.rectangle_perimeter((2,2), (two_times_num_cells-5, two_times_num_cells-5), shape=data.shape)
    data[rr,cc] = 1

    local_grid = GridPlotter(cell_size, num_cells)
    local_grid.draw_grid(data)



    for i in range(10):
        x_sample, y_sample = local_grid.sample_point_around_other_point(x_prev, y_prev, radius=20, data=data)
        print(f"Sampled point: {x_sample}, {y_sample}")
        # local_grid.draw_line(x_prev, y_prev, x_sample, y_sample)
        # x_prev, y_prev = x_sample, y_sample
        data[y_sample, x_sample] = FRONTIER_CELL

    plt.ioff()
    plt.plot(x_prev, y_prev, marker='s', color='red', linestyle='none')
    local_grid.draw_grid(data)



    # while True:

    #     x, y = local_grid.sample_point_around_other_point(x_prev, y_prev, 5, data)
    #     # local_grid.collision_check(data, (x_prev, y_prev), (x, y))
    #     # data[0,0] = 5
    #     plt.plot(x, y, marker='s', color='red', linestyle='none')
    #     local_grid.draw_grid(data)
    #     # local_grid.collision_check(data, (x_prev, y_prev), (x, y))
    #     data[y,x] = 3
    #     x_prev, y_prev = x, y



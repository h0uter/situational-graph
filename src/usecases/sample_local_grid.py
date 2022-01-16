import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

# class LocalGridCoordBased():
#     def __init__(self) -> None:
        
#         xvalues = np.array([range(-25, 26)])
#         yvalues = np.array([range(-25, 26)])
#         self.xx, self.yy = np.meshgrid(xvalues, yvalues)

#         fig = plt.figure()
#         ax = fig.add_subplot(111)
#         size = 300
#         plt.xlim(-size, size)
#         plt.ylim(-size, size)
#         ax.set_aspect('equal', adjustable='box')

#         plt.plot(self.xx, self.yy, marker='s', color='grey', linestyle='none')
    
#     def sample_point_on_grid(self):
#         x_sample = np.random.randint(low=np.min(self.xx[0]), high=np.max(self.xx[0]),)
#         y_sample = np.random.randint(low=np.min(self.yy[:,0]), high=np.max(self.yy[:,0]))
#         return x_sample, y_sample

#     def draw_line(self, x1, y1, x2, y2):
#         plt.plot([x1, x2], [y1, y2], marker='s', color='blue')

#     def sample_point_around_other_point(self, x, y, radius):
#         x_sample = np.random.randint(low=x-radius, high=x+radius)
#         y_sample = np.random.randint(low=y-radius, high=y+radius)
#         return x_sample, y_sample
    

class GridPlotter():
    def __init__(self, data) -> None:
        self.init_plot(data)

    def init_plot(self, data) -> None:
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=1)
        ax.set_xticks(np.arange(0.5, size2, 1))
        ax.set_yticks(np.arange(0.5, size2, 1))
        plt.tick_params(axis='both', which='both', bottom=False,   
                    left=False, labelbottom=False, labelleft=False) 

        EMPTY_CELL = 0
        OBSTACLE_CELL = 1
        START_CELL = 2
        GOAL_CELL = 3
        MOVE_CELL = 4
        self.cmap = colors.ListedColormap(['white', 'black', 'green', 'red', 'blue'])
        self.bounds = [EMPTY_CELL, OBSTACLE_CELL, START_CELL, GOAL_CELL, MOVE_CELL ,MOVE_CELL + 1]
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
        plt.imshow( 
            data, 
            cmap = self.cmap , 
            norm = self.norm,
            )
        plt.show()
        plt.pause(0.001)

    def draw_line(self, x1, y1, x2, y2) -> None:
        plt.plot([x1, x2], [y1, y2], marker='s', color='blue')

    def sample_point_around_other_point(self, x, y, radius):
        x_sample = np.random.randint(low=x-radius, high=x+radius)
        y_sample = np.random.randint(low=y-radius, high=y+radius)
        return x_sample, y_sample


if __name__ == '__main__':
    size = 15
    size2 = int(size*2)
    x_prev, y_prev = size, size
    empty_data = np.zeros((size2, size2))
    local_grid = GridPlotter(empty_data)

    data = empty_data
    while True:

        x, y = local_grid.sample_point_around_other_point(x_prev, y_prev, 5)
        local_grid.draw_line(x_prev, y_prev, x, y)
        plt.plot(x, y, marker='s', color='red', linestyle='none')
        data[y,x] = 4
        local_grid.draw_grid(data)
        x_prev, y_prev = x, y



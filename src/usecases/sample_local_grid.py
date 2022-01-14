from threading import local
from turtle import color
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

class LocalGrid():
    def __init__(self) -> None:
        
        xvalues = np.array([range(-25, 26)])
        yvalues = np.array([range(-25, 26)])
        self.xx, self.yy = np.meshgrid(xvalues, yvalues)

        # self.occupancy_grid = np.array([xx, yy])
        # plt.grid(b=True, which='both', color='k', linestyle='-')

        fig = plt.figure()
        ax = fig.add_subplot(111)
        size = 300
        plt.xlim(-size, size)
        plt.ylim(-size, size)
        ax.set_aspect('equal', adjustable='box')

        plt.plot(self.xx, self.yy, marker='s', color='grey', linestyle='none')
    
    def sample_point_on_grid(self):
        # print(self.yy[:,0])
        # print(np.min(self.yy[:,0]))
        # print(np.max(self.yy[:,0]))
        x_sample = np.random.randint(low=np.min(self.xx[0]), high=np.max(self.xx[0]),)
        y_sample = np.random.randint(low=np.min(self.yy[:,0]), high=np.max(self.yy[:,0]))
        return x_sample, y_sample

    def draw_line(self, x1, y1, x2, y2):
        plt.plot([x1, x2], [y1, y2], marker='s', color='blue')

    def sample_point_around_other_point(self, x, y, radius):
        x_sample = np.random.randint(low=x-radius, high=x+radius)
        y_sample = np.random.randint(low=y-radius, high=y+radius)
        return x_sample, y_sample
    
    

def color_map():
    # random data
    x = np.random.randint(0, 1 +1, (10, 10))

    fig, ax = plt.subplots()

    # define the colors
    cmap = mpl.colors.ListedColormap(['r', 'k'])

    # create a normalize object the describes the limits of
    # each color
    bounds = [0., 0.5, 1.]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    # plot it
    ax.imshow(x, interpolation='none', cmap=cmap, norm=norm)
    plt.show()

def color_map2():
    # Program to plot 2-D Heat map
    # using matplotlib.pyplot.imshow() method

    data = np.random.random(( 12 , 12 ))
    print(data)
    plt.imshow( data , cmap = 'autumn' , interpolation = 'nearest' )
    
    plt.title( "2-D Heat Map" )
    plt.show()


if __name__ == '__main__':

    # plt.ion()
    # local_grid = LocalGrid()
    # # x_prev, y_prev = 0, 0
    # x_prev, y_prev = local_grid.sample_point_on_grid()

    # while True:
    # # print(local_grid.occupancy_grid)

    #     x, y = local_grid.sample_point_around_other_point(x_prev, y_prev, 5)
    #     local_grid.draw_line(x_prev, y_prev, x, y)
    #     plt.plot(x, y, marker='s', color='red', linestyle='none')
    #     x_prev, y_prev = x, y
    #     plt.pause(0.001)
    #     plt.show()

    # color_map()
    color_map2()

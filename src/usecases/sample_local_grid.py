from threading import local
import numpy as np
import matplotlib.pyplot as plt

class LocalGrid():
    def __init__(self) -> None:
        
        xvalues = np.array([range(-25, 26)])
        yvalues = np.array([range(-25, 26)])
        self.xx, self.yy = np.meshgrid(xvalues, yvalues)

        # self.occupancy_grid = np.array([xx, yy])
        plt.plot(self.xx, self.yy, marker='.', color='grey', linestyle='none')
        # plt.grid(b=True, which='both', color='k', linestyle='-')

    
    def sample_point_on_grid(self):
        print(self.yy[:,0])
        print(np.min(self.yy[:,0]))
        print(np.max(self.yy[:,0]))
        x_sample = np.random.randint(low=np.min(self.xx[0]), high=np.max(self.xx[0]),)
        y_sample = np.random.randint(low=np.min(self.yy[:,0]), high=np.max(self.yy[:,0]))
        plt.plot(x_sample, y_sample, marker='.', color='red', linestyle='none')

    
    
if __name__ == '__main__':

    local_grid = LocalGrid()
    # print(local_grid.occupancy_grid)
    local_grid.sample_point_on_grid()
    plt.show()
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import random

EMPTY_CELL = 0
OBSTACLE_CELL = 1
START_CELL = 2
GOAL_CELL = 3
MOVE_CELL = 4
# create discrete colormap
cmap = colors.ListedColormap(['white', 'black', 'green', 'red', 'blue'])
bounds = [EMPTY_CELL, OBSTACLE_CELL, START_CELL, GOAL_CELL, MOVE_CELL ,MOVE_CELL + 1]
norm = colors.BoundaryNorm(bounds, cmap.N)

def plot_grid(data, saveImageName):

    fig, ax = plt.subplots()
    ax.imshow(data, cmap=cmap, norm=norm)
    # draw gridlines
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=1)
    ax.set_xticks(np.arange(0.5, rows, 1))
    ax.set_yticks(np.arange(0.5, cols, 1))
    plt.tick_params(axis='both', labelsize=0, length = 0)
    # fig.set_size_inches((8.5, 11), forward=False)
    # plt.savefig(saveImageName + ".png", dpi=500)

def generate_moves(grid, startX, startY):
    num_rows = np.size(grid, 0)
    num_cols = np.size(grid, 1)

    # Currently do not support moving diagonally so there is a max
    # of 4 possible moves, up, down, left, right.
    possible_moves = np.zeros(8, dtype=int).reshape(4, 2)
    # Move up
    possible_moves[0, 0] = startX - 1
    possible_moves[0, 1] = startY
    # Move down
    possible_moves[1, 0] = startX + 1
    possible_moves[1, 1] = startY
    # Move left
    possible_moves[2, 0] = startX
    possible_moves[2, 1] = startY - 1
    # Move right
    possible_moves[3, 0] = startX
    possible_moves[3, 1] = startY + 1
    # Change the cell value if the move is valid
    for row in possible_moves:
        if row[0] < 0 or row[0] >= num_rows:
            continue
        if row[1] < 0 or row[1] >= num_cols:
            continue
        grid[row[0], row[1]] = MOVE_CELL        

if __name__ == "__main__":
    rows = 20
    cols = 20
    # Randomly create 20 different grids
    for i in range(0, 20):

        data = np.zeros(rows * cols).reshape(rows, cols)
        start_x = random.randint(0, rows - 1)
        start_y = random.randint(0, cols - 1)
        data[start_x, start_y] = START_CELL

        goal_x = random.randint(0, rows - 1)
        # Dont want the start and end positions to be the same
        # so keep changing the goal x until its different. 
        # If X is different dont need to check Y
        while goal_x is start_x:
            goal_x = random.randint(0, rows - 1)
        goal_y = random.randint(0, cols - 1)

        data[goal_x, goal_y] = GOAL_CELL
        generate_moves(data, start_x, start_y)
        plot_grid(data, "week1/images/grid_" + str(i))
        plt.show()
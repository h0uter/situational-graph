import os
import logging
import sys

class Configuration:
    def __init__(self):

        self.type_of_img = None

        # case ="maze"
        case ="villa"
        # case ="spot"

        if case == "villa":
            self.full_path = os.path.join("resource", "villa_holes_closed.png")
            self.total_map_len_m_x = 50
            self.img_total_x_pix = 2026
            self.img_total_y_pix = 1686
            self.lg_num_cells = 420  # max:400 due to img border margins
            self.agent_start_pos = (-9, 13)
            self.total_map_len_m_y = (
                self.total_map_len_m_x / self.img_total_x_pix
                ) * self.img_total_y_pix  # zo klopt het met de foto verhoudingen (square cells)
            self.total_map_len_m = (self.total_map_len_m_x, self.total_map_len_m_y)
            self.lg_cell_size_m = self.total_map_len_m_x / self.img_total_x_pix

        elif case == "maze":
            self.full_path = os.path.join('resource', 'simple_maze2_border_closed.png')
            self.total_map_len_m_x = 73
            self.img_total_x_pix = 2000
            self.img_total_y_pix = 1000
            self.lg_num_cells = 300  # max:400 due to img border margins
            self.agent_start_pos = (-2, 0)
            self.total_map_len_m_y = (
            self.total_map_len_m_x / self.img_total_x_pix
                ) * self.img_total_y_pix  # zo klopt het met de foto verhoudingen (square cells)
            self.total_map_len_m = (self.total_map_len_m_x, self.total_map_len_m_y)
            self.lg_cell_size_m = self.total_map_len_m_x / self.img_total_x_pix

        elif case == "spot":
            self.type_of_img = "spot_obstacle_map" # FIXME: this is a hack to get the spot agent working
            self.lg_num_cells = 128  # max:400 due to img border margins
            self.lg_cell_size_m = 0.03
            self.full_path = None

 
        self.lg_length_in_m = self.lg_num_cells * self.lg_cell_size_m

        # exploration hyperparameters
        self.N_samples = 25
        self.prune_radius = self.lg_length_in_m * 0.25
        self.sample_ring_width = 0.9

        # logging
        my_logger = logging.getLogger(__name__)
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)

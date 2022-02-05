import os

class Configuration:
    def __init__(self):
        self.img_total_x_pix = 2026
        # self.img_total_x_pix = 1500
        self.img_total_y_pix = 1686
        # self.img_total_y_pix = 500
        self.total_map_len_m_x = 50
        # self.total_map_len_m_x = 73
        # self.total_map_len_m_x = 17 # BUG: completely broken on different length scales
        # self.total_map_len_m_y = 13
        # self.total_map_len_m_y = 40
        self.total_map_len_m_y = (
            self.total_map_len_m_x / self.img_total_x_pix
        ) * self.img_total_y_pix  # zo klopt het met de foto verhoudingen (square cells)
        self.total_map_len_m = (self.total_map_len_m_x, self.total_map_len_m_y)
        self.lg_num_cells = 420  # max:400 due to img border margins
        # self.lg_num_cells = 150  # max:400 due to img border margins
        self.lg_cell_size_m = self.total_map_len_m_x / self.img_total_x_pix
        self.lg_length_in_m = self.lg_num_cells * self.lg_cell_size_m
        self.agent_start_pos = (-9, 13)
        # self.agent_start_pos = (-2, 0)
        self.full_path = os.path.join("resource", "villa_holes_closed.png")
        # full_path = os.path.join('resource', 'simple_maze2.png')
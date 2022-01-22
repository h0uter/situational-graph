
from knowledge_roadmap.data_providers.manual_graph_world import ManualGraphWorld
# from knowledge_roadmap.utils.coordinate_transforms import img_axes2world_axes



class LocalGridAdapter():
    def __init__(self, map_length_scales, mode='spoof', size_pix=150, cell_size=1,debug_container=None):
        self.mode = mode
        self.size_pix = size_pix
        self.cell_size = cell_size
        self.map_length_scales = map_length_scales
        self.debug_container = debug_container

    def get_local_grid(self):

        if self.mode == 'spoof':
            agent_pos = self.debug_container['agent'].pos
            img_world = ManualGraphWorld()
            
            return self.sim_observe_local_grid_from_img_world(agent_pos, img_world)
        else:
            # here comes calls to the spot API
            raise NotImplementedError
            
    def sim_observe_local_grid_from_img_world(self, agent_pos, world):
        '''crops the image around pos with size'''
        x, y = agent_pos # world coords
        x, y = self.world_coord2pix_idx(world, x,y)
        size_in_pix = self.size_pix
        # BUG:: cannot sample near edge of the image world_img.
        local_grid = world.map_img[int(y-size_in_pix):int(y+size_in_pix), int(x-size_in_pix):int(x+size_in_pix)]
        
        return local_grid


    def world_coord2pix_idx(self, world, x_pos, y_pos):
        '''converts world coordinates to image pixel indices'''

        Nx_pix = world.map_img.shape[1]
        Ny_pix = world.map_img.shape[0]

        # FIXME: this has to be linked to the x and y offset in the gui
        # x_map_length_scale = 50
        x_map_length_scale = self.map_length_scales[0]*2
        # y_map_length_scale = 40
        y_map_length_scale = self.map_length_scales[1]*2

        x_pix_per_meter = Nx_pix // x_map_length_scale
        y_pix_per_meter = Ny_pix // y_map_length_scale

        x_origin_pix_offset = Nx_pix // 2
        y_origin_pix_offset = Ny_pix // 2

        x_pix = x_pos * x_pix_per_meter - x_origin_pix_offset
        y_pix = y_pos * y_pix_per_meter - y_origin_pix_offset

        return x_pix, y_pix


    def pix_idx2world_coord(self, img, x_idx, y_idx):
        Nx_pix = img.shape[0]
        Ny_pix = img.shape[1]
        
        # FIXME: this has to be linked to the x and y offset in the gui
        x_map_length_scale = 300
        y_map_length_scale = 300


        # x_origin_meter_offset = x_map_length_scale // 2
        # y_origin_meter_offset = y_map_length_scale // 2

        x_meter_per_pix = x_map_length_scale / Nx_pix
        y_meter_per_pix = y_map_length_scale / Ny_pix

        x_meter = x_idx * x_meter_per_pix
        y_meter = y_idx * y_meter_per_pix
        
        return x_meter, y_meter
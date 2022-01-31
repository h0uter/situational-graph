from knowledge_roadmap.data_providers.local_grid_image_spoofer import LocalGridImageSpoofer
from knowledge_roadmap.data_providers.manual_graph_world import ManualGraphWorld


class LocalGridAdapter:
    def __init__(
        self,
        img_length_in_m: tuple,
        num_cells: int,
        cell_size_m: float,
        mode="spoof",
        debug_container=None,
    ):
        self.mode = mode
        self.num_cells = num_cells
        self.cell_size_m = cell_size_m
        self.lg_length_in_m = num_cells * cell_size_m
        self.spoof_img_length_in_m = img_length_in_m
        self.debug_container = debug_container

    def get_local_grid(self, mode:str) -> list:
        """
        Given the agent's position, return the local grid image around the agent.
        
        :return: The local grid.
        """

        if mode == "spoof":
            agent_pos = self.debug_container["agent"].pos
            world_img = ManualGraphWorld().map_img
        

            lgs = LocalGridImageSpoofer()

            return lgs.sim_spoof_local_grid_from_img_world(agent_pos, world_img, self.num_cells, self.spoof_img_length_in_m)
        else:
            # here comes calls to the spot API
            raise NotImplementedError





from knowledge_roadmap.data_providers.local_grid_image_spoofer import (
    LocalGridImageSpoofer,
)
from knowledge_roadmap.entities.abstract_agent import AbstractAgent
from knowledge_roadmap.entities.agent import Agent
from knowledge_roadmap.data_providers.spot_agent import SpotAgent, get_local_grid


class LocalGridAdapter:
    def __init__(self):
        self.lgs = LocalGridImageSpoofer()

    def get_local_grid(self, agent: AbstractAgent) -> list[list]:
        """
        Given the agent's position, return the local grid image around the agent.
        
        :return: The local grid image.
        """

        # obtain lg from real robot or simulated bot
        if isinstance(agent, SpotAgent):
            # here comes calls to the spot API
            return get_local_grid(agent)

        elif isinstance(agent, Agent):

            return self.lgs.sim_spoof_local_grid_from_img_world(agent.pos)

        else:
            raise Exception("Agent type not recognized")


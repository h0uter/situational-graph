from mpl_vizualisation import MplVizualisation
from src.entities.event import post_event, subscribe
from src.utils.config import Config


class MPLListener():

    def __init__(self, cfg: Config):
        self.gui = MplVizualisation(cfg)
        self.setup_gui_event_handler()
        # self.lg = None

    def handle_new_lg_event(self, lg):
        print(f"new lg event being handled: {lg}")
        self.lg = lg

    def handle_figure_update_event(self, data):
        krm = data["krm"]
        agents = data["agents"]
        self.gui.figure_update(krm, agents, self.lg)

    def setup_gui_event_handler(self):
        subscribe("new lg", self.handle_new_lg_event)
        subscribe("figure update", self.handle_figure_update_event)

from dataclasses import dataclass


@dataclass
class KRMStats:
    num_nodes = []
    num_edges = []
    num_waypoint_nodes = []
    num_frontier_nodes = []
    step_duration = []

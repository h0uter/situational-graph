from dataclasses import dataclass
import matplotlib.pyplot as plt
from src.domain.entities.behaviors import Behaviors
from src.domain.entities.object_types import ObjectTypes

from src.utils.saving_data_objects import load_something, save_something


@dataclass
class TOSGStats:
    def __init__(self) -> None:
        self.num_nodes = [0]
        self.num_edges = [0]
        self.num_waypoint_nodes = [0]
        self.num_waypoint_edges = [0]
        self.num_frontier_nodes = [0]
        self.num_world_object_nodes = [0]
        self.step_duration = [0]

    def update(self, krm, step_duration):

        self.num_nodes.append(krm.graph.number_of_nodes())
        self.num_edges.append(krm.graph.number_of_edges())
        self.step_duration.append(step_duration)

        self.num_waypoint_nodes.append(
            len(
                [
                    n
                    for n in krm.graph.nodes()
                    if krm.graph.nodes[n]["type"] == ObjectTypes.WAYPOINT
                ]
            )
        )
        self.num_waypoint_edges.append(
            len(
                [
                    e
                    # for e in krm.graph.edges()
                    for e in krm.graph.edges
                    if krm.graph.edges[e]["type"] == Behaviors.GOTO
                ]
            )
        )
        self.num_frontier_nodes.append(
            len(
                [
                    n
                    for n in krm.graph.nodes()
                    if krm.graph.nodes[n]["type"] == ObjectTypes.FRONTIER
                ]
            )
        )
        self.num_world_object_nodes.append(
            len(
                [
                    n
                    for n in krm.graph.nodes()
                    if krm.graph.nodes[n]["type"] == ObjectTypes.WORLD_OBJECT
                ]
            )
        )

    def subplot_step_vs_step_duration(self, ax):
        ax.step(
            range(len(self.step_duration)), self.step_duration, label="step duration"
        )

        ax.set_title("Step duration vs step")
        ax.set(xlabel="Step", ylabel="Step duration (seconds)")
        ax.legend()

    def subplot_step_vs_num_nodes(self, ax: plt.Axes):
        ax.set_title("Step vs size of the KRM")
        ax.set(xlabel="Step", ylabel="# of nodes")

        ax.step(range(len(self.num_nodes)), self.num_nodes, label="Total nodes", c="b")
        ax.step(
            range(len(self.num_edges)),
            self.num_edges,
            label="Total edges",
            linestyle="--",
            c="b",
        )

        ax.step(
            range(len(self.num_waypoint_nodes)),
            self.num_waypoint_nodes,
            label="Waypoint nodes",
            c="r",
        )
        ax.step(
            range(len(self.num_waypoint_edges)),
            self.num_waypoint_edges,
            label="Waypoint edges",
            c="r",
            # marker=".",
            linestyle="--",
        )
        ax.step(
            range(len(self.num_frontier_nodes)),
            self.num_frontier_nodes,
            label="Frontier nodes",
            c="g",
        )
        ax.step(
            range(len(self.num_world_object_nodes)),
            self.num_world_object_nodes,
            label="World object nodes",
            c="purple",
        )
        ax.legend()

    def subplot_num_nodes_vs_step_duration(self, ax):
        ax.set_title("Step duration vs size of the KRM")
        ax.set(xlabel="# of nodes", ylabel="Step duration (seconds)")

        ax.step(self.num_nodes, self.step_duration, label="Total nodes")
        ax.step(self.num_edges, self.step_duration, label="Total edges")

        ax.step(
            self.num_waypoint_nodes,
            self.step_duration,
            label="Total waypoint nodes",
            c="r",
        )
        ax.step(
            self.num_frontier_nodes,
            self.step_duration,
            label="Total frontier nodes",
            c="g",
        )
        ax.step(
            self.num_world_object_nodes,
            self.step_duration,
            label="Total world-object nodes",
            c="purple",
        )
        ax.legend()

    def plot_krm_stats(self):

        fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(2, 2)  # type: ignore
        fig.suptitle("Statistics about the KRM")

        self.subplot_step_vs_num_nodes(ax0)
        self.subplot_step_vs_step_duration(ax2)

        self.subplot_num_nodes_vs_step_duration(ax1)

        # mng = plt.get_current_fig_manager()
        # mng.window.showMaximized()

        plt.show()

    def save(self):
        save_something(self, "krm_stats")


if __name__ == "__main__":
    krm_stats = load_something("krm_stats_20220302-1658")
    krm_stats.plot_krm_stats()

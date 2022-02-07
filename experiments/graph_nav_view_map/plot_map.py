import os
import numpy as np

from bosdyn.api.graph_nav import map_pb2
from bosdyn.api import geometry_pb2
from bosdyn.client.frame_helpers import *
from bosdyn.client.math_helpers import *

import matplotlib.pyplot as plt


def load_map(path):
    """
    Load a map from the given file path.
    :param path: Path to the root directory of the map.
    :return: the graph, waypoints, waypoint snapshots and edge snapshots.
    """
    with open(os.path.join(path, "graph"), "rb") as graph_file:
        # Load the graph file and deserialize it. The graph file is a protobuf containing only the waypoints and the
        # edges between them.
        data = graph_file.read()
        current_graph = map_pb2.Graph()
        current_graph.ParseFromString(data)
        # print(current_graph.waypoints)

        # Set up maps from waypoint ID to waypoints, edges, snapshots, etc.
        current_waypoints = {}
        current_waypoint_snapshots = {}
        current_edge_snapshots = {}

        # For each waypoint, load any snapshot associated with it.
        for waypoint in current_graph.waypoints:
            current_waypoints[waypoint.id] = waypoint

            # Load the snapshot. Note that snapshots contain all of the raw data in a waypoint and may be large.
            file_name = os.path.join(path, "waypoint_snapshots", waypoint.snapshot_id)
            if not os.path.exists(file_name):
                continue
            with open(file_name, "rb") as snapshot_file:
                waypoint_snapshot = map_pb2.WaypointSnapshot()
                waypoint_snapshot.ParseFromString(snapshot_file.read())
                current_waypoint_snapshots[waypoint_snapshot.id] = waypoint_snapshot
        # Similarly, edges have snapshot data.
        for edge in current_graph.edges:
            file_name = os.path.join(path, "edge_snapshots", edge.snapshot_id)
            if not os.path.exists(file_name):
                continue
            with open(file_name, "rb") as snapshot_file:
                edge_snapshot = map_pb2.EdgeSnapshot()
                edge_snapshot.ParseFromString(snapshot_file.read())
                current_edge_snapshots[edge_snapshot.id] = edge_snapshot
        print("Loaded graph with {} waypoints and {} edges".format(
            len(current_graph.waypoints), len(current_graph.edges)))
        return (current_graph, current_waypoints, current_waypoint_snapshots,
                current_edge_snapshots)


def main():
    path = os.path.join("experiments", "graph_nav_view_map", "villa.walk")

    (current_graph, current_waypoints, current_waypoint_snapshots,
    current_edge_snapshots) = load_map(path)

    queue = []
    queue.append((current_graph.waypoints[0], np.eye(4)))
    visited = {}

    while len(queue) > 0:
        # Visit a waypoint.
        curr_element = queue[0]
        queue.pop(0)
        curr_waypoint = curr_element[0]
        visited[curr_waypoint.id] = True


        world_tform_current_waypoint = curr_element[1]
        x, y, z = world_tform_current_waypoint[:3, 3]
        # print(f"xyz {x}, {y}, {z}")
        plt.plot(x, y, 'ro')

        for edge in current_graph.edges:
            # If the edge is directed away from us...
            if edge.id.from_waypoint == curr_waypoint.id and edge.id.to_waypoint not in visited:
                current_waypoint_tform_to_waypoint = SE3Pose.from_obj(
                    edge.from_tform_to).to_matrix()
                
                world_tform_to_wp = np.dot(world_tform_current_waypoint, current_waypoint_tform_to_waypoint)

                # world_tform_to_wp = create_edge_object(current_waypoint_tform_to_waypoint,
                #                                        world_tform_current_waypoint, renderer)
                # Add the neighbor to the queue.
                queue.append((current_waypoints[edge.id.to_waypoint], world_tform_to_wp))
                # avg_pos += world_tform_to_wp[:3, 3]
            # If the edge is directed toward us...
            elif edge.id.to_waypoint == curr_waypoint.id and edge.id.from_waypoint not in visited:
                current_waypoint_tform_from_waypoint = (SE3Pose.from_obj(
                    edge.from_tform_to).inverse()).to_matrix()

                world_tform_from_wp = np.dot(world_tform_current_waypoint, current_waypoint_tform_from_waypoint)
                # world_tform_from_wp = create_edge_object(current_waypoint_tform_from_waypoint,
                #                                          world_tform_current_waypoint, renderer)
                # Add the neighbor to the queue.
                queue.append((current_waypoints[edge.id.from_waypoint], world_tform_from_wp))
                # avg_pos += world_tform_from_wp[:3, 3]

    plt.show()


if __name__ == "__main__":
    main()
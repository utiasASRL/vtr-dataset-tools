import os
import numpy as np
from tools import Graph

# Read in data from text files
data_folder = "/home/ben/Documents/dataset_transforms"

teach_run = data_folder + "/run_000000/transforms_temporal.txt"
repeat_runs = []
for i in range(1, 40):
    run_file = "{0}/run_{1}/transforms_spatial.txt".format(data_folder, str(i).zfill(6))
    if os.path.isfile(run_file):
        repeat_runs.append(run_file)

# Create graph
in_the_dark = Graph(teach_run, repeat_runs)            # todo deal with timestamps, GPS

# Example vertices
v1 = (0, 12)
v2 = (4, 25)

if in_the_dark.is_vertex(v1) and in_the_dark.is_vertex(v2):

    # Get path between vertices
    path, _ = in_the_dark.get_path(v1, v2)

    # Get the topological distance between the vertices
    edges_between = in_the_dark.get_topological_dist(v1, v2)

    # Returns T_21
    T = in_the_dark.get_transform(v1, v2)
    dist_between = np.linalg.norm(T.r_ab_inb)
    print("Vertex {0} and vertex {1} are {2} nodes and {3} metres apart.".format(v1, v2, edges_between, round(dist_between, 3)))

    topo_search = in_the_dark.get_topo_neighbours(v1, 1)
    r = 0.1
    metric_search = in_the_dark.get_metric_neighbours(v1, r)
    print("The following vertices are within {0} metres of vertex {1}: {2}".format(r, v1, metric_search))

    # Print T_12
    # print(T.inv())


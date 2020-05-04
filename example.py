import os
from datetime import datetime
import numpy as np
import tools


# Read in data from text files
data_folder = "/media/benc/1c892fc6-27ff-49a3-9358-ac5addb68219/home/ben/Documents/dataset_transforms"
teach_run, repeat_runs, timestamps = tools.get_run_files(data_folder)

# Create graph
in_the_dark = tools.Graph(teach_run, repeat_runs, timestamps)

# Extract subgraph to work with (optional)
in_the_dark = in_the_dark.get_subgraph(0, 500)

# Example vertices
v1 = (0, 67)
v2 = (4, 62)

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

    print("Image at vertex {0} was captured at {1} UTC.".format(v2, datetime.utcfromtimestamp(in_the_dark.get_vertex(v2).timestamp)))

    # Print T_12
    # print(T.inv())


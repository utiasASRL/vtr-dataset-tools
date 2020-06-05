import os
from datetime import datetime
import numpy as np
import tools


def get_run_files(data_dir):

    if not os.path.isdir(data_dir):
        raise Exception("data_dir is not a valid directory")

    teach = data_dir + "/run_000000/transforms_temporal.txt"
    if not os.path.isfile(teach):
        raise Exception("run_000000 must be present in data directory to use these tools.")

    repeats = []
    image_timestamps = {}
    gps_filenames = {}
    gps_timestamps = {}

    for i in range(0, 150):
        im_times = "{0}/run_{1}/timestamps_images.txt".format(data_dir, str(i).zfill(6))
        if os.path.isfile(im_times):
            image_timestamps[i] = im_times

            run_file = "{0}/run_{1}/transforms_spatial.txt".format(data_dir, str(i).zfill(6))
            if os.path.isfile(run_file):
                repeats.append(run_file)

            gps_file = "{0}/run_{1}/gps.txt".format(data_dir, str(i).zfill(6))
            if os.path.isfile(gps_file):
                gps_filenames[i] = gps_file

                gps_time = "{0}/run_{1}/timestamps_gps.txt".format(data_dir, str(i).zfill(6))
                if os.path.isfile(gps_time):
                    gps_timestamps[i] = gps_time

    return teach, repeats, image_timestamps, gps_filenames, gps_timestamps


if __name__ == "__main__":
    # Read in data from text files
    data_folder = "/home/path/to/data"
    teach_run, repeat_runs, image_times, gps_files, gps_times = get_run_files(data_folder)

    # Create graph
    g = tools.Graph(teach_run, repeat_runs, image_times, gps_files, gps_times)

    # Extract sub-graph to work with (optional)
    g = g.get_subgraph(0, 500)

    # Example vertices
    v1 = (0, 67)
    v2 = (1, 62)

    # Check that the vertices are in our graph
    if g.is_vertex(v1) and g.is_vertex(v2):

        # Get path between vertices
        path, _ = g.get_path(v1, v2)

        # Get the topological distance between the vertices
        edges_between = g.get_topological_dist(v1, v2)

        # Returns T_21
        T_v2_v1 = g.get_transform(v1, v2)
        dist_between = np.linalg.norm(T_v2_v1.r_ab_inb)
        print("Vertex {0} and vertex {1} are {2} nodes and {3} metres apart.".format(v1, v2, edges_between, round(dist_between, 3)))

        topo_search = g.get_topo_neighbours(v1, 1)
        r = 0.1
        metric_search = g.get_metric_neighbours(v1, r)
        print("The following vertices are within {0} metres of vertex {1}: {2}".format(r, v1, metric_search))

        print("Image at vertex {0} was captured at {1} UTC.".format(v2, datetime.utcfromtimestamp(g.get_vertex(v2).timestamp)))

        # Calculate T_12
        T_v1_v2 = T_v2_v1.inv()
        # print(T_v1_v2)

""" Example of using tools to read transforms from pose graph. Then use transforms
    to plot path in 2D.
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import tools
from transform import Transform

def plot_path(x, y, run_id, results_folder):
        
    plt.figure()
    
    plt.plot(x, y)
    plt.ylabel('y (meters)', fontsize=16)
    plt.xlabel('x (meters)', fontsize=16)
    plt.title('Integrated path in the plane, run {}'.format(run_id), fontsize=16, weight='bold')
    
    plt.savefig("{}/path_plane_{}.png".format(results_folder, run_id), format='png', bbox_inches='tight')
    plt.close()

def get_run_files(data_folder):

    teach_file = data_folder + "/run_000000/transforms_temporal.txt"
    repeat_files = []

    for i in range(1, 200):
        run_file = "{0}/run_{1}/transforms_spatial.txt".format(data_folder, str(i).zfill(6))
        if os.path.isfile(run_file):
            repeat_files.append(run_file)

    return teach_file, repeat_files


if __name__=="__main__":

    results_folder = "/path/to/results"
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    # Read in data from text files
    data_folder = "/path/to/data"
    teach_file, repeat_files = get_run_files(data_folder)

    # Create graph
    g = tools.Graph(teach_file, repeat_files)

    # Iterate over all runs
    for run_id in range(len(repeat_files) + 1):
        
	x, y = [], []
        T_curr_start = Transform(np.eye(3), np.zeros((3,))) 
 
	pose_id = 0
        vertex_id_curr = (run_id, pose_id)
        vertex_id_next = (run_id, pose_id + 1)
        
        # Iterate sequentially over all vertices in a run
        while g.is_vertex(vertex_id_curr) and g.is_vertex(vertex_id_next):
                        
            # Get transform between adjacent vertices and integrate pose
            T_next_curr = g.get_transform(vertex_id_curr, vertex_id_next)
            T_next_start = T_next_curr * T_curr_start
            r_ba_ina = -T_next_start.C_ba.T.dot(T_next_start.r_ab_inb) 
            x.append(r_ba_ina[0])
            y.append(r_ba_ina[1])
            
            pose_id += 1
            T_curr_start = T_next_start
            vertex_id_curr = vertex_id_next
            vertex_id_next = (run_id, pose_id + 1)

        # Plot the integrated path
        plot_path(x, y, run_id, results_folder) 

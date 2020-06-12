""" Example of using tools to read GPS data from pose graph. Then plot latitude
    and longitude.
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import tools

def plot_path(lat, lon, run_id, results_folder):

    plt.figure()
  
    plt.plot(lat, lon)  
    plt.ylabel('latitude', fontsize=16)
    plt.xlabel('longitude', fontsize=16)
    plt.title('GPS latitude, longitude for run {}'.format(run_id), fontsize=16, weight='bold')
    
    plt.savefig("{}/path_gps_{}.png".format(results_folder, run_id), format='png', bbox_inches='tight')
    plt.close()

def get_run_files(data_folder):
    
    teach_file = data_folder + "/run_000000/transforms_temporal.txt"
    repeat_files = []
    gps_files = {}

    if not os.path.isdir(data_folder):
        raise Exception("data_dir is not a valid directory")

    if not os.path.isfile(teach_file):
        raise Exception("run_000000 must be present in data directory to use these tools.")

    gps_file = "{0}/run_{1}/gps.txt".format(data_folder, '000000')
    if os.path.isfile(gps_file):
        gps_files[0] = gps_file

    for i in range(1, 200):
        run_file = "{0}/run_{1}/transforms_spatial.txt".format(data_folder, str(i).zfill(6))
        if os.path.isfile(run_file):
            repeat_files.append(run_file)

            gps_file = "{0}/run_{1}/gps.txt".format(data_folder, str(i).zfill(6))
            if os.path.isfile(gps_file):
                gps_files[i] = gps_file

    return teach_file, repeat_files, gps_files

if __name__=="__main__":

    results_folder = "/path/to/results"
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    # Read in data from text files
    data_folder = "/path/to/data"
    teach_files, repeat_files, gps_files = get_run_files(data_folder)

    # Create graph
    g = tools.Graph(teach_files, repeat_files, gps_files=gps_files)

    # Iterate over all runs
    for run_id in range(len(repeat_files) + 1):
        if run_id in gps_files.keys():        
            lat, lon = [], []
         
            pose_id = 0
            vertex_id = (run_id, pose_id)
        
            # Iterate sequentially over all vertices in a run
            while g.is_vertex(vertex_id):
                vertex = g.get_vertex(vertex_id)
                        
                # Get transform between adjacent vertices and integrate pose
                if (vertex.latitude is not None) and (vertex.longitude is not None):
                    lat.append(vertex.latitude)
                    lon.append(vertex.longitude)
        
                pose_id += 1
                vertex_id = (run_id, pose_id)

            # Plot the integrated path
            plot_path(lat, lon, run_id, results_folder)

""" Example of using tools to read GPS data from pose graph. Then plot latitude
    and longitude.
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import tools

def plot_path(lat, lon, run, folder):

    plt.figure()
  
    plt.plot(lat, lon)  
    plt.ylabel('lat', fontsize=24, weight='bold')
    plt.xlabel('lon', fontsize=24, weight='bold')
    plt.title('GPS lat, lon for path, run {}'.format(run))
    plt.xticks(fontsize=22)
    plt.yticks(fontsize=22)
    
    plt.savefig("{}/path_gps_{}.png".format(folder, run), format='png', bbox_inches='tight')
    plt.close()

def get_run_files(data_folder):
    
    teach = data_folder + "/run_000000/transforms_temporal.txt"
    repeats = []
    gps = {}

    if not os.path.isdir(data_dir):
        raise Exception("data_dir is not a valid directory")

    if not os.path.isfile(teach):
        raise Exception("run_000000 must be present in data directory to use these tools.")

    for i in range(1, 200):
        run_file = "{0}/run_{1}/transforms_spatial.txt".format(data_folder, str(i).zfill(6))
        if os.path.isfile(run_file):
            repeats.append(run_file)

            gps_file = "{0}/run_{1}/gps.txt".format(data_folder, str(i).zfill(6))
            if os.path.isfile(gps_file):
                gps[i] = gps_file

    return teach, repeats, gps

if __name__=="__main__":

    results_folder = "/home/jenkins/results/in-the-dark"
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    # Read in data from text files
    data_folder = "/home/jenkins/data/UTIAS-In-The-Dark-Public"
    teach, repeats, gps = tools.get_run_files(data_folder)

    # Create graph
    g = tools.Graph(teach, repeats, gps)

    # Iterate over all runs
    for r_ind in range(len(repeat_runs) + 1):
        if r_ind in gps.keys():        
            lat, lon = [], []
         
            v_ind = 0
            v_id = (r_ind, v_ind)
        
            # Iterate over vertices in a run
            v = g.get_vertex(v_id)
            while v is not None:
                        
                # Get transform between adjacent vertices and integrate pose
                if (v.latitude is not None) and (v.longitude is not None):
                    lat.append(v.latitude)
                    lon.append(v.longitude)
        
                v_ind += 1
                v_id = (r_ind, v_ind)
                v = g.get_vertex(v_id)

            # Plot the integrated path
            plot_path(lat, lon, r_ind, results_folder)

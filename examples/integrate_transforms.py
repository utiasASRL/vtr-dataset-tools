import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import tools
from transform import Transform

def plot_path(x, y, run, folder):

    plt.figure()
    
    plt.plot(x, y)
    plt.ylabel('y', fontsize=24, weight='bold')
    plt.xlabel('x', fontsize=24, weight='bold')
    plt.title('Integrated path in the plane, run {}'.format(run))
    plt.xticks(fontsize=22)
    plt.yticks(fontsize=22)
    
    plt.savefig("{}/path_{}.png".format(folder, run), format='png', bbox_inches='tight')
    plt.close()

def get_run_files(data_folder):

    teach = data_folder + "/run_000000/transforms_temporal.txt"
    repeats = []

    for i in range(1, 200):
        run_file = "{0}/run_{1}/transforms_spatial.txt".format(data_folder, str(i).zfill(6))
        if os.path.isfile(run_file):
            repeats.append(run_file)

    return teach, repeats


if __name__=="__main__":

    results_folder = "/home/jenkins/results/in-the-dark"
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    # Read in data from text files
    data_folder = "/home/jenkins/data/UTIAS-In-The-Dark-Public"
    teach, repeats = get_run_files(data_folder)

    # Create graph
    g = tools.Graph(teach, repeats)

    # Iterate over all runs
    for r_ind in range(len(repeat_runs) + 1):
        
	x, y = [], []
        T_curr_start = Transform(np.eye(3), np.zeros((3,))) 
 
	v_ind = 0
        v_curr = (r_ind, v_ind)
        v_next = (r_ind, v_ind + 1)
        
        # Iterate over vertices in a run
        while len(g.get_path(v_curr, v_next)[0]) > 0:
                        
            # Get transform between adjacent vertices and integrate pose
            T_next_curr = g.get_transform(v_curr, v_next)
            T_next_start = T_next_curr * T_curr_start
            r_ba_ina = -T_next_start.C_ba.T.dot(T_next_start.r_ab_inb) 
            x.append(r_ba_ina[0])
            y.append(r_ba_ina[1])
            
            v_ind += 1
            T_curr_start = T_next_start
            v_curr = v_next
            v_next = (r_ind, v_ind + 1)

        # Plot the integrated path
        plot_path(x, y, r_ind, results_folder)


  
            

    
    
    

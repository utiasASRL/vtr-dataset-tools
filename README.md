This repository contains Python classes and functions for working with the UTIAS In the Dark and UTIAS Multiseason datasets.
The data and more information about the datasets can be found [here](http://asrl.utias.utoronto.ca/datasets/2020-vtr-dataset/index.html).

To start, download the teach run folder and as many repeat runs as you would like to work with.
Change the `data_folder` path in `example.py` to your top-level directory containing the run_000xxx folders.
Run the `example.py` script.

**Note**: your data folder must contain run000000 (the Teach run) from one of the two datasets. All other runs have are localized to this run.

###### Key Tools 

`get_topological_dist(self, vertex_id1, vertex_id2)`: Returns the number of edges in the pose graph between the vertices with IDs `vertex_id1` and `vertex_id2`.

`get_transform(self, vertex_id1, vertex_id2)`: Returns the 4x4 transformation matrix T<sub>21<sub>.

`get_topo_neighbours(self, vertex_id, radius)`: Returns a list of vertex IDs of those vertices within `radius` edges of the vertex with ID `vertex_id`.

`get_metric_neighbours(self, vertex_id, radius)`: Returns a list of vertex IDs of those vertices within `radius` metres of the vertex with ID `vertex_id`.

`get_subgraph(self, start, end)`: Returns a Graph consisting of the teach vertices between `start` and `end` and the repeat vertices that are locaized to them. 

This repository contains Python classes and functions for working with the UTIAS In the Dark and UTIAS Multi-Season datasets.

To start, download the teach run folder and as many repeat runs as you would like to work with.
Change the `data_folder` path to your top-level directory containing the run_000xxx folders.
Run the `example.py` script.

###### Key Tools 

`get_topological_dist(self, vertex1, vertex2)`: Returns the number of edges in the pose graph between the vertices with IDs `vertex1` and `vertex2`.

`get_transform(self, vertex1, vertex2)`: Returns the 4x4 transformation matrix T_21.

`get_topo_neighbours(self, vertex, radius)`: Returns a list of vertex IDs of those vertices within `radius` edges of the vertex with ID `vertex`.

`get_metric_neighbours(self, vertex, radius)`: Returns a list of vertex IDs of those vertices within `radius` metres of the vertex with ID `vertex`.

`get_subgraph(self, start, end)`: Returns a Graph consisting of the teach vertices between `start` and `end` and the repeat vertices that are locaized to them. 

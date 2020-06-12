## VT&R Dataset Tools

This repository contains Python classes and functions for working with the UTIAS In the Dark and UTIAS Multiseason datasets.
The data and more information about the datasets can be found [here](http://asrl.utias.utoronto.ca/datasets/2020-vtr-dataset/index.html).

### Notation

Given data from different runs of a path, these tools will build a pose graph and provide methods to extract useful information from the pose graph, such as finding neighbours of a given vertex or the relative transform between two vertices.

As explained in more detail on the dataset [website](http://asrl.utias.utoronto.ca/datasets/2020-vtr-dataset/index.html), the dataset consists of several runs of a path. The data for each run is stored in its own folder. The pose graph consists of vertices for each keyframe on the Teach and Repeat runs. The vertices along the Teach run are connected to the following Teach run vertex, while each Repeat vertex is connected to a Teach vertex. Each connection between vertices has an associated relative transformation.

The figure below illustrates the pose graph with dots representing vertices and arrows representing transformations. The first number in the vertex ID tuple indicates the run number while the second number indicates the pose within the run. In the code we use this ID, `(run_id, pose_id)` to identify vertices.

![Pose graph](http://asrl.utias.utoronto.ca/datasets/2020-vtr-dataset/images/pose_graph.png)

### Example

To start, download the teach run folder and as many repeat runs as you would like to work with.
Change the `data_folder` path in `example.py` to your top-level directory containing the run_000xxx folders.
Run the `example.py` script. This script shows example usage of the key methods provided in these tools. 

**Note**: your data folder must contain run_000000 (the Teach run) from one of the two datasets. All other runs are localized to this run.

The `integrate_transforms.py` script provides an example of iterating through the vertices of several repeat runs in the pose graph, extracting the relative transform between consecutive vertices in the run, integrating the pose and plotting the resulting path in the 2D plane.

Finally, `read_gps.py` shows an example of iterating through the vertices of several runs, extracting the GPS data for the vertices and plotting latitude vs. longitude. 

### Key Tools

Below is an overview of the key methods found in `tools.py` for working with the pose graph data. 

`get_topological_dist(self, vertex_id1, vertex_id2)`: Returns the number of edges in the pose graph between the vertices with IDs `vertex_id1` and `vertex_id2`.

`get_transform(self, vertex_id1, vertex_id2)`: Returns the 4x4 transformation matrix T<sub>21<sub>.

`get_topo_neighbours(self, vertex_id, radius)`: Returns a list of vertex IDs of those vertices within `radius` edges of the vertex with ID `vertex_id`.

`get_metric_neighbours(self, vertex_id, radius)`: Returns a list of vertex IDs of those vertices within `radius` metres of the vertex with ID `vertex_id`.

`get_subgraph(self, start, end)`: Returns a Graph consisting of the Teach vertices between `start` and `end` and the Repeat vertices that are localized to them. 

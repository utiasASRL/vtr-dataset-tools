import copy
import numpy as np

from transform import Transform


class Vertex:
    def __init__(self, run_id, pose_id, next_run_id, next_pose_id, next_transform, teach=False, prev_run_id=-1,
                 prev_pose_id=-1, timestamp=None, gps_time=None, latitude=None, longitude=None, altitude=None):
        self.vertex_id = (int(run_id), int(pose_id))
        self.next_id = (int(next_run_id), int(next_pose_id))
        self.next_transform = next_transform
        self.prev_id = (int(prev_run_id), int(prev_pose_id))
        self.teach = teach
        self.timestamp = timestamp
        self.gps_time = gps_time
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude


class Graph:
    def __init__(self, teach_file, repeat_files=None, im_times=None, gps_files=None, gps_times=None):
        if repeat_files is None:
            repeat_files = []
        if im_times is None:
            im_times = {}
        if gps_files is None:
            gps_files = {}
        if gps_times is None:
            gps_times = {}

        # Read teach run transforms from file
        transforms_temporal = np.loadtxt(teach_file, delimiter=",")
        self.teach_id = int(transforms_temporal[0, 0])
        self.vertices = {}
        self.matches = {}

        # Add teach run vertices
        for row in transforms_temporal:
            transform = Transform(np.array([row[4:7], row[8:11], row[12:15]]), np.array([row[7], row[11], row[15]]))
            self.add_vertex(row[0], row[1], row[2], row[3], transform, True)

        self.add_prev_ids()

        # If repeat run transforms, add those to graph
        for run_file in repeat_files:
            self.add_run(run_file)

        self.add_timestamps(im_times)
        self.add_gps(gps_files, gps_times)

    # Return Vertex in the graph with the given id
    def get_vertex(self, vertex_id):
        return self.vertices.get(vertex_id)

    def is_vertex(self, vertex_id):
        if vertex_id in self.vertices:
            return True
        else:
            return False

    # Add new vertex to graph
    def add_vertex(self, run_id, pose_id, next_run_id, next_pose_id, next_transform, teach=False):

        v = Vertex(run_id, pose_id, next_run_id, next_pose_id, next_transform, teach)

        # Check if vertex already exists
        if self.is_vertex(v.vertex_id):
            print("Vertex {0} already exists in graph".format(v.vertex_id))
            return

        # If teach vertex, create an empty list of repeat vertices that have matched,
        # otherwise check that teach vertex exists and add this vertex to its list of matches
        if teach:
            self.matches[v.vertex_id] = []
            self.vertices[v.vertex_id] = v
        elif v.next_id in self.vertices:
            self.matches[v.next_id].append(v)
            self.vertices[v.vertex_id] = v
        else:
            print("Teach vertex {0} not found in graph so vertex {1} was not added.".format(v.next_id, v.vertex_id))

    # Iterate through teach vertices to add previous indices
    def add_prev_ids(self):
        for v_id in self.vertices:
            v = self.get_vertex(v_id)
            if v.teach and v.next_id in self.vertices:
                self.vertices[v.next_id].prev_id = v_id

    # Add new repeat run to graph
    def add_run(self, run_file):
        transforms_spatial = np.loadtxt(run_file, delimiter=",")
        for row in transforms_spatial:
            transform = Transform(np.array([row[4:7], row[8:11], row[12:15]]), np.array([row[7], row[11], row[15]]))
            self.add_vertex(row[0], row[1], row[2], row[3], transform, False)

    # Add image timestamps to each vertex
    def add_timestamps(self, time_files):
        for run in time_files:
            run_times = np.loadtxt(time_files[run], delimiter=",")
            for row in run_times:
                if (run, int(row[0])) in self.vertices:
                    self.vertices[(run, row[0])].timestamp = float(row[1]) * 10**-9
                else:
                    print("Warning: attempted to add timestamp for vertex ({0}, {1}) not in graph.".format(run, int(row[0])))

    # Add associated GPS measurement and its timestamp to vertices where available
    def add_gps(self, gps_files, gps_times):
        for run in gps_files:
            run_times = np.loadtxt(gps_files[run], delimiter=",")
            for row in run_times:
                if (run, row[0]) in self.vertices:
                    self.vertices[(run, row[1])].latitude = row[2]
                    self.vertices[(run, row[1])].longitude = row[3]
                    self.vertices[(run, row[1])].altitude = row[4]
                else:
                    print("Warning: attempted to add GPS data for vertex ({0}, {1}) not in graph.".format(run, int(row[1])))

        for run in gps_times:
            run_times = np.loadtxt(gps_times[run], delimiter=",")
            for row in run_times:
                if (run, int(row[0])) in self.vertices:
                    self.vertices[(run, row[0])].gps_time = float(row[1]) * 10**-9

    # Returns a subgraph made from the teach vertices between (teach_id, start) and (teach_id, end)
    def get_subgraph(self, start, end):
        if self.is_vertex((self.teach_id, start)) and self.is_vertex((self.teach_id, end)):
            subgraph = copy.copy(self)
            subgraph.matches = {id: self.matches[id] for id in self.matches if start <= id[1] <= end}

            subgraph.vertices = {}
            for m in subgraph.matches:
                subgraph.vertices.update({m: self.get_vertex(m)})
                subgraph.vertices.update({repeat_vertex.vertex_id: repeat_vertex for repeat_vertex in subgraph.matches[m]})

            return subgraph
        else:
            print("Invalid vertex chosen.")
            return self

    # Returns number of edges between vertices in pose graph
    def get_topological_dist(self, vertex1, vertex2):
        path, _ = self.get_path(vertex1, vertex2)
        return len(path) - 1

    # Returns Transform, T_21
    def get_transform(self, vertex1, vertex2):

        transform = Transform(np.eye(3), np.zeros((3,)))

        path, forward = self.get_path(vertex1, vertex2)

        if len(path) == 0:
            print("No path found between vertex {0} and vertex {1}.".format(vertex1, vertex2))
            return transform
        if len(path) == 1:
            return transform

        # Always calculate transform in forward direction then flip if backward
        if not forward:
            path.reverse()

        # Compose transforms
        for vertex in path[:-2]:
            transform = self.get_vertex(vertex).next_transform * transform

        # Check if last vertex in path is a teach vertex
        if self.get_vertex(path[-2]).next_id == path[-1]:
            transform = self.get_vertex(path[-2]).next_transform * transform
        else:
            transform = self.get_vertex(path[-1]).next_transform.inv() * transform

        if forward:
            return transform
        else:
            return transform.inv()

    # Returns list of vertices connecting vertex 1 and vertex2
    # Traverses graph both ways and returns shorter path (topologically)
    def get_path(self, vertex1, vertex2):

        if self.get_vertex(vertex1) is None or self.get_vertex(vertex2) is None:
            print("Invalid vertex.")
            return [], False

        # Set to false if can't find path between vertices
        forward_valid = True
        backward_valid = True

        forward_path = [vertex1]

        # Check if vertex are the same
        if vertex1 == vertex2:
            return forward_path, True

        # Follow chain of vertices from vertex 1 to vertex 2
        start = self.get_vertex(vertex1)
        goal = self.get_vertex(vertex2)
        if not goal.teach:
            goal = self.get_vertex(goal.next_id)
        while start != goal:
            start = self.get_vertex(start.next_id)
            if start is None:
                forward_valid = False
                break
            else:
                forward_path.append(start.vertex_id)
        # If vertex 2 is repeat vertex add edge from teach path to vertex 2 at end
        if forward_path[-1] != vertex2:
            forward_path.append(vertex2)

        # Check other way around loop
        backward_path = [vertex2]
        start = self.get_vertex(vertex2)
        goal = self.get_vertex(vertex1)
        if not goal.teach:
            goal = self.get_vertex(goal.next_id)
        while start != goal:
            start = self.get_vertex(start.next_id)
            if start is None:
                backward_valid = False
                break
            else:
                backward_path.append(start.vertex_id)
        # If vertex 1 is repeat vertex add edge from teach path to vertex 1 at end
        if backward_path[-1] != vertex1:
            backward_path.append(vertex1)

        # Return shorter of the two. Returns boolean to indicate if path is in the forward direction
        if len(forward_path) <= len(backward_path) or not backward_valid and forward_valid:
            return forward_path, True
        elif backward_valid:
            backward_path.reverse()
            return backward_path, False
        else:
            print("No path found. Problem with graph.")
            return [], False

    # Returns set of vertices within 'radius' edges of 'vertex'
    def get_topo_neighbours(self, vertex, radius):

        if self.get_vertex(vertex) is None:
            print("Vertex {0} does not exist.".format(vertex))
            return set()

        if radius < 0:
            print("Warning: negative radius specified.")
            return set()

        neighbours = {vertex}
        if radius == 0:
            return neighbours

        search_radius = 0

        v = self.get_vertex(vertex)
        if not v.teach:
            neighbours.add(v.next_id)
            left_bound = v.next_id
            right_bound = v.next_id
            search_radius += 1
        else:
            left_bound = vertex
            right_bound = vertex

        while search_radius < radius:
            neighbours.update(m.vertex_id for m in self.matches[left_bound])
            neighbours.update(m.vertex_id for m in self.matches[right_bound])
            left_bound = self.get_vertex(left_bound).prev_id
            right_bound = self.get_vertex(right_bound).next_id
            neighbours.add(left_bound)
            neighbours.add(right_bound)
            search_radius += 1

        return neighbours

    # Returns set of vertices within 'radius' metres of 'vertex'
    def get_metric_neighbours(self, vertex, radius):

        if self.get_vertex(vertex) is None:
            print("Vertex {0} does not exist.".format(vertex))
            return set()

        if radius < 0:
            print("Warning: negative radius specified.")
            return set()

        neighbours = {vertex}
        v = self.get_vertex(vertex)
        if not v.teach:
            teach_v = self.get_vertex(v.next_id)
            teach_T = v.next_transform
        else:
            teach_v = v
            teach_T = Transform(np.eye(3), np.zeros((3,)))

        # Search forward direction
        query_v = teach_v
        query_T = teach_T
        while True:
            # Test repeat vertices localized to current teach
            for m in self.matches[query_v.vertex_id]:
                T = m.next_transform.inv() * query_T
                if np.linalg.norm(T.r_ab_inb) < radius:
                    neighbours.add(m.vertex_id)

            # Update current teach
            if np.linalg.norm(query_T.r_ab_inb) < radius:
                neighbours.add(query_v.vertex_id)
                query_T = query_v.next_transform * query_T
                query_v = self.get_vertex(query_v.next_id)
            else:
                break

        # Search backward direction
        query_v = teach_v
        query_T = teach_T
        while True:
            # Update current teach. Order flipped to avoid checking closest teach vertex twice
            if np.linalg.norm(query_T.r_ab_inb) < radius:
                neighbours.add(query_v.vertex_id)
                query_v = self.get_vertex(query_v.prev_id)
                query_T = query_v.next_transform.inv() * query_T
            else:
                break
            # Test repeat vertices localized to current teach
            for m in self.matches[query_v.vertex_id]:
                T = m.next_transform.inv() * query_T
                if np.linalg.norm(T.r_ab_inb) < radius:
                    neighbours.add(m.vertex_id)

        return neighbours


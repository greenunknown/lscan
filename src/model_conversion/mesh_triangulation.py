# Copyright (C) 2018 - This notice is to be included in all relevant source files.
# "Brandon Goldbeck" <bpg@pdx.edu>
# “Anthony Namba” <anamba@pdx.edu>
# “Brandon Le” <lebran@pdx.edu>
# “Ann Peake” <peakean@pdx.edu>
# “Sohan Tamang” <sohan@pdx.edu>
# “An Huynh” <an35@pdx.edu>
# “Theron Anderson” <atheron@pdx.edu>
# This software is licensed under the MIT License. See LICENSE file for the full text.
import matplotlib.pyplot as plt
import time
from stl import Mesh
from src.model_conversion.edge import Edge
from src.model_conversion.unique_edge_list import UniqueEdgeList
from src.model_conversion.triangle import Triangle
from src.util import Util
from src.model_conversion.face import Face


# Group by normals into N groups
# For each group:recursively find neighbors for all edges
# Copy mesh data array of triangles
# Create a new array to track normals
# Create a new array to store groups


class MeshTriangulation:
    """

    """

    def __init__(self, mesh: Mesh):
        self.mesh = mesh

    def run(self):
        # Step 1
        output_from_step_1 = self.group_triangles_triangulation()
        # Step 2
        self._step_2(output_from_step_1)
        # Step 3
        # Step 4

    def get_mesh_triangles(self):
        """
        Converts the mesh to Triangle objects
        :return: List of Triangles
        """
        mesh_triangles = []  # array of Triangles
        for data in self.mesh.data:
            normal = data[0]
            vertex_1 = data[1][0]
            vertex_2 = data[1][1]
            vertex_3 = data[1][2]
            edge_1 = Edge(vertex_1[0], vertex_1[1], vertex_1[2], vertex_2[0], vertex_2[1], vertex_2[2])
            edge_2 = Edge(vertex_2[0], vertex_2[1], vertex_2[2], vertex_3[0], vertex_3[1], vertex_3[2])
            edge_3 = Edge(vertex_3[0], vertex_3[1], vertex_3[2], vertex_1[0], vertex_1[1], vertex_1[2])
            mesh_triangles.append(Triangle(edge_1, edge_2, edge_3, normal=normal))
        return mesh_triangles

    @staticmethod
    def regroup_by_neighbors(groups):
        """
        regroup by neighbors
        :param groups: List of TriangleGroups
        :return:
        """
        all_groups = []
        for group in groups:
            group_triangles = group.triangles
            triangle = group_triangles.pop(-1)
            while group_triangles:
                new_group = MeshTriangulation.regroup(triangle, group_triangles)
                all_groups.append(new_group)
        return all_groups

    @staticmethod
    def regroup(triangle, group_triangles):
        """
        Recursive method
        :param group:
        :return:
        """
        if not group_triangles:
            return []
        edges = triangle.edges
        match_triangles_1 = Triangle.get_edge_match(edges[0], group_triangles)
        if not match_triangles_1:
            return []
        edge_1 = MeshTriangulation.regroup(match_triangles_1, group_triangles).append(match_triangles_1)
        match_triangles_2 = Triangle.get_edge_match(edges[1], group_triangles)
        if not match_triangles_2:
            return []
        edge_2 = MeshTriangulation.regroup(match_triangles_2, group_triangles).append(match_triangles_2)
        match_triangles_3 = Triangle.get_edge_match(edges[2], group_triangles)
        if not match_triangles_3:
            return []
        edge_3 = MeshTriangulation.regroup(match_triangles_3, group_triangles).append(match_triangles_3)
        return edge_1 + edge_2 + edge_3

    @staticmethod
    def group_by_normal(triangles):
        """

        :param triangles:
        :return: a list of list of triangles that have same normal.
        """

    @staticmethod
    def group_by_face(normal_groups):
        """
        This function is assumed that the input is a list of list of triangles that are sorted by normal.
        Any false input may caused bugs or errors.

        The algorithm:
        For each normal group do:
            loop until the normal group is empty:
                pop a triangle in the normal group (this will guaranty that the loop will end)
                set a flag (in a face) is false
                check the whole group finding a neighbor.
                    if having neighbor:
                        creating a face and pass the triangle as parameter
                        set the flag is true
                        loop all normal group to pop all triangle belong to that face.
                        (since we know that there is at least one triangle is neighbor with that triangle)
                        adding the face to face groups
                if the flag is false, adding that triangle to fa group (for this triangle is alone)




        :param normal_groups: is a list of list of triangles that are sorted by normal.
        :return face_group: a list of faces
        """
        fa_group = []
        face_group = []

        for normal_group in normal_groups:
            while not normal_group:
                chosen_triangle = normal_group.pop()
                in_face = False
                for triangle in normal_group:
                    if Triangle.are_neighbors(triangle, chosen_triangle):
                        face = Face(chosen_triangle)
                        in_face = True
                        # looping to pull all triangles in same face
                        for neighbor in normal_group:
                            if face.has_neighbor(neighbor):
                                face.add_triangle(neighbor)
                                normal_group.remove(neighbor)
                if not in_face:
                    fa_group.append(chosen_triangle)

        return face_group

    @staticmethod
    def group_triangles_by_normals(triangles):
        """
        Group triangles by normal
        :param triangles: List of Triangles
        :return: List of Faces
        """
        faces_groups = []
        group_match = False
        for triangle in triangles:
            for group in faces_groups:
                if group.match_normal(triangle.normal):
                    group_match = True
                    group.add_triangle(triangle)
                    break
            if not group_match:
                faces_groups.append(Face([triangle]))
            group_match = False
        return faces_groups

    def group_triangles_triangulation(self):
        """

        :return:
        """
        triangles = self.get_mesh_triangles()
        groups = MeshTriangulation.group_triangles_by_normals(triangles)
        return MeshTriangulation.regroup_by_neighbors(groups) # goes infinite loop

    def step_2(self, faces: []):
        """Step 2. Remove shared edges.
        Input: List of faces.
        Output: List of a list of edges where each list of edges is the edges that were not shared
        in that face.
        :return:
        """
        # Faces is a list of faces, where faces are composed of triangles on the same plane and
        # have some edge connecting them.
        # faces.count() should return the number of planes on an object IE: A cube has 6 faces.
        output = []
        k = -1
        for face in faces:
            shared_edges = UniqueEdgeList()
            # len(face.triangles) should return the # of triangles in the face.
            for m in range(len(face.triangles)):
                for n in range(len(face.triangles)):
                    if m is not n:
                        for i in range(3):
                            for j in range(3):
                                # Compare an edge in triangle "m" vs the 3 other edges in
                                # triangle "n"
                                if Edge.are_overlapping_edges(face.triangles[m].edges[i],
                                                              face.triangles[n].edges[j]):
                                    shared_edges.add(face.triangles[m].edges[i])

            k += 1
            output.append(UniqueEdgeList())
            all_edges_in_face = face.get_edges()
            output[k] = UniqueEdgeList.set_difference(all_edges_in_face, shared_edges)

        return output

    def step_3(self, grouped_edges):
        """
        :param grouped_edges: A list of list of edges, grouped by connectivity between edges.
        :return: List of a list of edges where each list of edges have been simplified. Connecting
        edges that were parallel are joined together.
        """
        output = []
        k = -1
        for outline_edge_group in grouped_edges:
            self._step_3_recursive(outline_edge_group)
            k += 1
            output.append(UniqueEdgeList())
            output[k] = outline_edge_group
        return output

    def _step_3_recursive(self, outline_edge_group: UniqueEdgeList):
        for edge_outer in outline_edge_group.edge_list:
            for edge_inner in outline_edge_group.edge_list:
                if not Edge.same_edge(edge_inner, edge_outer):
                    shared_vertex = Edge.has_shared_vertex(edge_inner, edge_outer)
                    parallel = Edge.are_parallel_or_anti_parallel(edge_inner, edge_outer)
                    if shared_vertex is not None and parallel:
                        # Case 1.
                        start_vertex = [edge_inner.x1, edge_inner.y1, edge_inner.z1]

                        # Case 2.
                        if (edge_inner.x1 == shared_vertex[0] and
                                edge_inner.y1 == shared_vertex[1] and
                                edge_inner.z1 == shared_vertex[2]):
                            start_vertex = [edge_inner.x2, edge_inner.y2, edge_inner.z2]

                        # Case 3.
                        end_vertex = [edge_outer.x1, edge_outer.y1, edge_outer.z1]

                        # Case 4.
                        if (edge_outer.x1 == shared_vertex[0] and
                                edge_outer.y1 == shared_vertex[1] and
                                edge_outer.z1 == shared_vertex[2]):
                            end_vertex = [edge_outer.x2, edge_outer.y2, edge_outer.z2]
                        outline_edge_group.edge_list.remove(edge_outer)
                        outline_edge_group.edge_list.remove(edge_inner)
                        outline_edge_group.add(
                            Edge(start_vertex[0], start_vertex[1], start_vertex[2],  # Edge Start
                                 end_vertex[0], end_vertex[1], end_vertex[2]))  # Edge end
                        self._step_3_recursive(outline_edge_group)

    def step_3_part_2(self, grouped_edges):
        """

        :param grouped_edges: A list of UniqueEdgeLists that compose the edges of a face.
        :return:
        """
        buckets = []

        for group in grouped_edges:
            if len(group.edge_list) > 0:
                current_edge_list = UniqueEdgeList()
                current_edge_list.add(group.edge_list[0])

                unique_edge_lists = self._step_3_part_2_recursive([current_edge_list], group, 0)

                buckets.append(unique_edge_lists)

        return buckets

    def _step_3_part_2_recursive(self, unique_edge_lists: [], all_edges: UniqueEdgeList, i: int):
        """

        :param all_edges:
        :return:
        """
        if len(all_edges.edge_list) == 0:
            return unique_edge_lists

        # Remove all_edges from list that exist in bucket.
        for e in unique_edge_lists[i].edge_list:
            all_edges.remove(e)

        for e in all_edges.edge_list:
            for current_edge in unique_edge_lists[i].edge_list:
                if (not Edge.same_edge(e, current_edge)) and \
                        (Edge.has_shared_vertex(e, current_edge) is not None):
                    if unique_edge_lists[i].add(e):
                        return self._step_3_part_2_recursive(unique_edge_lists, all_edges, i)

        if len(all_edges.edge_list) > 0:
            new_edge_list = UniqueEdgeList()
            new_edge_list.add(all_edges.edge_list[0])
            unique_edge_lists.append(new_edge_list)

            return self._step_3_part_2_recursive(unique_edge_lists, all_edges, i + 1)
        return self._step_3_part_2_recursive(unique_edge_lists, all_edges, i)

    def step_3_part_3(self, grouped_edges):
        """

        :param grouped_edges:
        :return:
        """
        list_of_outer_boundary_indices = []

        for bucket in output_step_3_part_2:
            outer_boundary_index = 0
            max_dist_to_origin = -1.0
            for i in range(len(bucket)):
                for edge in bucket[i].edge_list:
                    origin_to_start = Edge(0, 0, 0, edge.x1, edge.y1, edge.z1)
                    origin_to_end = Edge(0, 0, 0, edge.x2, edge.y2, edge.z2)

                    if origin_to_start.length() > max_dist_to_origin:
                        max_dist_to_origin = origin_to_start.length()
                        outer_boundary_index = i

                    if origin_to_end.length() > max_dist_to_origin:
                        max_dist_to_origin = origin_to_end.length()
                        outer_boundary_index = i

            list_of_outer_boundary_indices.append(outer_boundary_index)

        return list_of_outer_boundary_indices

# test script

#start_time = time.time()
mesh = Mesh.from_file(Util.path_conversion("assets/models/2_holes.stl"), calculate_normals=False)
mesh_trianglulation = MeshTriangulation(mesh)
#group = mesh_trianglulation.group_triangles_triangulation()
#end_time = time.time()

#print(len(group))
print(f"Triangles count: {len(mesh.normals)}")
#print(end_time - start_time)

face1 = Face()
face1.triangles = mesh_trianglulation.get_mesh_triangles()

face2 = Face()
face2.triangles = mesh_trianglulation.get_mesh_triangles()

faces = [face1]

output_step_2 = mesh_trianglulation.step_2(faces)
output_step_3 = mesh_trianglulation.step_3(output_step_2)
output_step_3_part_2 = mesh_trianglulation.step_3_part_2(output_step_3)
# The output for step_3_part3 and step_3_part_2 are both useful.
output_step_3_part_3 = mesh_trianglulation.step_3_part_3(output_step_3_part_2)

# output_step_3_part_2: Contains a list of "buckets", where each bucket contains a list of
# UniqueEdgeLists.

# output_step_3_part_3: An array of indices that reference
# each buckets corresponding outer boundary.

print(f"Triangles count: {len(mesh.normals)}")

t = -1
print(f"Length of output_step_3_part_2: " + str(len(output_step_3_part_2)))

for i in range(len(output_step_3_part_2)):
    bucket = output_step_3_part_2[i]
    print(f"Length of bucket: " + str(len(bucket)))
    print(f"Outer Boundary Index: " + str(output_step_3_part_3[i]))
    colors = ['g', 'b', 'k', 'y', 'r']
    for unique_edge_list in output_step_3_part_2[i]:
        t += 1
        if t > 4:
            t = 0
        print(f"col index: " + str(t))
        for edge in unique_edge_list.edge_list:
            plt.plot([edge.x1, edge.x2], [edge.y1, edge.y2], marker="o", color=colors[t])
    plt.show()

# for z in range(len(output_step_3)):
#    unique_edge_list = output_step_3[z]
#    unique_edge_list.display()
#    plt.figure(figsize=(1, 1), dpi=150)
#    for edge in unique_edge_list.edge_list:
#        plt.plot([edge.x1, edge.x2], [edge.y1, edge.y2], marker="o")
#    plt.show()
#    break

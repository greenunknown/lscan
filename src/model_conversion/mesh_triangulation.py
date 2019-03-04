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

    @staticmethod
    def regroup_by_neighbors(groups):
        """
        regroup by neighbors
        :param groups: List of TriangleGroups
        :return:
        """
        groups
        new_group = []
        for group in groups:
            group_triangles = group.triangles
            triangle = group_triangles.pop(-1)
            while group_triangles:
                MeshTriangulation.regroup(triangle, group_triangles)
        return new_group


    @staticmethod
    def regroup(group):
        """
        Recursive method
        :param group:
        :return:
        """

    def group_triangles_triangulation(self):
        """

        :return:
        """
        triangles = self.get_mesh_triangles()
        groups = MeshTriangulation.group_triangles_by_normals(triangles)
        return MeshTriangulation.regroup_by_neighbors(groups)

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
            print("CLASS: CLASS CLASS:" + str(face.__class__))

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
                            Edge(start_vertex[0], start_vertex[1], start_vertex[2], # Edge Start
                                 end_vertex[0], end_vertex[1], end_vertex[2]))  # Edge end
                        self._step_3_recursive(outline_edge_group)

    def _step_3_part_2(self, grouped_edges):
        """

        :param grouped_edges: A list of list of edges that compose the edges of faces.
        :return:
        """
        grouped_buckets = []

        for group in grouped_edges:
            first_bucket = UniqueEdgeList()
            first_bucket.add(grouped_edges.edgeList[0])
            buckets = [first_bucket]
            buckets = self._step_3_part_2_recursive(buckets, group, 0)
            grouped_buckets.append(buckets)

        return grouped_buckets

    def _step_3_part_2_recursive(self, buckets, edges, i):
        """

        :param edges:
        :return:
        """
        if edges.edge_list.count() == 0:
            return buckets

        bucket = buckets[i]

        for edge in edges.edge_list:
            for edge_in_bucket in bucket.edge_list:
                if not (Edge.same_edge(edge, edge_in_bucket) and
                        Edge.has_shared_vertex(edge, edge_in_bucket)):
                    if bucket.add(edge):
                        return self._step_3_part_2_recursive(buckets, edges, i)

        # Remove edges from list that exist in bucket.
        for edge in bucket.edge_list:
            edges.edge_list.remove(edge)

        if edges.edge_list.count() > 0:
            new_bucket = UniqueEdgeList()
            new_bucket.add(edges.edge_list[0])
            buckets.add(new_bucket)
            return self._step_3_part_2_recursive(buckets, edges, i + 1)
        return self._step_3_part_2_recursive(buckets, edges, i)

    def _step_3_part_3(self, grouped_edges):
        """

        :param grouped_edges:
        :return:
        """
        max_dist_to_origin = -1.0
        outer_boundary_index = 0


# test script


mesh = Mesh.from_file(Util.path_conversion("assets/models/untitled.stl"), calculate_normals=False)
mesh_trianglulation = MeshTriangulation(mesh)

face1 = Face()
face1.triangles = mesh_trianglulation.get_mesh_triangles()

face2 = Face()
face2.triangles = mesh_trianglulation.get_mesh_triangles()

faces = [face1, face2]

output_step_2 = mesh_trianglulation.step_2(faces)
output_step_3 = mesh_trianglulation.step_3(output_step_2)

print(f"Triangles count: {len(mesh.normals)}")

for z in range(len(output_step_3)):
    unique_edge_list = output_step_3[z]
    unique_edge_list.display()
    plt.figure(figsize=(1, 1), dpi=150)
    for edge in unique_edge_list.edge_list:
        plt.plot([edge.x1, edge.x2], [edge.y1, edge.y2], marker="o")
    plt.show()
    break



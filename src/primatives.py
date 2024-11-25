from matrix_util import *
from cmu_graphics import *
from rendering.shading import *


class Mesh:
    def __init__(self, vertices, indices, shading_model=Lambertian()):
        self.vertices = vertices  # List of [x,y,z,w] vertices
        self.indices = indices    # List of triangle indices
        self.shading_model = shading_model

    def rotate(self, angle_rad):
        R = rotation_matrix_y(angle_rad)
        rotated_vertices = []
        for vertex in self.vertices:
            rotated_vertex = matrix_vector_multiply(R, vertex)
            rotated_vertices.append(rotated_vertex)
        self.vertices = rotated_vertices

    def render(self, camera, width, height):
        # Transform vertices to clip space
        transformed_vertices = [matrix_vector_multiply(
            camera.projection_view_matrix, v) for v in self.vertices]

        # Perspective division and conversion to NDC
        ndc = [[v[0]/v[3], v[1]/v[3], v[2]/v[3]] if v[3] !=
               0 else [0, 0, 0] for v in transformed_vertices]

        # Screen space conversion
        screen_coords = [[(x + 1) * (width / 2), (1 - y) *
                          (height / 2), z] for x, y, z in ndc]

        # Render with drawPolygon
        triangles = []
        for i in range(0, len(self.indices), 3):
            idx0 = self.indices[i]
            idx1 = self.indices[i+1]
            idx2 = self.indices[i+2]

            # Get screen coordinates for each vertex
            v0 = screen_coords[idx0]
            v1 = screen_coords[idx1]
            v2 = screen_coords[idx2]

            # Prepare points for drawPolygon
            points = [v0[0], v0[1], v1[0], v1[1], v2[0], v2[1]]

            # Get world coordinates for normal calculation
            world_v0 = self.vertices[idx0][:3]
            world_v1 = self.vertices[idx1][:3]
            world_v2 = self.vertices[idx2][:3]

            # Calculate edges and normal
            edge1 = [world_v1[i] - world_v0[i] for i in range(3)]
            edge2 = [world_v2[i] - world_v0[i] for i in range(3)]
            normal = cross_product(edge1, edge2)

            # Backface culling
            if dot_product(normal, camera.get_view_direction()) >= 0:
                continue  # Skip triangles facing away

            # Shading
            color = self.shading_model.shade(normal, light_dir=[1, -1, 1])

            # Calculate average depth
            avg_depth = sum([v[2] for v in [v0, v1, v2]]) / 3

            triangles.append(
                {'depth': avg_depth, 'points': points, 'color': color})

        triangles.sort(key=lambda tri: tri['depth'], reverse=True)

        for tri in triangles:
            drawPolygon(*tri['points'], fill=tri['color'])


class Cube(Mesh):
    def __init__(self, size=1.0):
        s = size/2
        vertices = [
            # Front face
            [-s, -s,  s, 1],  # 0
            [s, -s,  s, 1],  # 1
            [s,  s,  s, 1],  # 2
            [-s,  s,  s, 1],  # 3
            # Back face
            [-s, -s, -s, 1],  # 4
            [s, -s, -s, 1],  # 5
            [s,  s, -s, 1],  # 6
            [-s,  s, -s, 1],  # 7
        ]

        indices = [
            # Front
            0, 1, 2,  0, 2, 3,
            # Right
            1, 5, 6,  1, 6, 2,
            # Back
            5, 4, 7,  5, 7, 6,
            # Left
            4, 0, 3,  4, 3, 7,
            # Top
            3, 2, 6,  3, 6, 7,
            # Bottom
            4, 5, 1,  4, 1, 0
        ]

        super().__init__(vertices, indices)


class Plane(Mesh):
    def __init__(self, width=1.0):
        s = width/2
        vertices = [
            [-s, -s, 0, 1],
            [s, -s, 0, 1],
            [s, s, 0, 1],
            [-s, s, 0, 1]
        ]

        indices = [
            0, 1, 2,  0, 2, 3
        ]

        super().__init__(vertices, indices)


class Grid(Mesh):
    def __init__(self, size=10.0, divisions=10):
        vertices = []
        indices = []

        half_size = size / 2.0
        step = size / divisions

        # Generate vertices for grid lines along X and Z axes
        for i in range(divisions + 1):
            position = -half_size + i * step
            # Lines parallel to Z axis (along X)
            vertices.append([position, 0, -half_size, 1])  # Start point
            vertices.append([position, 0, half_size, 1])   # End point
            indices.extend([len(vertices) - 2, len(vertices) - 1])

            # Lines parallel to X axis (along Z)
            vertices.append([-half_size, 0, position, 1])  # Start point
            vertices.append([half_size, 0, position, 1])   # End point
            indices.extend([len(vertices) - 2, len(vertices) - 1])

        super().__init__(vertices, indices)

    def render(self, camera, width, height):
        # Transform vertices to clip space
        transformed_vertices = [matrix_vector_multiply(
            camera.projection_view_matrix, v) for v in self.vertices]

        # Perspective division and conversion to NDC
        ndc = [[v[0] / v[3], v[1] / v[3], v[2] / v[3]] if v[3] != 0 else [0, 0, 0]
               for v in transformed_vertices]

        # Screen space conversion
        screen_coords = [[(x + 1) * (width / 2), (1 - y) * (height / 2)]
                         for x, y, z in ndc]

        # Draw grid lines
        for i in range(0, len(self.indices), 2):
            idx_start = self.indices[i]
            idx_end = self.indices[i + 1]

            start_point = screen_coords[idx_start]
            end_point = screen_coords[idx_end]

            # Draw line between the start and end points
            drawLine(start_point[0], start_point[1],
                     end_point[0], end_point[1],
                     fill='lightGray')

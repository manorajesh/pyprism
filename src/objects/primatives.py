from matrix_util import *
from cmu_graphics import *
from rendering.shading import *
from objects.mesh import Mesh


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

        # Used ChatGPT to generate these indices
        # and understand the order of vertices
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

        super().__init__(vertices, indices, is_editable=True)


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

        super().__init__(vertices, indices, is_editable=True)


class Grid(Mesh):
    def __init__(self, size=10.0, divisions=10):
        vertices = []
        indices = []

        half_size = size / 2.0
        step = size / divisions

        # Generate vertices for grid lines along X and Z axes
        # Used ChatGPT to understand the logic and get started
        for i in range(divisions + 1):
            position = -half_size + i * step
            vertices.append([position, 0, -half_size, 1])  # Start point
            vertices.append([position, 0, half_size, 1])   # End point
            indices.extend([len(vertices) - 2, len(vertices) - 1])

            vertices.append([-half_size, 0, position, 1])  # Start point
            vertices.append([half_size, 0, position, 1])   # End point
            indices.extend([len(vertices) - 2, len(vertices) - 1])

        super().__init__(vertices, indices, is_selectable=False)

    def render(self, app):
        # The rendering logic is the same as any object in the scene
        # Just the final drawLine call is different

        # Transform vertices
        transformed_vertices = [matrix_vector_multiply(
            app.camera.projection_view_matrix, v) for v in self.vertices]

        # Perspective division and conversion to NDC
        ndc = []
        for point in transformed_vertices:
            if app.is_ortho:
                ndc.append(point[:3])
            else:
                ndc.append([point[0]/point[3], point[1] /
                           point[3], point[2]/point[3]])

        # Screen space conversion
        screen_coords = [[(x + 1) * (app.width / 2), (1 - y) * (app.height / 2)]
                         for x, y, z in ndc]

        # Draw grid lines
        for i in range(0, len(self.indices), 2):
            idx_start = self.indices[i]
            idx_end = self.indices[i + 1]

            start_point = screen_coords[idx_start]
            end_point = screen_coords[idx_end]

            # color the two center x and z axis lines red and blue
            if idx_start == 20:
                drawLine(start_point[0], start_point[1],
                         end_point[0], end_point[1], fill='blue')
            elif idx_start == 22:
                drawLine(start_point[0], start_point[1],
                         end_point[0], end_point[1], fill='red')
            else:
                drawLine(start_point[0], start_point[1],
                         end_point[0], end_point[1],
                         fill=rgb(50, 50, 50))


class ImportedMesh(Mesh):
    def __init__(self, file_path, shading_model=Lambertian()):
        vertices, indices = self.load_obj(file_path)
        self.name = file_path.split('/')[-1].split('.')[0]
        super().__init__(vertices, indices, shading_model, is_editable=True)

    @staticmethod
    def load_obj(file_path):
        # https://cs418.cs.illinois.edu/website/text/obj.html
        vertices = []
        indices = []

        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('v '):  # vertices
                    parts = line.strip().split()
                    x, y, z = map(float, parts[1:4])
                    # Add homogeneous coordinate w=1
                    vertices.append([x, y, z, 1])
                elif line.startswith('f '):  # face info/indices
                    parts = line.strip().split()
                    # obj file indices start from 1 so we subtract 1
                    face_indices = [int(part.split('/')[0]) -
                                    1 for part in parts[1:]]
                    if len(face_indices) == 3:
                        indices.extend(face_indices)
                    elif len(face_indices) > 3:
                        raise ValueError(
                            'Only triangles are supported for now')
        return vertices, indices

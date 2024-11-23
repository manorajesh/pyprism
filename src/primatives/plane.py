from matrix_util import *
from cmu_graphics import *


class Plane:
    def __init__(self):
        self.vertices = [
            [-1, -1, 0, 1],  # Bottom-left
            [1, -1, 0, 1],   # Bottom-right
            [1, 1, 0, 1],    # Top-right
            [-1, 1, 0, 1]    # Top-left
        ]

    def rotate(self, angle_rad):
        R = rotation_matrix_y(angle_rad)

        # Apply rotation to each vertex
        rotated_vertices = []
        for vertex in self.vertices:
            rotated_vertex = matrix_vector_multiply(R, vertex)
            rotated_vertices.append(rotated_vertex)
        self.vertices = rotated_vertices

    def render(self, camera, width, height):
        # Transform vertices from local space to clip space
        transformed_vertices = []
        for vertex in self.vertices:
            transformed_vertex = matrix_vector_multiply(
                camera.projection_view_matrix, vertex)
            transformed_vertices.append(transformed_vertex)

        # Perspective Division to Normalized Device Coordinates (NDC)
        ndc = []
        for p in transformed_vertices:
            if p[3] == 0:
                ndc.append([0, 0, 0])  # Avoid division by zero
            else:
                ndc_x = p[0] / p[3]
                ndc_y = p[1] / p[3]
                ndc_z = p[2] / p[3]
                ndc.append([ndc_x, ndc_y, ndc_z])

        # Map NDC to Screen Coordinates
        screen_coords = []
        for coord in ndc:
            x_screen = (coord[0] + 1) * (width / 2)
            y_screen = (1 - coord[1]) * (height / 2)  # Invert Y-axis
            screen_coords.append([x_screen, y_screen])

        flattened_coords = []
        for point in screen_coords:
            flattened_coords.extend([float(point[0]), float(point[1])])

        drawPolygon(*flattened_coords, fill='gray')

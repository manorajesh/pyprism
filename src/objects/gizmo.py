from cmu_graphics import *
from matrix_util import *


class Gizmo:
    def __init__(self, size=1.0):
        self.is_editable = False
        self.is_selectable = False
        self.size = size
        self.axes = [
            # X-axis
            ([0, 0, 0, 1], [size, 0, 0, 1], 'red'),
            # Y-axis
            ([0, 0, 0, 1], [0, size, 0, 1], 'green'),
            # Z-axis
            ([0, 0, 0, 1], [0, 0, size, 1], 'blue'),
        ]

    def render(self, app):
        gizmo_size_in_pixels = 40
        offset_x = app.width - 50 - gizmo_size_in_pixels
        offset_y = 50

        # Draw background circle
        drawCircle(offset_x + gizmo_size_in_pixels / 2,
                   offset_y + gizmo_size_in_pixels / 2, gizmo_size_in_pixels, fill='white', opacity=20)

        # ignore the view matrix translation
        # so that gizmo is always at the center of the screen
        view_matrix = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]

        # only use rotation
        rotation = [
            app.camera.view_matrix[0][:3] + [0],
            app.camera.view_matrix[1][:3] + [0],
            app.camera.view_matrix[2][:3] + [0],
            [0, 0, 0, 1]
        ]

        view_matrix = matrix_multiply(rotation, view_matrix)
        projection_view = matrix_multiply(
            app.camera.gizmo_perspective_matrix, view_matrix)

        # Render axes
        for start, end, color in self.axes:
            # Apply modified view transformation
            transformed_start = matrix_vector_multiply(projection_view, start)
            transformed_end = matrix_vector_multiply(projection_view, end)

            # Just use transformed start and end points as NDC
            # for orthographic projection
            ndc_start = transformed_start
            ndc_end = transformed_end

            screen_start = [
                offset_x + (ndc_start[0] + 1) * (gizmo_size_in_pixels / 2),
                offset_y + (1 - ndc_start[1]) * (gizmo_size_in_pixels / 2)
            ]
            screen_end = [
                offset_x + (ndc_end[0] + 1) * (gizmo_size_in_pixels / 2),
                offset_y + (1 - ndc_end[1]) * (gizmo_size_in_pixels / 2)
            ]

            # Draw line
            drawLine(screen_start[0], screen_start[1], screen_end[0], screen_end[1],
                     fill=color, lineWidth=2)

            # Draw Axis Labels
            if color == 'red':
                drawLabel('X', screen_end[0],
                          screen_end[1], fill='red', bold=True)
            elif color == 'green':
                drawLabel('Y', screen_end[0],
                          screen_end[1], fill='green', bold=True)
            elif color == 'blue':
                drawLabel('Z', screen_end[0],
                          screen_end[1], fill='blue', bold=True)

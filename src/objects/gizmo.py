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

    def render(self, app, camera, width, height, edit_mode=False):
        gizmo_size_in_pixels = 40
        offset_x = width - 50 - gizmo_size_in_pixels
        offset_y = 50

        # Draw background circle
        drawCircle(offset_x + gizmo_size_in_pixels / 2,
                   offset_y + gizmo_size_in_pixels / 2, gizmo_size_in_pixels, fill='white', opacity=20)

        # Render axes
        for start, end, color in self.axes:
            # Apply camera transformation for perspective projection
            transformed_start = matrix_vector_multiply(
                camera.gizmo_projection_view_matrix, start)
            transformed_end = matrix_vector_multiply(
                camera.gizmo_projection_view_matrix, end)

            # Just use transformed start and end points as NDC
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

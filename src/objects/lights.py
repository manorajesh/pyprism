from matrix_util import *
from cmu_graphics import *
from objects.primatives import Mesh


class Light(Mesh):
    def __init__(self, intensity, x=1, y=-1, z=1):
        self.intensity = intensity
        self.x = x
        self.y = y
        self.z = z
        self.is_selectable = True
        self.is_editable = False
        self.selection_mode = 'vertex'
        self.screen_coords = None

        super().__init__([], [], None, False, True)

    def get_view_direction(self):
        # Same as getting camera view direction
        x = self.x
        y = self.y
        z = self.z
        length = math.sqrt(x * x + y * y + z * z)
        if length != 0:
            x /= length
            y /= length
            z /= length

        return [x, y, z]


class PointLight(Light):
    def render(self, app):
        # Transform point to screen space
        world_point = [self.x, self.y, self.z, 1]
        transformed_point = matrix_vector_multiply(
            app.camera.projection_view_matrix, world_point)

        if app.is_ortho:
            ndc = transformed_point[:3]
        else:
            ndc = [transformed_point[0]/transformed_point[3],
                   transformed_point[1]/transformed_point[3],
                   transformed_point[2]/transformed_point[3]]

        x = (ndc[0] + 1) * (app.width / 2)
        y = (1 - ndc[1]) * (app.height / 2)
        z = ndc[2]

        self.screen_coords = [x, y, z]

        # Create octagon points
        size = 10
        points = []
        for i in range(8):
            angle = i * math.pi / 4
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.extend([px, py])

        border = 'orange' if app.selected_object == self else None

        # Return a single polygon
        triangles = [{
            'depth': z,
            'points': points,
            'color': 'yellow',
            'opacity': 90,
            'border': border,
            'borderWidth': 2 if border else 0
        }]

        return triangles

    def check_selection(self, mouseX, mouseY):
        # Assume circular selection area
        if not self.screen_coords:
            return False

        if self.screen_coords[0] - 10 <= mouseX <= self.screen_coords[0] + 10 \
                and self.screen_coords[1] - 10 <= mouseY <= self.screen_coords[1] + 10:
            return True

    # def transform(self, app, dx, dy):
    #     # Same as mesh transform
    #     movement_factor = 0.01  # Adjust as necessary
    #     if app.transform_mode == 'move':
    #         move_vector = [dx * movement_factor, -dy *
    #                        movement_factor, -dx * movement_factor]
    #         if app.axis_constraint == 'x':
    #             move_vector[1] = move_vector[2] = 0
    #         elif app.axis_constraint == 'y':
    #             move_vector[0] = move_vector[2] = 0
    #         elif app.axis_constraint == 'z':
    #             move_vector[0] = move_vector[1] = 0

    #         self.apply_translation(move_vector)

    def apply_translation(self, move_vector):
        self.x += move_vector[0]
        self.y += move_vector[1]
        self.z += move_vector[2]

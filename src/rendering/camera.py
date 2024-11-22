from matrix_util import *


class Camera:
    def __init__(self, x, y, z, aspect_ratio, fov=90, near=0.1, far=1000):
        self.x = x
        self.y = y
        self.z = z
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

        self.previous_mouse = None
        self.azimuth = 0.0
        self.elevation = 0.0

        fov_rad = math.radians(fov)
        f = 1 / math.tan(fov_rad / 2)

        self.perspective_matrix = [
            [f / aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, -(far + near) / (far - near), -
             (2 * far * near) / (far - near)],
            [0, 0, -1, 0]
        ]

        self.translation_matrix = [
            [1, 0, 0, -x],
            [0, 1, 0, -y],
            [0, 0, 1, -z],
            [0, 0, 0, 1]
        ]

        self.view_matrix = self.translation_matrix

        self.projection_view_matrix = matrix_multiply(
            self.perspective_matrix, self.view_matrix)

    def move(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z

        self.translation_matrix = [
            [1, 0, 0, -self.x],
            [0, 1, 0, -self.y],
            [0, 0, 1, -self.z],
            [0, 0, 0, 1]
        ]

        self.view_matrix = self.translation_matrix

        self.projection_view_matrix = matrix_multiply(
            self.perspective_matrix, self.view_matrix)

    def resize(self, width, height):
        fov_rad = math.radians(self.fov)
        f = 1 / math.tan(fov_rad / 2)

        self.aspect_ratio = width / height
        self.perspective_matrix = [
            [f / self.aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, -(self.far + self.near) / (self.far - self.near), -
             (2 * self.far * self.near) / (self.far - self.near)],
            [0, 0, -1, 0]
        ]

        self.projection_view_matrix = matrix_multiply(
            self.perspective_matrix, self.view_matrix)

    def orbit(self, mouseX, mouseY, target=[0, 0, 0], radius=5.0, sensitivity=0.05):
        if self.previous_mouse is None:
            self.previous_mouse = [mouseX, mouseY]
            return

        dAzimuth = sensitivity * (mouseX - self.previous_mouse[0])
        dElevation = sensitivity * (mouseY - self.previous_mouse[1])

        self.previous_mouse = [mouseX, mouseY]

        # Update azimuth and elevation
        self.azimuth += dAzimuth
        self.elevation += dElevation

        self.elevation = max(-math.pi / 2, min(math.pi / 2, self.elevation))

        # Get the new camera position
        x = target[0] + radius * \
            math.cos(self.elevation) * math.sin(self.azimuth)
        y = target[1] + radius * math.sin(self.elevation)
        z = target[2] + radius * \
            math.cos(self.elevation) * math.cos(self.azimuth)

        # Update camera position
        self.x, self.y, self.z = x, y, z

        # Update the view matrix to look at the target
        self.lookAt([self.x, self.y, self.z], target, [0, 1, 0])

    def lookAt(self, position, target, up):
        z = normalize(subtract(position, target))
        x = normalize(cross_product(up, z))
        y = cross_product(z, x)

        self.view_matrix = [
            [x[0], x[1], x[2], -dot_product(x, position)],
            [y[0], y[1], y[2], -dot_product(y, position)],
            [z[0], z[1], z[2], -dot_product(z, position)],
            [0, 0, 0, 1]
        ]

        self.projection_view_matrix = matrix_multiply(
            self.perspective_matrix, self.view_matrix)

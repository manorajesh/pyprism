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

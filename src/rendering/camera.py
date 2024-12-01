from matrix_util import *


class Camera:
    def __init__(self, x, y, z, aspect_ratio, fov=90, near=0.1, far=1000):
        # gluPerspective https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml

        # Perspective Projection Matrix
        # https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/building-basic-perspective-projection-matrix.html

        self.x = x
        self.y = y
        self.z = z
        self.fov = fov
        self.prev_fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

        self.azimuth = 0.0
        self.elevation = 0.0
        self.radius = 5.0

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

        # so that gizmo rendering is always orthographic and at a stable fov
        self.gizmo_projection_view_matrix = self.projection_view_matrix
        self.gizmo_perspective_matrix = self.perspective_matrix

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

    def orbit(self, dx, dy, target=[0, 0, 0], sensitivity=0.01):
        # Orbit Camera
        # https://community.khronos.org/t/implementing-an-orbit-camera/75208/4

        dAzimuth = sensitivity * dx
        dElevation = sensitivity * dy

        # Update azimuth and elevation
        self.azimuth += dAzimuth
        self.elevation += dElevation

        self.elevation = max(-math.pi / 2, min(math.pi / 2, self.elevation))

        # Get the new camera position
        x = target[0] + self.radius * \
            math.cos(self.elevation) * math.sin(self.azimuth)
        y = target[1] + self.radius * math.sin(self.elevation)
        z = target[2] + self.radius * \
            math.cos(self.elevation) * math.cos(self.azimuth)

        # Update camera position
        self.x, self.y, self.z = x, y, z

        # Update the view matrix to look at the target
        self.lookAt([self.x, self.y, self.z], target, [0, 1, 0])

    def lookAt(self, position, target, up):
        # gluLookAt https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluLookAt.xml
        z = normalize(subtract(position, target))
        x = normalize(cross(up, z))
        y = cross(z, x)

        self.view_matrix = [
            [x[0], x[1], x[2], -dot(x, position)],
            [y[0], y[1], y[2], -dot(y, position)],
            [z[0], z[1], z[2], -dot(z, position)],
            [0, 0, 0, 1]
        ]

        self.projection_view_matrix = matrix_multiply(
            self.perspective_matrix, self.view_matrix)

        self.gizmo_projection_view_matrix = matrix_multiply(
            self.gizmo_perspective_matrix, self.view_matrix)

    def position(self):
        return [self.x, self.y, self.z]

    def get_view_direction(self):
        # Calculate the view direction vector based on azimuth and elevation
        # https://community.khronos.org/t/implementing-an-orbit-camera/75208/4

        x = math.cos(self.elevation) * math.sin(self.azimuth)
        y = math.sin(self.elevation)
        z = math.cos(self.elevation) * math.cos(self.azimuth)

        # Normalize the vector
        length = math.sqrt(x * x + y * y + z * z)
        if length != 0:
            x /= length
            y /= length
            z /= length

        return [x, y, z]

    def zoom(self, app, amount):
        print(self.radius, self.fov)
        # Sensitivity should decrease as the radius decreases
        if app.is_ortho:
            sensitivity = 0.001 * self.fov
            self.fov += amount * sensitivity
            self.fov = min(180, self.fov)
            self.fov = max(2, self.fov)
            # force perspective matrix recalculation
            self.resize(app.width, app.height)
        else:
            sensitivity = 0.001 * self.radius
            self.radius += amount * sensitivity
            self.radius = max(0.1, self.radius)
            # force perspective update
            self.orbit(0, 0)

    def snap_to_axis(self, axis, target=[0, 0, 0]):
        match axis:
            case 'x':
                self.elevation = 0
                self.azimuth = 45.5
            case 'y':
                self.elevation = math.pi/2
                self.azimuth = 0
            case 'z':
                self.elevation = 0
                self.azimuth = 0
            case _:
                raise ValueError('Invalid axis supplied: x, y, z allowed')

        x = target[0] + self.radius * \
            math.cos(self.elevation) * math.sin(self.azimuth)
        y = target[1] + self.radius * math.sin(self.elevation)
        z = target[2] + self.radius * \
            math.cos(self.elevation) * math.cos(self.azimuth)

        # Update camera position
        self.x, self.y, self.z = x, y, z

        # Update the view matrix to look at the target
        self.lookAt([self.x, self.y, self.z], target, [0, 1, 0])

    def is_ortho(self, app):
        if app.is_ortho:
            self.prev_fov = self.fov
            self.fov = self.radius * 25
        else:
            self.fov = self.prev_fov

        self.resize(app.width, app.height)

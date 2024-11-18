from cmu_graphics import *
import math


def matrix_multiply(a, b):
    result = []
    for i in range(4):
        row = []
        for j in range(4):
            sum = 0
            for k in range(4):
                sum += a[i][k] * b[k][j]
            row.append(sum)
        result.append(row)
    return result


def matrix_vector_multiply(matrix, vector):
    result = []
    for i in range(4):
        sum = 0
        for j in range(4):
            sum += matrix[i][j] * vector[j]
        result.append(sum)
    return result


def cross_product(a, b):
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ]


def dot_product(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def rotation_matrix_y(angle_rad):
    return [
        [math.cos(angle_rad), 0, math.sin(angle_rad), 0],
        [0, 1, 0, 0],
        [-math.sin(angle_rad), 0, math.cos(angle_rad), 0],
        [0, 0, 0, 1]
    ]


class World:
    def __init__(self, camera):
        self.camera = camera
        self.objects = []

    def addObject(self, obj):
        self.objects.append(obj)

    def removeObject(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    def render(self, width, height):
        for obj in self.objects:
            obj.render(self.camera, width, height)


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


def onAppStart(app):
    app.camera = Camera(
        x=0, y=0, z=-5,
        aspect_ratio=app.width / app.height,
        fov=60,
        near=0.1,
        far=1000
    )

    app.world = World(app.camera)

    app.world.addObject(Plane())


def onKeyPress(app, key):
    if key == 'up':
        app.camera.move(0, 0, 0.1)
    elif key == 'down':
        app.camera.move(0, 0, -0.1)
    elif key == 'left':
        app.camera.move(0.1, 0, 0)
    elif key == 'right':
        app.camera.move(-0.1, 0, 0)


def onStep(app):
    for obj in app.world.objects:
        obj.rotate(math.radians(1))


def redrawAll(app):
    app.world.render(app.width, app.height)


def main():
    runApp(width=1000, height=1000)


if __name__ == "__main__":
    main()

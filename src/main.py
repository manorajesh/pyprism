from cmu_graphics import *
import math
import numpy as np


class World:
    def __init__(self, camera):
        self.camera = camera
        self.objects = []

    def addObject(self, obj):
        self.objects.append(obj)

    def removeObject(self, obj):
        self.objects.remove(obj)

    def render(self, width, height):
        for obj in self.objects:
            obj.render(self.camera, width, height)


class Camera():
    def __init__(self, x, y, z, aspect_ratio, fov=90, near=0.1, far=1000):
        self.x = x
        self.y = y
        self.z = z
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

        fov_rad = math.radians(fov)

        # Calculate focal length
        f = 1 / math.tan(fov_rad / 2)

        # Perspective Projection Matrix
        self.perspective_matrix = np.array([
            [f / aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, -(far + near) / (far - near), -
             (2 * far * near) / (far - near)],
            [0, 0, -1, 0]
        ])

        self.translation_matrix = np.array([
            [1, 0, 0, -x],
            [0, 1, 0, -y],
            [0, 0, 1, -z],
            [0, 0, 0, 1]
        ])

        # Assuming no rotation
        self.view_matrix = self.translation_matrix

        self.projection_view_matrix = np.dot(
            self.perspective_matrix, self.view_matrix)

    def move(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z

        self.translation_matrix = np.array([
            [1, 0, 0, -self.x],
            [0, 1, 0, -self.y],
            [0, 0, 1, -self.z],
            [0, 0, 0, 1]
        ])

        self.view_matrix = self.translation_matrix

        self.projection_view_matrix = np.dot(
            self.perspective_matrix, self.view_matrix)


class Plane():
    def __init__(self):
        # Define plane vertices in homogeneous coordinates (x, y, z, w)
        self.vertices = np.array([
            [-1, -1, 0, 1],  # Bottom-left
            [1, -1, 0, 1],   # Bottom-right
            [1, 1, 0, 1],    # Top-right
            [-1, 1, 0, 1]    # Top-left
        ])

    def rotate(self, angle):
        R_y = np.array([
            [math.cos(angle), 0, math.sin(angle), 0],
            [0, 1, 0, 0],
            [-math.sin(angle), 0, math.cos(angle), 0],
            [0, 0, 0, 1]
        ])

        self.vertices = self.vertices @ R_y.T

    def render(self, camera, width, height):
        # Transform vertices from local space to world space
        transformed_vertices = self.vertices @ camera.projection_view_matrix.T

        # Normalize the vertices to Normalized Device Coordinates
        # Divide by the w component of each vertex
        # This will put the vertices in the range [-1, 1]
        ndc = [[p[0]/p[3], p[1]/p[3], p[2]/p[3]] for p in transformed_vertices]

        # Map NDC to Screen Coordinates
        # NDC x and y are in range [-1, 1], map them to [0, width] and [0, height]
        screen_coords = np.zeros((4, 2))
        for i in range(4):
            screen_coords[i, 0] = (ndc[i][0] + 1) * (width / 2)
            screen_coords[i, 1] = (1 - ndc[i][1]) * (height / 2)

        flattened_coords = screen_coords.flatten()
        float_coords = [float(coord) for coord in flattened_coords]

        drawPolygon(*float_coords, fill='gray')


def onAppStart(app):
    # Initialize the camera
    app.camera = Camera(
        x=0, y=0, z=-5,  # Camera positioned at (0, 0, -5)
        aspect_ratio=app.width / app.height,
        fov=60,           # Field of View
        near=0.1,
        far=1000
    )

    # Initialize world
    app.world = World(app.camera)

    # Create a plane object
    app.world.addObject(Plane())


def onKeyPress(app, key):
    if key == 'up':
        app.camera.move(0, 0, 0.1)
    elif key == 'down':
        app.camera.move(0, 0, -0.1)
    elif key == 'left':
        app.camera.move(-0.1, 0, 0)
    elif key == 'right':
        app.camera.move(0.1, 0, 0)


def onStep(app):
    # Rotate the plane object
    for obj in app.world.objects:
        obj.rotate(math.radians(1))


def redrawAll(app):
    app.world.render(app.width, app.height)


def main():
    runApp(width=800, height=600)


if __name__ == "__main__":
    main()

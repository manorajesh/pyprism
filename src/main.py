from cmu_graphics import *
import time

from primatives import *
from rendering.camera import *
from rendering.world import *


class FrameTime:
    def __init__(self):
        self.now = time.time()

    def get(self):
        frame_time = (time.time() - self.now) * 1000
        self.now = time.time()
        return frame_time


def onAppStart(app):
    app.frame_time = FrameTime()
    app.is_orbiting = False
    app.is_zooming = False
    app.prev_mouse = (0, 0)

    app.camera = Camera(
        x=0, y=0, z=-5,
        aspect_ratio=app.width / app.height,
        fov=60,
        near=0.1,
        far=1000
    )

    app.world = World(app.camera, app.width, app.height)

    app.world.addObject(Grid(size=5))
    # app.world.addObject(Sphere())


def onMouseMove(app, mouseX, mouseY):
    dx = mouseX - app.prev_mouse[0]
    dy = mouseY - app.prev_mouse[1]
    app.prev_mouse = (mouseX, mouseY)

    if app.is_zooming:
        app.camera.zoom(dy)
    elif app.is_orbiting:
        app.camera.orbit(-dx, dy)


def onKeyPress(app, key, modifiers):
    print(modifiers)
    if key == 'space':
        app.is_orbiting = True

    if key == 'z':
        app.is_zooming = True


def onKeyRelease(app, key):
    if key == 'space':
        app.is_orbiting = False

    if key == 'z':
        app.is_zooming = False


def onStep(app):
    pass


def redrawAll(app):
    drawLabel(f"Frame time: {app.frame_time.get():.2f}ms", 100, 10)
    app.world.render(app.width, app.height)


def main():
    runApp(width=1000, height=1000)


if __name__ == "__main__":
    main()

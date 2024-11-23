from cmu_graphics import *

from primatives.plane import *
from rendering.camera import *
from rendering.world import *


def onAppStart(app):
    app.camera = Camera(
        x=0, y=0, z=-5,
        aspect_ratio=app.width / app.height,
        fov=60,
        near=0.1,
        far=1000
    )

    app.world = World(app.camera, app.width, app.height)

    app.world.addObject(Plane())


def onKeyPress(app, key):
    if key == 'up':
        app.camera.move(0, 0, 0.1)
    elif key == 'down':
        app.camera.move(0, 0, -0.1)
    elif key == 'left':
        # Lateral movement is inverted due to camera orientation
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

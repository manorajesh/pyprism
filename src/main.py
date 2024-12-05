from cmu_graphics import *
import time

from objects.primatives import *
from objects.lights import *
from objects.gizmo import *
from rendering.camera import *
from rendering.world import *


class FrameStats:
    def __init__(self):
        self.last_time = time.time()

    def frame_time(self):
        now = time.time()
        frame_time = (now - self.last_time) * 1000
        self.last_time = now
        return frame_time

    def fps(self):
        return 1 / (self.frame_time())


def onAppStart(app):
    app.setMaxShapeCount(2000000)
    app.background = rgb(64, 64, 64)
    app.frame_stats = FrameStats()
    app.is_orbiting = False
    app.is_zooming = False
    app.edit_mode = False
    app.is_ortho = False
    app.prev_mouse = (0, 0)

    app.camera = Camera(
        x=0, y=0, z=-5,
        aspect_ratio=app.width / app.height,
        fov=60,
        near=0.1,
        far=1000
    )

    app.camera.orbit(10, 10)

    app.world = World(app.camera, app.width, app.height)

    app.world.add_object(Grid(size=5))
    app.world.add_object(PointLight(10))
    app.world.add_object(ImportedMesh("suzanne.obj"))
    app.world.add_object(Gizmo())

    app.selected_object = None
    app.transform_mode = None  # 'move', 'rotate', 'scale'
    app.axis_constraint = None  # 'x', 'y', 'z'
    app.is_transforming = False
    app.selection_mode = 'vertex'  # or 'face'


def onMouseMove(app, mouseX, mouseY):
    dx = mouseX - app.prev_mouse[0]
    dy = mouseY - app.prev_mouse[1]
    app.prev_mouse = (mouseX, mouseY)

    if app.is_transforming and app.selected_object:
        app.selected_object.transform(app, dx, dy)

    if app.is_zooming:
        app.camera.zoom(app, dy)
    elif app.is_orbiting:
        app.camera.orbit(-dx, dy)


def onMousePress(app, mouseX, mouseY):
    app.prev_mouse = (mouseX, mouseY)
    if app.edit_mode:
        for obj in app.world.objects:
            if obj.is_editable:
                if obj.selection_mode == 'vertex':
                    if obj.check_vertex_selection(mouseX, mouseY):
                        app.selected_object = obj
                        break
                else:  # face selection mode
                    if obj.check_face_selection(mouseX, mouseY):
                        app.selected_object = obj
                        break
    else:
        # Select mesh
        for obj in reversed(app.world.objects):  # Check from topmost object
            if obj.is_selectable and obj.check_selection(mouseX, mouseY):
                app.selected_object = obj
                break
            else:
                app.selected_object = None


def onKeyPress(app, key, modifiers):
    if key == 'space':
        app.is_orbiting = True
    elif key == 'q':
        app.is_zooming = True
    elif key == 'tab':
        app.edit_mode = not app.edit_mode
    elif key == 'g':
        if app.selected_object:
            app.transform_mode = 'move'
            app.is_transforming = True
    elif key == 'r':
        if app.selected_object:
            app.transform_mode = 'rotate'
            app.is_transforming = True
    elif key == 's':
        if app.selected_object:
            app.transform_mode = 'scale'
            app.is_transforming = True
    elif key in ['x', 'y', 'z'] and app.transform_mode:
        app.axis_constraint = key
    elif key == 'x':
        app.camera.snap_to_axis('x')
    elif key == 'y':
        app.camera.snap_to_axis('y')
    elif key == 'z':
        app.camera.snap_to_axis('z')
    elif key == '5':
        app.is_ortho = not app.is_ortho
        app.camera.is_ortho(app)
    elif key == '1':  # Add these new controls
        if app.selected_object:
            app.selected_object.selection_mode = 'vertex'
            app.selected_object.selected_face = None
    elif key == '2':
        if app.selected_object:
            app.selected_object.selection_mode = 'face'
            app.selected_object.selected_vertice = None
    elif key == 'backspace':
        app.world.remove_object(app.selected_object)
        app.selected_object = None
        app.transform_mode = None
        app.axis_constraint = None
        app.is_transforming = False
    elif key == 'A' and 'shift' in modifiers:
        app.world.add_object(ImportedMesh("suzanne.obj"))


def onKeyRelease(app, key):
    if key == 'space':
        app.is_orbiting = False
    elif key == 'q':
        app.is_zooming = False
    elif key in ['g', 'r', 's']:
        app.transform_mode = None
        app.is_transforming = False
        app.axis_constraint = None


def onStep(app):
    pass


def redrawAll(app):
    app.world.render(app)

    drawLabel(f"Frame time: {app.frame_stats.frame_time():.2f}ms", 100, 10)
    drawLabel(f"FPS: {app.frame_stats.fps():.2f}", 100, 25)
    if app.edit_mode:
        drawLabel("Edit Mode", 100, 40, fill='red')
    if app.selected_object:
        drawLabel(f"Selected: {type(app.selected_object).__name__}", 100, 55)
    if app.transform_mode:
        drawLabel(f"Transform Mode: {app.transform_mode}", 100, 70)
    if app.axis_constraint:
        drawLabel(f"Axis Constraint: {app.axis_constraint}", 100, 80)
    if app.selected_object:
        drawLabel(f"Selection Mode: {
                  app.selected_object.selection_mode}", 100, 90)


def main():
    runApp(width=1250, height=800)


if __name__ == "__main__":
    main()

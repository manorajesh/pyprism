from cmu_graphics import *
import time

from objects.primatives import *
from objects.lights import *
from objects.gizmo import *
from rendering.camera import *
from rendering.world import *
from ui import *


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
    app.is_extruding = False
    app.is_panning = False

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
    app.show_help = False

    app.help_x = 30
    app.help_y = app.height - 30

    app.show_add_menu = False
    app.add_menu_x = app.width//5
    app.add_menu_y = 10


def onResize(app):
    app.add_menu_x = app.width//5
    app.help_y = app.height - 30


def onMouseMove(app, mouseX, mouseY):
    dx = mouseX - app.prev_mouse[0]
    dy = mouseY - app.prev_mouse[1]
    app.prev_mouse = (mouseX, mouseY)

    if app.is_extruding and app.selected_object:
        app.selected_object.update_extrusion(dy)
    elif app.is_transforming and app.selected_object:
        app.selected_object.transform(app, dx, dy)
    elif app.is_panning:
        app.camera.pan(dx, dy)
    elif app.is_zooming:
        app.camera.zoom(app, dy)
    elif app.is_orbiting:
        app.camera.orbit(-dx, dy)


def onMousePress(app, mouseX, mouseY):
    # Check add button click
    if (mouseX < app.width//5 and
        mouseY > app.add_menu_y - 15 and
            mouseY < app.add_menu_y + 15):
        app.show_add_menu = not app.show_add_menu
        return

    # Check add menu options
    if app.show_add_menu:
        menu_x = 10
        menu_y = app.add_menu_y + 25
        menu_w = app.width//5 - 20
        menu_h = 25

        # Used ChatGPT to make option lists dynamic instead of fixed to Cube
        # and Plane. Key was to use index of option element to adjust the
        # window in which to check for mouse click.
        for i, option in enumerate(['Cube', 'Plane', 'Suzanne', 'Sphere',
                                    'Teapot']):
            if (menu_x <= mouseX <= menu_x + menu_w and
                    menu_y + i*menu_h <= mouseY <= menu_y + (i+1)*menu_h):
                if option == 'Cube':
                    app.world.add_object(Cube())
                elif option == 'Plane':
                    app.world.add_object(Plane())
                elif option == 'Suzanne':
                    app.world.add_object(ImportedMesh("suzanne.obj"))
                elif option == 'Sphere':
                    app.world.add_object(ImportedMesh("sphere.obj"))
                elif option == 'Teapot':
                    app.world.add_object(ImportedMesh("teapot.obj"))
                app.show_add_menu = False
                return

    # Check if click is in scene list area
    if mouseX < app.width//5:
        y_start = 27
        idx = 0
        for obj in app.world.objects:
            if obj.is_selectable:
                idx += 1
                y = y_start + (idx * 20)
                if y - 10 <= mouseY <= y + 10:
                    app.selected_object = obj
                    return

    # Check if help button is clicked
    if ((mouseX - app.help_x)**2 + (mouseY - app.help_y)**2 <= 100):
        app.show_help = not app.show_help
        return

    if app.show_help:
        app.show_help = False
        return

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
    elif key == 'w':
        app.is_panning = True
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
    elif key == 'e':
        if (app.selected_object and
            app.selected_object.selection_mode == 'face' and
                app.selected_object.selected_face is not None):
            app.is_extruding = True
            app.selected_object.start_extrude_selected_face()


def onKeyRelease(app, key):
    if key == 'space':
        app.is_orbiting = False
    elif key == 'q':
        app.is_zooming = False
    elif key == 'w':
        app.is_panning = False
    elif key in ['g', 'r', 's']:
        app.transform_mode = None
        app.is_transforming = False
        app.axis_constraint = None
    elif key == 'e':
        app.is_extruding = False
        if app.selected_object:
            app.selected_object.finish_extrusion()


def redrawAll(app):
    app.world.render(app)

    drawUi(app)

    drawLabel(f"Frame time: {app.frame_stats.frame_time(
    ):.2f}ms", app.width//5 + 20, 10, fill='white', align='left')
    drawLabel(f"FPS: {app.frame_stats.fps():.2f}", app.width //
              5 + 20, 25, fill='white', align='left')


def main():
    runApp(width=1250, height=800)


if __name__ == "__main__":
    main()

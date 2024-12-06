from cmu_graphics import *


def drawUi(app):
    drawPanel(app)
    drawSceneObjectsList(app)
    drawAddObjectMenu(app)
    drawPropertiesPanel(app)
    drawHelpButton(app)
    if app.show_help:
        drawHelpPopup(app)


def drawPanel(app):
    drawRect(0, 0, app.width//5, app.height, fill=rgb(30, 30, 30), opacity=90)


def drawText(text, x, y, fill='white', font='arial', size=12, align='left',
             highlight_width=0, highlight_height=0, highlight_fill='black',
             bold=False):
    if highlight_width > 0 or highlight_height > 0:
        drawRect(x - 10, y - highlight_height//2, highlight_width,
                 highlight_height, fill=highlight_fill)
    drawLabel(text, x, y, fill=fill,
              size=size, font=font, align=align, bold=bold)


def drawSceneObjectsList(app):
    # Scene Objects
    drawText('Scene', 10, 30, size=14, highlight_width=app.width//5,
             highlight_height=32, highlight_fill=rgb(40, 40, 40), bold=True)

    y_start = 32
    idx = 0
    for obj in app.world.objects:
        if obj.is_selectable:
            idx += 1
            bg_color = rgb(40, 40, 40) if idx % 2 == 0 else rgb(50, 50, 50)
            y = y_start + (idx * 20)
            # so that the list doesn't go below into properties panel
            if y >= app.height//2:
                break

            # Highlight selected object
            if obj == app.selected_object:
                drawRect(0, y - 10, app.width//5, 20,
                         fill=bg_color, border='orange', borderWidth=1)
            else:
                drawRect(0, y - 10, app.width//5, 20, fill=bg_color)

            name = obj.name if hasattr(obj, 'name') else type(obj).__name__
            drawText(name, 15, y, size=12)


def drawObjectListItem(app, obj, background):
    x = 10
    y = 20 * app.world.objects.index(obj)
    w = 200
    h = 20

    drawText(type(obj).__name__, x + 5, y + 10, highlight_width=w -
             10, highlight_height=h, highlight_fill=background)


def drawPropertiesPanel(app):
    if not app.selected_object:
        return

    # Padding so that properties panel doesn't overlap with scene list
    y = app.height // 2

    # Properties Header
    drawText('Properties', 10, y, size=14, highlight_width=app.width//5,
             highlight_height=27, highlight_fill=rgb(40, 40, 40), bold=True)

    y += 30
    # Mode Section
    drawText('Mode:', 15, y, size=12)
    mode_color = 'orange' if app.edit_mode else 'white'
    drawText('Edit' if app.edit_mode else 'Object',
             60, y, fill=mode_color, size=12)

    # Object Properties
    y += 20
    drawText(f'Vertices: {len(app.selected_object.vertices)}', 15, y, size=12)

    if app.selected_object.is_editable:
        drawText(f'Trianges: {len(app.selected_object.indices) // 3}',
                 15, y + 20, size=12)

    # Selection Mode
    if app.edit_mode:
        y += 50
        drawText('Select:', 15, y, size=12)
        vertex_color = 'orange' if \
            app.selected_object.selection_mode == 'vertex' else 'white'
        face_color = 'orange' if \
            app.selected_object.selection_mode == 'face' else 'white'
        drawText('Vertex (1)', 60, y, fill=vertex_color, size=12)
        drawText('Face (2)', 60, y + 20, fill=face_color, size=12)

    # Transform Section
    y += 60
    drawText('Transform:', 15, y, size=12)
    move_color = 'orange' if app.transform_mode == 'move' else 'white'
    rotate_color = 'orange' if app.transform_mode == 'rotate' else 'white'
    scale_color = 'orange' if app.transform_mode == 'scale' else 'white'
    drawText('Move (G)', 90, y, fill=move_color, size=12)
    drawText('Rotate (R)', 90, y + 20, fill=rotate_color, size=12)
    drawText('Scale (S)', 90, y + 40, fill=scale_color, size=12)

    # Axis Constraint
    if app.transform_mode:
        y += 70
        drawText('Axis:', 15, y, size=12)
        x_color = 'orange' if app.axis_constraint == 'x' else 'white'
        y_color = 'orange' if app.axis_constraint == 'y' else 'white'
        z_color = 'orange' if app.axis_constraint == 'z' else 'white'
        drawText('X', 70, y, fill=x_color, size=12)
        drawText('Y', 90, y, fill=y_color, size=12)
        drawText('Z', 110, y, fill=z_color, size=12)


def drawHelpButton(app):
    drawCircle(app.help_x, app.help_y, 10, fill=rgb(60, 60, 60))
    drawLabel('?', app.help_x, app.help_y, size=14, bold=True, fill='white')


def drawHelpPopup(app):
    drawRect(0, 0, app.width, app.height, fill='black', opacity=50)

    w = 420
    h = 540
    x = app.width//2 - w//2
    y = app.height//2 - h//2
    drawRect(x, y, w, h, fill=rgb(40, 40, 40), border='white')

    help_text = [
        ('Navigation', [
            'Space + Mouse: Orbit camera',
            'q + Mouse: Zoom camera',
            'w + Mouse: Pan camera',
            'X/Y/Z: Snap view to axis',
            '5: Toggle orthographic view'
        ]),
        ('Selection', [
            'Click: Select object',
            'Tab: Toggle edit mode',
            '1: Vertex selection mode',
            '2: Face selection mode'
        ]),
        ('Transformation', [
            'G: Move',
            'R: Rotate',
            'S: Scale',
            'X/Y/Z: Constraint to axis'
        ]),
        ('Modeling', [
            'E: Extrude (in face mode)',
            'Backspace: Delete selected object'
        ]),
        ('Click anywhere to close', [])
    ]

    ty = y + 40
    for section, items in help_text:
        drawText(section, x + 20, ty, size=14, bold=True)
        ty += 30
        for item in items:
            drawText(item, x + 40, ty, size=12)
            ty += 20
        ty += 10


def drawAddObjectMenu(app):
    # Add button
    y = app.add_menu_y
    drawText('+ Add', 10, y, size=14, highlight_width=app.width//5,
             highlight_height=25, highlight_fill=rgb(40, 40, 40))

    if app.show_add_menu:
        # Menu background
        options = ['Cube', 'Plane', 'Suzanne', 'Sphere', 'Teapot']
        menu_y = y + 25
        menu_h = 25 * len(options)
        drawRect(10, menu_y, app.width//5-20, menu_h,
                 fill=rgb(50, 50, 50), border=rgb(60, 60, 60))

        # Menu options
        for i, option in enumerate(options):
            option_y = menu_y + (i * 25) + 12
            drawText(option, 20, option_y, size=12)

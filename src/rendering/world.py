from cmu_graphics import *
from objects.lights import *
from rendering.path_tracer import *


class World:
    def __init__(self, camera, width, height):
        self.camera = camera
        self.objects = []
        self.light = None
        self.width = width
        self.height = height

    def add_object(self, obj):
        if isinstance(obj, Light):
            self.light = obj
        self.objects.append(obj)

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    def get_light_direction(self):
        if self.light:
            return self.light.get_view_direction()

    def render(self, app):
        if app.width != self.width or app.height != self.height:
            self.camera.resize(app.width, app.height)
            self.width = app.width
            self.height = app.height

        # Collect all triangles from all objects
        all_triangles = []
        for obj in self.objects:
            triangles = obj.render(app)
            if triangles:
                all_triangles.extend(triangles)

        # Sort all triangles by depth
        all_triangles.sort(key=lambda tri: tri['depth'], reverse=True)

        # Draw all triangles in sorted order
        for tri in all_triangles:
            if app.edit_mode and not tri.get('is_editable', False):
                drawPolygon(*tri['points'], fill=tri['color'], opacity=50)
            else:
                drawPolygon(*tri['points'],
                            fill=tri['color'],
                            border=tri.get('border', None),
                            borderWidth=tri.get('borderWidth', 0),
                            opacity=tri.get('opacity', 100))

    def onMouseMove(self, mouseX, mouseY, edit_mode=False):
        if edit_mode:
            for obj in self.objects:
                if obj.is_editable:
                    obj.point_over_vertex(mouseX, mouseY)

    def render_path_traced(self, samples=1):
        """Render the scene using path tracing"""
        tracer = PathTracer(100, 100, samples)
        image = tracer.render(self)
        return image

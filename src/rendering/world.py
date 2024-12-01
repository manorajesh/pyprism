class World:
    def __init__(self, camera, width, height):
        self.camera = camera
        self.objects = []
        self.width = width
        self.height = height

    def addObject(self, obj):
        self.objects.append(obj)

    def removeObject(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    def render(self, app):
        if app.width != self.width or app.height != self.height:
            self.camera.resize(app.width, app.height)
            self.width = app.width
            self.height = app.height

        for obj in self.objects:
            obj.render(app)

    def onMouseMove(self, mouseX, mouseY, edit_mode=False):
        if edit_mode:
            for obj in self.objects:
                if obj.is_editable:
                    obj.point_over_vertex(mouseX, mouseY)

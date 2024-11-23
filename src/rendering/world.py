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

    def render(self, width, height):
        if width != self.width or height != self.height:
            self.camera.resize(width, height)
            self.width = width
            self.height = height

        for obj in self.objects:
            obj.render(self.camera, width, height)

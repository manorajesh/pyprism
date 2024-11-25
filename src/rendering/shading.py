from cmu_graphics import *
from matrix_util import *


class ShadingModel:
    def __init__(self, diffuse=1.0, specular=1.0):
        self.diffuse = diffuse
        self.specular = specular

    def shade(self):
        raise NotImplementedError


class Lambertian(ShadingModel):
    def shade(self, normal, light_dir):
        # Normalize vectors
        normal = normalize(normal)
        light_dir = normalize(light_dir)

        # Compute the diffuse intensity
        intensity = self.diffuse * max(0.2, dot_product(normal, light_dir))

        # Scale to 0-255 and clamp
        intensity = int(min(max(intensity * 255, 0), 200))
        return rgb(intensity, intensity, intensity)


class Phong(ShadingModel):
    pass

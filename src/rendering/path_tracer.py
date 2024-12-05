import numpy as np
from random import random
import math


def ray_triangle_intersect(ray_origin, ray_dir, v0, v1, v2):
    """
    Checks if a ray intersects a triangle and returns the intersection point and distance.

    Parameters:
        ray_origin (numpy array): Origin of the ray (3D point).
        ray_dir (numpy array): Direction of the ray (3D vector, normalized).
        v0, v1, v2 (numpy arrays): Vertices of the triangle (3D points).

    Returns:
        tuple: (intersection_point, t) where intersection_point is the point of intersection
               and t is the distance from the ray origin to the intersection. 
               Returns (None, None) if there's no intersection.
    """
    epsilon = 1e-8  # Tolerance to handle numerical precision issues

    # Compute edges of the triangle
    edge1 = v1 - v0
    edge2 = v2 - v0

    # Compute determinant
    h = np.cross(ray_dir, edge2)
    a = np.dot(edge1, h)

    # If the determinant is close to 0, the ray is parallel to the triangle
    if abs(a) < epsilon:
        return None, None

    # Compute the distance from v0 to the ray origin
    f = 1.0 / a
    s = ray_origin - v0

    # Calculate u parameter and test bounds
    u = f * np.dot(s, h)
    if u < 0.0 or u > 1.0:
        return None, None

    # Calculate v parameter and test bounds
    q = np.cross(s, edge1)
    v = f * np.dot(ray_dir, q)
    if v < 0.0 or u + v > 1.0:
        return None, None

    # Calculate t (distance from ray origin to intersection point)
    t = f * np.dot(edge2, q)
    if t > epsilon:  # Ray intersection with the triangle
        intersection_point = ray_origin + ray_dir * t
        return intersection_point, t

    # No valid intersection
    return None, None


def save_to_ppm(filename, image):
    """Save image array to PPM file"""
    height, width, _ = image.shape
    maxval = 255

    # Ensure values are in valid range
    image = np.clip(image * 255, 0, maxval).astype(np.uint8)

    with open(filename, 'wb') as f:
        # Write PPM header
        f.write(f'P6\n{width} {height}\n{maxval}\n'.encode())

        # Write pixel data
        for y in range(height):
            for x in range(width):
                f.write(bytes(image[y, x]))


class PathTracer:
    def __init__(self, width, height, samples=1):
        self.width = width
        self.height = height
        self.samples = samples
        self.aspect_ratio = width / height

    def get_camera_ray(self, camera, x, y):
        """Convert screen coordinates to ray direction"""
        # Convert to NDC space
        ndc_x = (2.0 * x / self.width - 1.0) * self.aspect_ratio
        ndc_y = 1.0 - 2.0 * y / self.height

        # Get camera direction and right vector
        forward = np.array(camera.get_view_direction())
        right = np.cross(forward, [0, 1, 0])
        up = np.cross(right, forward)

        # Calculate ray direction
        fov_rad = math.radians(camera.fov)
        ray_dir = (ndc_x * right + ndc_y * up +
                   forward * (1.0/math.tan(fov_rad/2.0)))
        return np.array(camera.position()), np.array(ray_dir)/np.linalg.norm(ray_dir)

    def trace_ray(self, origin, direction, scene):
        """Simplified ray tracer with direct illumination only"""
        closest_t = float('inf')
        closest_hit = None

        # Check intersection with all triangles in scene
        for obj in scene.objects:
            if not hasattr(obj, 'vertices') or not hasattr(obj, 'indices') or not obj.should_render_mesh:
                continue

            vertices = obj.vertices
            indices = obj.indices

            for i in range(0, len(indices), 3):
                idx0 = indices[i]
                idx1 = indices[i+1]
                idx2 = indices[i+2]
                try:
                    v0 = np.array(vertices[idx0][:3])
                    v1 = np.array(vertices[idx1][:3])
                    v2 = np.array(vertices[idx2][:3])
                except IndexError:
                    print("Invalid index in object")
                    continue

                x, y = ray_triangle_intersect(origin, direction, v0, v1, v2)
                if x is not None and y is not None:
                    if y < closest_t:
                        print(f"Intersection at t = {y}")
                        closest_t = y
                        normal = obj.get_normal(v0, v1, v2)
                        closest_hit = (y, normal)

        if closest_hit is None:
            return np.zeros(3)  # Background color (black)

        # Direct lighting only
        hit_point = origin + closest_hit[0] * direction
        normal = closest_hit[1]
        light_dir = np.array(scene.get_light_direction())

        # Basic diffuse shading
        light_contribution = max(0, np.dot(normal, -light_dir))
        return np.array([1, 1, 1]) * light_contribution

    def render(self, scene):
        """Render scene and save to PPM"""
        image = np.zeros((self.height, self.width, 3))
        total_pixels = self.width * self.height
        pixels_done = 0

        for y in range(self.height):
            for x in range(self.width):
                pixels_done += 1
                if pixels_done % 1000 == 0:
                    print(f"Progress: {(pixels_done/total_pixels)*100:.1f}%")

                color = np.zeros(3)
                for _ in range(self.samples):
                    # Add some randomness for anti-aliasing
                    rx = x + random() - 0.5
                    ry = y + random() - 0.5

                    ray_origin, ray_dir = self.get_camera_ray(
                        scene.camera, rx, ry)
                    color += self.trace_ray(ray_origin, ray_dir, scene)

                image[y, x] = color / self.samples

        # Save the rendered image
        save_to_ppm('render.ppm', image)
        return image

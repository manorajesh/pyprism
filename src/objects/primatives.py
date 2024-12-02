
from matrix_util import *
from cmu_graphics import *
from rendering.shading import *


class Mesh:
    def __init__(self, vertices, indices, shading_model=Lambertian(), is_editable=False, is_selectable=True):
        self.vertices = vertices  # List of [x,y,z,w] vertices
        self.indices = indices    # List of triangle indices
        self.shading_model = shading_model

        # Screen coordinates for vertices
        # Used for point selection in edit mode
        self.screen_coords = None

        self.is_editable = is_editable
        self.is_selectable = is_selectable
        self.selected_vertex = None
        self.transform_matrix = identity_matrix()

    def render(self, app):
        # Perspective projection
        # https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/building-basic-perspective-projection-matrix.html

        # Apply transformations to vertices
        transformed_vertices = [matrix_vector_multiply(
            app.camera.projection_view_matrix,
            matrix_vector_multiply(self.transform_matrix, v)
        ) for v in self.vertices]

        # Perspective division and conversion to NDC
        ndc = []
        for point in transformed_vertices:
            if app.is_ortho:
                ndc.append(point[:3])
            else:
                ndc.append([point[0]/point[3], point[1] /
                           point[3], point[2]/point[3]])

        # Screen space conversion
        screen_coords = [[(x + 1) * (app.width / 2), (1 - y) *
                          (app.height / 2), z] for x, y, z in ndc]

        # Render with drawPolygon
        triangles = []
        for i in range(0, len(self.indices), 3):
            idx0 = self.indices[i]
            idx1 = self.indices[i+1]
            idx2 = self.indices[i+2]

            # Get screen coordinates for each vertex
            v0 = screen_coords[idx0]
            v1 = screen_coords[idx1]
            v2 = screen_coords[idx2]

            # Calculate center point
            center = [
                (v0[0] + v1[0] + v2[0]) / 3,
                (v0[1] + v1[1] + v2[1]) / 3
            ]

            # Inset vertices slightly away from center
            inset = 1.01
            v0_inset = [
                center[0] + (v0[0] - center[0]) * inset,
                center[1] + (v0[1] - center[1]) * inset,
                v0[2]
            ]
            v1_inset = [
                center[0] + (v1[0] - center[0]) * inset,
                center[1] + (v1[1] - center[1]) * inset,
                v1[2]
            ]
            v2_inset = [
                center[0] + (v2[0] - center[0]) * inset,
                center[1] + (v2[1] - center[1]) * inset,
                v2[2]
            ]

            # Use inset points for drawing
            points = [v0_inset[0], v0_inset[1], v1_inset[0],
                      v1_inset[1], v2_inset[0], v2_inset[1]]

            # Get world coordinates for normal calculation
            world_v0 = self.vertices[idx0][:3]
            world_v1 = self.vertices[idx1][:3]
            world_v2 = self.vertices[idx2][:3]

            # Calculate edges and normal
            edge1 = [world_v1[i] - world_v0[i] for i in range(3)]
            edge2 = [world_v2[i] - world_v0[i] for i in range(3)]
            normal = cross(edge1, edge2)

            # Backface culling
            if dot(normal, app.camera.get_view_direction()) <= 0 and not app.edit_mode:
                continue  # Skip triangles facing away

            # Shading
            color = self.shading_model.shade(
                normal, light_dir=app.world.get_light_direction())

            # Calculate average depth
            avg_depth = sum([v[2] for v in [v0, v1, v2]]) / 3

            triangles.append(
                {'depth': avg_depth, 'points': points, 'color': color})

        triangles.sort(key=lambda tri: tri['depth'], reverse=True)

        self.screen_coords = screen_coords

        # Add mesh properties to triangles
        for tri in triangles:
            tri['is_editable'] = self.is_editable
            if not app.edit_mode and self == app.selected_object:
                tri['border'] = 'orange'
                tri['borderWidth'] = 0.5
            elif app.edit_mode:
                tri['opacity'] = 50

        # Draw vertices in edit mode
        if app.edit_mode:
            for point in screen_coords:
                drawCircle(point[0], point[1], 2, fill='white')

        # Highlight selected vertex
        if app.edit_mode and self.selected_vertex is not None:
            point = screen_coords[self.selected_vertex]
            drawCircle(point[0], point[1], 3, fill='orange')

        return triangles

    def point_over_vertex(self, x, y, threshold=5):
        for point in self.screen_coords:
            if abs(point[0] - x) < threshold and abs(point[1] - y) < threshold:
                self.selected_vertex = point

    def check_selection(self, mouseX, mouseY):
        if not self.screen_coords:
            return False

        # Simple bounding box check
        min_x = min(point[0] for point in self.screen_coords)
        max_x = max(point[0] for point in self.screen_coords)
        min_y = min(point[1] for point in self.screen_coords)
        max_y = max(point[1] for point in self.screen_coords)
        return min_x <= mouseX <= max_x and min_y <= mouseY <= max_y

    def check_vertex_selection(self, mouseX, mouseY, threshold=5):
        if not self.screen_coords:
            return

        for idx, point in enumerate(self.screen_coords):
            dx = point[0] - mouseX
            dy = point[1] - mouseY
            if dx * dx + dy * dy < threshold * threshold:
                self.selected_vertex = idx
                return
        self.selected_vertex = None

    def transform(self, app, dx, dy):
        # Making sure that you can only transform
        # vertices when in edit mode
        if not app.edit_mode:
            self.selected_vertex = None

        # Map screen movement to world coordinates
        movement_factor = 0.01  # Adjust as necessary
        if app.transform_mode == 'move':
            move_vector = [dx * movement_factor, -dy *
                           movement_factor, -dx * movement_factor]
            if app.axis_constraint == 'x':
                move_vector[1] = move_vector[2] = 0
            elif app.axis_constraint == 'y':
                move_vector[0] = move_vector[2] = 0
            elif app.axis_constraint == 'z':
                move_vector[0] = move_vector[1] = 0
            if self.selected_vertex is not None:
                # Move single vertex
                idx = self.selected_vertex
                self.vertices[idx] = vector_add(
                    self.vertices[idx], move_vector + [0])
            else:
                # Move entire mesh
                self.apply_translation(move_vector)
        elif app.transform_mode == 'rotate':
            angle = dx * movement_factor
            if app.axis_constraint == 'x':
                axis = [1, 0, 0]
            elif app.axis_constraint == 'y':
                axis = [0, 1, 0]
            elif app.axis_constraint == 'z':
                axis = [0, 0, 1]
            else:
                axis = app.camera.get_view_direction()
            self.apply_rotation(angle, axis)
        elif app.transform_mode == 'scale':
            scale_factor = 1 + dy * movement_factor
            if app.axis_constraint == 'x':
                scale_vector = [scale_factor, 1, 1]
            elif app.axis_constraint == 'y':
                scale_vector = [1, scale_factor, 1]
            elif app.axis_constraint == 'z':
                scale_vector = [1, 1, scale_factor]
            else:
                scale_vector = [scale_factor, scale_factor, scale_factor]
            self.apply_scaling(scale_vector)

    def apply_translation(self, move_vector):
        translation = translation_matrix(*move_vector)
        self.transform_matrix = matrix_multiply(
            translation, self.transform_matrix)

    def apply_rotation(self, angle, axis):
        rotation = rotation_matrix(angle, axis)
        self.transform_matrix = matrix_multiply(
            rotation, self.transform_matrix)

    def apply_scaling(self, scale_vector):
        scaling = scaling_matrix(*scale_vector)
        self.transform_matrix = matrix_multiply(scaling, self.transform_matrix)


class Cube(Mesh):
    def __init__(self, size=1.0):
        s = size/2
        vertices = [
            # Front face
            [-s, -s,  s, 1],  # 0
            [s, -s,  s, 1],  # 1
            [s,  s,  s, 1],  # 2
            [-s,  s,  s, 1],  # 3
            # Back face
            [-s, -s, -s, 1],  # 4
            [s, -s, -s, 1],  # 5
            [s,  s, -s, 1],  # 6
            [-s,  s, -s, 1],  # 7
        ]

        indices = [
            # Front
            0, 1, 2,  0, 2, 3,
            # Right
            1, 5, 6,  1, 6, 2,
            # Back
            5, 4, 7,  5, 7, 6,
            # Left
            4, 0, 3,  4, 3, 7,
            # Top
            3, 2, 6,  3, 6, 7,
            # Bottom
            4, 5, 1,  4, 1, 0
        ]

        super().__init__(vertices, indices, is_editable=True)


class Plane(Mesh):
    def __init__(self, width=1.0):
        s = width/2
        vertices = [
            [-s, -s, 0, 1],
            [s, -s, 0, 1],
            [s, s, 0, 1],
            [-s, s, 0, 1]
        ]

        indices = [
            0, 1, 2,  0, 2, 3
        ]

        super().__init__(vertices, indices, is_editable=True)


class Grid(Mesh):
    def __init__(self, size=10.0, divisions=10):
        vertices = []
        indices = []

        half_size = size / 2.0
        step = size / divisions

        # Generate vertices for grid lines along X and Z axes
        for i in range(divisions + 1):
            position = -half_size + i * step
            vertices.append([position, 0, -half_size, 1])  # Start point
            vertices.append([position, 0, half_size, 1])   # End point
            indices.extend([len(vertices) - 2, len(vertices) - 1])

            vertices.append([-half_size, 0, position, 1])  # Start point
            vertices.append([half_size, 0, position, 1])   # End point
            indices.extend([len(vertices) - 2, len(vertices) - 1])

        super().__init__(vertices, indices, is_selectable=False)

    def render(self, app):
        # The rendering logic is the same as any object in the scene
        # Just the final drawLine call is different

        # Transform vertices
        transformed_vertices = [matrix_vector_multiply(
            app.camera.projection_view_matrix, v) for v in self.vertices]

        # Perspective division and conversion to NDC
        ndc = []
        for point in transformed_vertices:
            if app.is_ortho:
                ndc.append(point[:3])
            else:
                ndc.append([point[0]/point[3], point[1] /
                           point[3], point[2]/point[3]])

        # Screen space conversion
        screen_coords = [[(x + 1) * (app.width / 2), (1 - y) * (app.height / 2)]
                         for x, y, z in ndc]

        # Draw grid lines
        for i in range(0, len(self.indices), 2):
            idx_start = self.indices[i]
            idx_end = self.indices[i + 1]

            start_point = screen_coords[idx_start]
            end_point = screen_coords[idx_end]

            # TODO: Issue with start_point and end_point being out of bounds
            # and too large when camera is zoomed in

            # color the two center x and z axis lines red and blue
            if idx_start == 20:
                drawLine(start_point[0], start_point[1],
                         end_point[0], end_point[1], fill='blue')
            elif idx_start == 22:
                drawLine(start_point[0], start_point[1],
                         end_point[0], end_point[1], fill='red')
            else:
                drawLine(start_point[0], start_point[1],
                         end_point[0], end_point[1],
                         fill=rgb(50, 50, 50))


class ImportedMesh(Mesh):
    def __init__(self, file_path, shading_model=Lambertian()):
        vertices, indices = self.load_obj(file_path)
        super().__init__(vertices, indices, shading_model, is_editable=True)

    @staticmethod
    def load_obj(file_path):
        vertices = []
        indices = []

        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('v '):  # vertices
                    parts = line.strip().split()
                    x, y, z = map(float, parts[1:4])
                    # Add homogeneous coordinate w=1
                    vertices.append([x, y, z, 1])
                elif line.startswith('f '):  # face info/indices
                    parts = line.strip().split()
                    # obj file indices start from 1 so we subtract 1
                    face_indices = [int(part.split('/')[0]) -
                                    1 for part in parts[1:]]
                    if len(face_indices) == 3:
                        indices.extend(face_indices)
                    elif len(face_indices) > 3:
                        raise ValueError(
                            'Only triangles are supported for now')
        return vertices, indices

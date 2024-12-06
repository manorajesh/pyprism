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
        self.selection_mode = 'vertex'  # 'vertex' or 'face'
        self.selected_face = None

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
            # to avoid z-fighting (overlapping triangles)
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
                normal, light_dir=app.world.get_light_direction()) if self.shading_model else 'white'

            # Calculate average depth
            avg_depth = sum([v[2] for v in [v0, v1, v2]]) / 3

            triangles.append(
                {'depth': avg_depth, 'points': points, 'color': color})

        # Already sorted by world render
        # triangles.sort(key=lambda tri: tri['depth'], reverse=True)

        self.screen_coords = screen_coords

        # Add mesh properties to triangles
        for tri in triangles:
            tri['is_editable'] = self.is_editable
            if not app.edit_mode and self == app.selected_object:
                tri['border'] = 'orange'
                tri['borderWidth'] = 0.5
            elif app.edit_mode and app.selected_object == self:
                tri['opacity'] = 50

        # Draw vertices in edit mode
        if app.edit_mode and self.selection_mode == 'vertex' and app.selected_object == self:
            for point in screen_coords:
                drawCircle(point[0], point[1], 2, fill='white')

        # Highlight selected vertex
        if app.edit_mode and self.selected_vertex is not None:
            point = screen_coords[self.selected_vertex]
            drawCircle(point[0], point[1], 3, fill='orange')

        # Highlight selected face
        if app.edit_mode and self.selection_mode == 'face' and self.selected_face is not None:
            idx0 = self.indices[self.selected_face]
            idx1 = self.indices[self.selected_face + 1]
            idx2 = self.indices[self.selected_face + 2]

            v0 = screen_coords[idx0]
            v1 = screen_coords[idx1]
            v2 = screen_coords[idx2]

            points = [v0[0], v0[1], v1[0], v1[1], v2[0], v2[1]]
            drawPolygon(*points, fill=None, border='orange', borderWidth=2)

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
        if not self.screen_coords or self.selection_mode != 'vertex':
            return

        self.selected_face = None

        for idx, point in enumerate(self.screen_coords):
            dx = point[0] - mouseX
            dy = point[1] - mouseY
            if dx * dx + dy * dy < threshold * threshold:
                self.selected_vertex = idx
                return
        self.selected_vertex = None

    def check_face_selection(self, mouseX, mouseY):
        if not self.screen_coords or self.selection_mode != 'face':
            return False

        self.selected_vertex = None

        # Store faces that contain the clicked point along with their depths
        candidate_faces = []

        for i in range(0, len(self.indices), 3):
            idx0 = self.indices[i]
            idx1 = self.indices[i+1]
            idx2 = self.indices[i+2]

            v0 = self.screen_coords[idx0]
            v1 = self.screen_coords[idx1]
            v2 = self.screen_coords[idx2]

            if point_in_triangle(mouseX, mouseY,
                                 (v0[0], v0[1]),
                                 (v1[0], v1[1]),
                                 (v2[0], v2[1])):
                # Calculate average depth of the face
                avg_depth = (v0[2] + v1[2] + v2[2]) / 3
                candidate_faces.append((i, avg_depth))

        if not candidate_faces:
            self.selected_face = None
            return False

        # Sort faces by depth and select the closest one
        candidate_faces.sort(key=lambda x: x[1])
        closest_face_idx = candidate_faces[0][0]

        if closest_face_idx == self.selected_face:
            self.selected_face = None  # Deselect if clicking same face
        else:
            self.selected_face = closest_face_idx  # Select new face
        return True

    def transform(self, app, dx, dy):
        if not app.edit_mode or self.selection_mode == 'face':
            self.selected_vertex = None

        if not app.edit_mode or self.selection_mode == 'vertex':
            self.selected_face = None

        # Get camera right and up vectors for screen-space movement
        # https://gamedev.stackexchange.com/a/139704
        view_dir = app.camera.get_view_direction()
        camera_right = normalize(cross([0, 1, 0], view_dir))
        camera_up = normalize(cross(view_dir, camera_right))

        movement_factor = 0.01
        if app.transform_mode == 'move':
            # Create movement vector based on camera orientation
            # https://www.youtube.com/watch?v=7kGCrq1cJew
            right_movement = [x * dx * movement_factor for x in camera_right]
            up_movement = [x * -dy * movement_factor for x in camera_up]
            move_vector = vector_add(right_movement, up_movement)

            if app.axis_constraint == 'x':
                move_vector = [move_vector[0], 0, 0]
            elif app.axis_constraint == 'y':
                move_vector = [0, move_vector[1], 0]
            elif app.axis_constraint == 'z':
                move_vector = [0, 0, move_vector[2]]

            if self.selection_mode == 'vertex' and self.selected_vertex is not None:
                # Move single vertex
                idx = self.selected_vertex
                self.vertices[idx] = vector_add(
                    self.vertices[idx], move_vector + [0])
            elif self.selection_mode == 'face' and self.selected_face:
                # Move vertices of selected face
                affected_vertices = set()
                for i in range(3):
                    affected_vertices.add(self.indices[self.selected_face + i])

                for vertex_idx in affected_vertices:
                    self.vertices[vertex_idx] = vector_add(
                        self.vertices[vertex_idx], move_vector + [0])
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

    def start_extrude_selected_face(self):
        if self.selected_face is None:
            return

        # Indices of the selected face
        idx0 = self.indices[self.selected_face]
        idx1 = self.indices[self.selected_face + 1]
        idx2 = self.indices[self.selected_face + 2]
        self.extrude_face_indices = [idx0, idx1, idx2]

        # Original positions of the face vertices
        self.extrude_original_vertices = [
            self.vertices[idx0][:3],
            self.vertices[idx1][:3],
            self.vertices[idx2][:3]
        ]

        # Compute the face normal
        edge1 = [self.extrude_original_vertices[1][i] -
                 self.extrude_original_vertices[0][i] for i in range(3)]
        edge2 = [self.extrude_original_vertices[2][i] -
                 self.extrude_original_vertices[0][i] for i in range(3)]
        self.extrude_normal = normalize(cross(edge1, edge2))

        # Duplicate vertices for the new face
        self.extrude_new_vertices_indices = []
        for v in self.extrude_original_vertices:
            new_v = v + [1]
            self.vertices.append(new_v)
            self.extrude_new_vertices_indices.append(len(self.vertices) - 1)

        idx_new0, idx_new1, idx_new2 = self.extrude_new_vertices_indices

        # Add side faces and extruded face
        idx_list = [
            idx0, idx1, idx_new1, idx0, idx_new1, idx_new0,  # Side face 1
            idx1, idx2, idx_new2, idx1, idx_new2, idx_new1,  # Side face 2
            idx2, idx0, idx_new0, idx2, idx_new0, idx_new2,  # Side face 3
            idx_new0, idx_new1, idx_new2  # Extruded face
        ]
        self.indices.extend(idx_list)

        # Initialize extrusion offset
        self.extrude_offset = 0.0

    def update_extrusion(self, dy):
        movement_factor = 0.01

        # Get camera right and up vectors for screen-space movement
        view_dir = app.camera.get_view_direction()
        camera_right = normalize(cross([0, 1, 0], view_dir))
        camera_up = normalize(cross(view_dir, camera_right))

        up_movement = [x * -dy * movement_factor for x in camera_up]
        self.extrude_offset += up_movement[1]

        # Update positions of new vertices along the normal
        for i, idx in enumerate(self.extrude_new_vertices_indices):
            offset_vector = [self.extrude_normal[j] *
                             self.extrude_offset for j in range(3)]
            new_position = [self.extrude_original_vertices[i]
                            [j] + offset_vector[j] for j in range(3)]
            self.vertices[idx] = new_position + [1]

    def finish_extrusion(self):
        # Reset extrusion variables
        self.selected_face = None
        self.extrude_face_indices = None
        self.extrude_new_vertices_indices = None
        self.extrude_original_vertices = None
        self.extrude_normal = None
        self.extrude_offset = 0.0

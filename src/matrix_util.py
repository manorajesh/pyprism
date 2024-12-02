import math


def matrix_multiply(a, b):
    result = []
    for i in range(4):
        row = []
        for j in range(4):
            sum = 0
            for k in range(4):
                sum += a[i][k] * b[k][j]
            row.append(sum)
        result.append(row)
    return result


def matrix_vector_multiply(matrix, vector):
    result = []
    for i in range(4):
        sum = 0
        for j in range(4):
            sum += matrix[i][j] * vector[j]
        result.append(sum)
    return result


def cross(a, b):
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ]


def subtract(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def length(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)


def normalize(v):
    l = length(v)
    if l == 0:
        return [0, 0, 0]

    return [v[0] / l, v[1] / l, v[2] / l]


def dot(a, b):
    return sum([a[i] * b[i] for i in range(len(a))])


def identity_matrix():
    return [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]


def translation_matrix(tx, ty, tz):
    return [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ]


def rotation_matrix(angle, axis):
    # https://math.libretexts.org/Bookshelves/Applied_Mathematics/Mathematics_for_Game_Developers_(Burzynski)/04%3A_Matrices/4.06%3A_Rotation_Matrices_in_3-Dimensions
    def rotation_x(angle):
        c = math.cos(angle)
        s = math.sin(angle)
        return [
            [1, 0,  0, 0],
            [0, c, -s, 0],
            [0, s,  c, 0],
            [0, 0,  0, 1]
        ]

    def rotation_y(angle):
        c = math.cos(angle)
        s = math.sin(angle)
        return [
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ]

    def rotation_z(angle):
        c = math.cos(angle)
        s = math.sin(angle)
        return [
            [c, -s, 0, 0],
            [s,  c, 0, 0],
            [0,  0, 1, 0],
            [0,  0, 0, 1]
        ]

    # Normalize axis to get components
    axis = normalize(axis)
    x, y, z = axis

    # Get rotation matrix for each axis and scale by component
    rx = rotation_x(angle * x)
    ry = rotation_y(angle * y)
    rz = rotation_z(angle * z)

    # Combine rotations (order matters: Z * Y * X)
    return matrix_multiply(rz, matrix_multiply(ry, rx))


def scaling_matrix(sx, sy, sz):
    # https://en.wikipedia.org/wiki/Scaling_(geometry)
    return [
        [sx, 0,  0,  0],
        [0,  sy, 0,  0],
        [0,  0,  sz, 0],
        [0,  0,  0,  1]
    ]


def vector_add(a, b):
    return [a[i] + b[i] for i in range(len(a))]


def point_in_triangle(px, py, v1, v2, v3):
    # https://www.geeksforgeeks.org/check-whether-a-given-point-lies-inside-a-triangle-or-not/
    def area(x1, y1, x2, y2, x3, y3):
        return abs((x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))/2.0)

    # Calculate area of the entire triangle
    total_area = area(v1[0], v1[1], v2[0], v2[1], v3[0], v3[1])

    # Calculate areas of three triangles made between the point and triangle vertices
    area1 = area(px, py, v2[0], v2[1], v3[0], v3[1])
    area2 = area(v1[0], v1[1], px, py, v3[0], v3[1])
    area3 = area(v1[0], v1[1], v2[0], v2[1], px, py)

    # Point is inside if sum of three areas equals total area
    return abs(total_area - (area1 + area2 + area3)) < 0.0001

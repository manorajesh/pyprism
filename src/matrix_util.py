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


def cross_product(a, b):
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ]


def dot_product(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def subtract(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def length(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)


def normalize(v):
    l = length(v)
    if l == 0:
        return [0, 0, 0]

    return [v[0] / l, v[1] / l, v[2] / l]

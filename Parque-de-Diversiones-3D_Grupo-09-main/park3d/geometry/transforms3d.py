"""Matrices homogéneas 4 x 4 para transformaciones y cámara en 3D."""

from __future__ import annotations

from math import cos, radians, sin

Matrix4 = list[list[float]]
Point3 = tuple[float, float, float]


def identity4() -> Matrix4:
    return [[float(row == column) for column in range(4)] for row in range(4)]


def multiply4(left: Matrix4, right: Matrix4) -> Matrix4:
    return [[sum(left[row][k] * right[k][column] for k in range(4))
             for column in range(4)] for row in range(4)]


def translation3(tx: float, ty: float, tz: float) -> Matrix4:
    matrix = identity4()
    matrix[0][3], matrix[1][3], matrix[2][3] = tx, ty, tz
    return matrix


def scale3(sx: float, sy: float, sz: float) -> Matrix4:
    return [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]]


def rotation_x(degrees: float) -> Matrix4:
    angle = radians(degrees)
    c, s = cos(angle), sin(angle)
    return [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]


def rotation_y(degrees: float) -> Matrix4:
    angle = radians(degrees)
    c, s = cos(angle), sin(angle)
    return [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]]


def rotation_z(degrees: float) -> Matrix4:
    angle = radians(degrees)
    c, s = cos(angle), sin(angle)
    return [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def transform_point(point: Point3, matrix: Matrix4) -> Point3:
    x, y, z = point
    vector = (x, y, z, 1.0)
    result = [sum(matrix[row][column] * vector[column] for column in range(4))
              for row in range(4)]
    w = result[3]
    if abs(w) < 1e-12:
        raise ValueError("La coordenada homogénea w no puede ser cero")
    return result[0] / w, result[1] / w, result[2] / w

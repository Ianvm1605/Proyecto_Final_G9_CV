"""Matrices homogéneas didácticas para las transformaciones 2D y 3D."""

from __future__ import annotations

from math import cos, radians, sin


def identity3() -> list[list[float]]:
    return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def multiply3(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [[sum(left[row][k] * right[k][col] for k in range(3)) for col in range(3)] for row in range(3)]


def transform2(point: tuple[float, float], matrix: list[list[float]]) -> tuple[float, float]:
    x, y = point
    rx = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2]
    ry = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2]
    rw = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2]
    return rx / rw, ry / rw


def translate2(tx: float, ty: float) -> list[list[float]]:
    return [[1, 0, tx], [0, 1, ty], [0, 0, 1]]


def scale2(sx: float, sy: float) -> list[list[float]]:
    return [[sx, 0, 0], [0, sy, 0], [0, 0, 1]]


def rotate2(degrees: float) -> list[list[float]]:
    angle = radians(degrees)
    return [[cos(angle), -sin(angle), 0], [sin(angle), cos(angle), 0], [0, 0, 1]]


def shear2(x_factor: float, y_factor: float) -> list[list[float]]:
    return [[1, x_factor, 0], [y_factor, 1, 0], [0, 0, 1]]

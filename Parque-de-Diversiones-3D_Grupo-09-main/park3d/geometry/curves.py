"""Curvas Bézier, B-spline y fractal de Koch."""

from __future__ import annotations

from math import comb
from typing import Sequence
Point2 = tuple[float, float]


def bezier_point(control_points: Sequence[Point2], t: float) -> Point2:
    """Evalúa una curva Bézier de cualquier grado (semanas 9-10)."""
    degree = len(control_points) - 1
    if degree < 1:
        raise ValueError("Una curva Bézier necesita al menos dos puntos")
    x = sum(comb(degree, i) * (1 - t) ** (degree - i) * t**i * p[0] for i, p in enumerate(control_points))
    y = sum(comb(degree, i) * (1 - t) ** (degree - i) * t**i * p[1] for i, p in enumerate(control_points))
    return x, y


def sample_bezier(control_points: Sequence[Point2], samples: int = 48) -> list[Point2]:
    return [bezier_point(control_points, step / samples) for step in range(samples + 1)]


def bspline_point(control_points: Sequence[Point2], t: float, closed: bool = True) -> Point2:
    """B-spline cúbica uniforme. ``t`` pertenece a [0, 1]."""
    if len(control_points) < 4:
        raise ValueError("Una B-spline cúbica necesita cuatro puntos o más")
    points = list(control_points)
    if closed:
        points += points[:3]
    segments = len(control_points) if closed else len(control_points) - 3
    parameter = t % 1.0 if closed else max(0.0, min(t, 1.0))
    scaled = parameter * segments
    segment = min(int(scaled), segments - 1)
    local = scaled - segment
    p0, p1, p2, p3 = points[segment : segment + 4]
    b0 = (-local**3 + 3 * local**2 - 3 * local + 1) / 6
    b1 = (3 * local**3 - 6 * local**2 + 4) / 6
    b2 = (-3 * local**3 + 3 * local**2 + 3 * local + 1) / 6
    b3 = local**3 / 6
    return (
        b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0],
        b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1],
    )


def sample_bspline(control_points: Sequence[Point2], samples: int = 180, closed: bool = True) -> list[Point2]:
    return [bspline_point(control_points, step / samples, closed) for step in range(samples + 1)]


def koch_curve(start: Point2, end: Point2, depth: int) -> list[Point2]:
    """Curva fractal opcional para representar otro tipo de curva (semana 10)."""
    if depth <= 0:
        return [start, end]
    dx, dy = (end[0] - start[0]) / 3, (end[1] - start[1]) / 3
    one = (start[0] + dx, start[1] + dy)
    two = (start[0] + 2 * dx, start[1] + 2 * dy)
    peak = (one[0] + dx * 0.5 - dy * 0.8660254, one[1] + dy * 0.5 + dx * 0.8660254)
    segments = [koch_curve(a, b, depth - 1) for a, b in ((start, one), (one, peak), (peak, two), (two, end))]
    return [point for segment in segments[:-1] for point in segment[:-1]] + segments[-1]

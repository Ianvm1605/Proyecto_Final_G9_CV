"""Envolvente convexa por el algoritmo de Graham."""

from __future__ import annotations

from math import atan2
from typing import Iterable
Point2 = tuple[float, float]


def _cross(origin: Point2, a: Point2, b: Point2) -> float:
    return (a[0] - origin[0]) * (b[1] - origin[1]) - (a[1] - origin[1]) * (b[0] - origin[0])


def graham_scan(points: Iterable[Point2]) -> list[Point2]:
    """Calcula la envolvente convexa ordenando por ángulo polar desde el pivote."""
    unique = set(points)
    if len(unique) <= 1:
        return list(unique)
    pivot = min(unique, key=lambda point: (point[1], point[0]))

    def polar_key(point: Point2) -> tuple[float, float]:
        dx, dy = point[0] - pivot[0], point[1] - pivot[1]
        return atan2(dy, dx), dx * dx + dy * dy

    hull = [pivot]
    for point in sorted(unique - {pivot}, key=polar_key):
        while len(hull) >= 2 and _cross(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    return hull

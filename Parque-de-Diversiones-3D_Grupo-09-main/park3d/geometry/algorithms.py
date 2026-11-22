"""Algoritmos de Computación Visual implementados sin depender del rasterizador.

Cada función es deliberadamente pequeña y reutilizable: el modo Editor las
visualiza píxel a píxel y el modo Parque utiliza las curvas para la atracción.
"""

from __future__ import annotations

from math import atan2, comb, floor
from typing import Iterable, Sequence

Point2 = tuple[float, float]


def basic_line(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    """Rasteriza por evaluación directa de la ecuación en el eje dominante."""
    x, y = start
    dx, dy = end[0] - x, end[1] - y
    steps = max(abs(dx), abs(dy))
    if not steps:
        return [start]
    return [(round(x + dx * i / steps), round(y + dy * i / steps)) for i in range(steps + 1)]


def dda_line(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    """Rasteriza una línea sumando incrementos constantes en ambos ejes."""
    x, y = start
    dx, dy = end[0] - x, end[1] - y
    steps = max(abs(dx), abs(dy))
    if not steps:
        return [start]
    step_x, step_y = dx / steps, dy / steps
    pixels = []
    for _ in range(steps):
        pixels.append((round(x), round(y)))
        x, y = x + step_x, y + step_y
    return [*pixels, end]


def bresenham_line(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    """Devuelve los píxeles de una recta mediante Bresenham (semana 3)."""
    x0, y0 = start
    x1, y1 = end
    points: list[tuple[int, int]] = []
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    error = dx + dy
    while True:
        points.append((x0, y0))
        if (x0, y0) == (x1, y1):
            return points
        twice_error = 2 * error
        if twice_error >= dy:
            error += dy
            x0 += sx
        if twice_error <= dx:
            error += dx
            y0 += sy


def coverage_line(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int, float]]:
    """Estima cobertura repartiendo la intensidad entre los dos píxeles vecinos."""
    x0, y0 = start
    x1, y1 = end
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0, x1, y1 = y0, x0, y1, x1
    if x0 > x1:
        x0, y0, x1, y1 = x1, y1, x0, y0
    if x0 == x1:
        return [(*start, 1.0)]
    slope = (y1 - y0) / (x1 - x0)
    result = []
    for x in range(x0, x1 + 1):
        value = y0 + (x - x0) * slope
        y = floor(value)
        for neighbor, coverage in ((y, y + 1 - value), (y + 1, value - y)):
            if coverage > 0:
                result.append((neighbor, x, coverage) if steep else (x, neighbor, coverage))
    return result


def _circle_octants(center: tuple[int, int], x: int, y: int) -> set[tuple[int, int]]:
    cx, cy = center
    return {
        (cx + x, cy + y), (cx + y, cy + x), (cx - y, cy + x), (cx - x, cy + y),
        (cx - x, cy - y), (cx - y, cy - x), (cx + y, cy - x), (cx + x, cy - y),
    }


def bresenham_circle(center: tuple[int, int], radius: int) -> list[tuple[int, int]]:
    """Rasteriza una circunferencia con el error discriminante entero de Bresenham."""
    if radius < 0:
        raise ValueError("El radio no puede ser negativo")
    x, y, error = 0, radius, 3 - 2 * radius
    pixels: set[tuple[int, int]] = set()
    while x <= y:
        pixels.update(_circle_octants(center, x, y))
        if error < 0:
            error += 4 * x + 6
        else:
            error += 4 * (x - y) + 10
            y -= 1
        x += 1
    return sorted(pixels)


def midpoint_circle(center: tuple[int, int], radius: int) -> list[tuple[int, int]]:
    """Rasteriza una circunferencia evaluando el punto medio entre dos candidatos."""
    if radius < 0:
        raise ValueError("El radio no puede ser negativo")
    x, y, decision = 0, radius, 1.25 - radius
    pixels: set[tuple[int, int]] = set()
    while x <= y:
        pixels.update(_circle_octants(center, x, y))
        if decision < 0:
            decision += 2 * x + 3
        else:
            decision += 2 * (x - y) + 5
            y -= 1
        x += 1
    return sorted(pixels)


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


INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8


def _out_code(x: float, y: float, rect: tuple[float, float, float, float]) -> int:
    xmin, ymin, xmax, ymax = rect
    return (LEFT if x < xmin else RIGHT if x > xmax else 0) | (BOTTOM if y < ymin else TOP if y > ymax else 0)


def cohen_sutherland(
    start: Point2, end: Point2, rect: tuple[float, float, float, float]
) -> tuple[Point2, Point2] | None:
    """Recorta una línea contra una ventana rectangular (Unidad I)."""
    x0, y0, x1, y1 = *start, *end
    xmin, ymin, xmax, ymax = rect
    code0, code1 = _out_code(x0, y0, rect), _out_code(x1, y1, rect)
    while True:
        if not (code0 | code1):
            return (x0, y0), (x1, y1)
        if code0 & code1:
            return None
        outside = code0 or code1
        if outside & TOP:
            x, y = x0 + (x1 - x0) * (ymax - y0) / (y1 - y0), ymax
        elif outside & BOTTOM:
            x, y = x0 + (x1 - x0) * (ymin - y0) / (y1 - y0), ymin
        elif outside & RIGHT:
            x, y = xmax, y0 + (y1 - y0) * (xmax - x0) / (x1 - x0)
        else:
            x, y = xmin, y0 + (y1 - y0) * (xmin - x0) / (x1 - x0)
        if outside == code0:
            x0, y0, code0 = x, y, _out_code(x, y, rect)
        else:
            x1, y1, code1 = x, y, _out_code(x, y, rect)


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

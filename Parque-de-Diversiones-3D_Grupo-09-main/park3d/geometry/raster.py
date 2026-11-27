"""Algoritmos de rasterización de líneas y circunferencias."""

from __future__ import annotations

from math import floor


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

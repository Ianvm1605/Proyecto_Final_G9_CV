"""Recorte de segmentos contra una ventana rectangular."""

from __future__ import annotations

Point2 = tuple[float, float]
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

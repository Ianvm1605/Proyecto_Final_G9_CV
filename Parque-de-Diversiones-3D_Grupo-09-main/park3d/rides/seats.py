"""Posiciones de asiento compartidas entre la cámara y las mallas móviles."""

from math import cos, radians, sin, tau

WHEEL_CENTER = (7.0, 3.65, -7.0)
WHEEL_RADIUS = 2.62
WHEEL_GONDOLAS = 12
CAROUSEL_CENTER = (-7.1, 0.0, 5.5)
CAROUSEL_HORSES = 8


def wheel_gondola_anchor(angle: float, index: int = 0) -> tuple[float, float, float]:
    """El punto de suspensión gira con el aro. La cabina permanece vertical."""
    theta = radians(angle) + index * tau / WHEEL_GONDOLAS
    x, y, z = WHEEL_CENTER
    return x + WHEEL_RADIUS * cos(theta), y + WHEEL_RADIUS * sin(theta), z + 0.32


def carousel_horse_frame(angle: float, index: int = 0) -> tuple[tuple[float, float, float], float]:
    """La base del caballo da vueltas y oscila sobre su eje vertical."""
    phase = index * tau / CAROUSEL_HORSES
    rotation = radians(angle) - phase
    x, y, z = CAROUSEL_CENTER
    anchor = (x + 1.4 * cos(rotation), y + 1.19 + 0.17 * sin(radians(angle * 3) + phase),
              z - 1.4 * sin(rotation))
    return anchor, rotation

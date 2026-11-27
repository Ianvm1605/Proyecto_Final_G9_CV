"""Conversiones de color didácticas entre RGB y HSV."""

from __future__ import annotations

from colorsys import hsv_to_rgb as _hsv_to_rgb, rgb_to_hsv as _rgb_to_hsv

RGB = tuple[float, float, float]
HSV = tuple[float, float, float]


def rgb_to_hsv(rgb: RGB) -> HSV:
    """Convierte canales RGB normalizados [0, 1] a H en [0, 360), S y V [0, 1]."""
    if any(channel < 0 or channel > 1 for channel in rgb):
        raise ValueError("Los canales RGB deben estar entre 0 y 1")
    hue, saturation, value = _rgb_to_hsv(*rgb)
    return (hue * 360.0) % 360.0, saturation, value


def hsv_to_rgb(hsv: HSV) -> RGB:
    """Convierte H en grados y S/V normalizados a canales RGB en [0, 1]."""
    hue, saturation, value = hsv
    if not 0 <= saturation <= 1 or not 0 <= value <= 1:
        raise ValueError("La saturación y el valor deben estar entre 0 y 1")
    return _hsv_to_rgb((hue % 360.0) / 360.0, saturation, value)

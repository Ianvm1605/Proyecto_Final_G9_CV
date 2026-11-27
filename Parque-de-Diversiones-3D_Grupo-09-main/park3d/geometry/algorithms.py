"""Fachada retrocompatible de los módulos de geometría didáctica."""

from __future__ import annotations

from .clipping import cohen_sutherland
from .curves import bezier_point, koch_curve, sample_bezier, sample_bspline, bspline_point
from .hull import graham_scan
from .raster import basic_line, bresenham_circle, bresenham_line, coverage_line, dda_line, midpoint_circle

Point2 = tuple[float, float]

__all__ = ['basic_line', 'dda_line', 'bresenham_line', 'coverage_line', 'bresenham_circle', 'midpoint_circle', 'graham_scan', 'cohen_sutherland', 'bezier_point', 'sample_bezier', 'bspline_point', 'sample_bspline', 'koch_curve']

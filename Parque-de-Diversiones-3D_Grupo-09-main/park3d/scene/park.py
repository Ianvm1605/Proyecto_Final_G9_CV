"""Estado independiente del renderizado para el parque de diversiones."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass, field
from itertools import accumulate
from math import atan2, dist, hypot, pi, sin, tau

from park3d.geometry.algorithms import graham_scan, sample_bspline

Point3 = tuple[float, float, float]

DEFAULT_RIDE_SPEED = 0.034
TRACK_EDIT_LIMIT = 18.5
MIN_CONTROL_HEIGHT, MAX_CONTROL_HEIGHT = 1.30, 8.30
STATION_PARAMETER = 0.95
# Coordenadas X, Z y altura de cada punto de control de la B-spline periódica.
DEFAULT_TRACK = (
    (-12.7, -1.5, 1.65), (-13.3, -5.4, 1.84), (-13.8, -10.5, 4.80),
    (-10.5, -15.2, 8.00), (-5.7, -16.1, 7.60), (-0.3, -14.6, 2.05),
    (3.6, -12.4, 2.30), (7.1, -13.1, 5.90), (12.0, -15.3, 6.20),
    (16.1, -13.4, 4.40), (17.6, -9.1, 3.20), (17.0, -4.7, 5.00),
    (13.5, -1.9, 4.10), (9.4, -0.4, 2.65), (6.2, 2.0, 1.70),
    (5.85, 4.85, 2.65), (6.5, 7.65, 5.40), (6.3, 10.5, 6.25),
    (3.15, 11.0, 5.55), (-0.2, 9.0, 4.40), (-4.1, 9.6, 2.25),
    (-7.0, 9.4, 2.10), (-10.7, 8.7, 4.00), (-11.2, 5.0, 4.70),
    (-11.5, 1.6, 1.72),
)


@dataclass
class ParkModel:
    """Reúne el plano, la B-spline y el estado animado de las atracciones."""

    control_points: list[tuple[float, float]] = field(
        default_factory=lambda: [(x, z) for x, z, _ in DEFAULT_TRACK]
    )
    user_points: list[tuple[float, float]] = field(
        default_factory=lambda: [(-17, -12), (-17, 10), (-8, 13), (9, 13), (19, 8), (19, -16), (-5, -18)]
    )
    ride_progress: float = 0.95
    ride_speed: float = DEFAULT_RIDE_SPEED
    wheel_angle: float = 0.0
    carousel_angle: float = 0.0
    paused: bool = False
    fountain_phase: float = 0.0
    elapsed: float = 0.0
    track_heights: list[float] | None = None

    def __post_init__(self) -> None:
        if self.track_heights is None:
            course = [(x, z) for x, z, _ in DEFAULT_TRACK]
            self.track_heights = [y for _, _, y in DEFAULT_TRACK] if self.control_points == course else [2.50] * len(self.control_points)
        elif len(self.track_heights) != len(self.control_points):
            raise ValueError("Cada punto de control debe tener una altura.")
        self.rebuild_track()

    def rebuild_track(self) -> None:
        samples = max(240, len(self.control_points) * 20)
        self.track_2d = sample_bspline(self.control_points, samples=samples, closed=True)
        height_spline = sample_bspline([(height, 0.0) for height in self.track_heights], samples=samples, closed=True)
        self.track_3d = [(x, y, z) for (x, z), (y, _) in zip(self.track_2d, height_spline)]
        self.track_distances = list(accumulate(
            (dist(a, b) for a, b in zip(self.track_3d, self.track_3d[1:])), initial=0.0
        ))
        self.track_length = self.track_distances[-1]
        self.station_progress = self.track_distances[round(STATION_PARAMETER * samples)] / max(1e-9, self.track_length)

    @property
    def hull(self) -> list[tuple[float, float]]:
        return graham_scan(self.user_points)

    def tick(self, seconds: float) -> None:
        if self.paused:
            return
        self.ride_progress = (self.ride_progress + self.ride_rate * seconds) % 1.0
        self.wheel_angle = (self.wheel_angle + 10 * seconds) % 360
        self.carousel_angle = (self.carousel_angle + 24 * seconds) % 360
        self.fountain_phase = (self.fountain_phase + 1.5 * seconds) % 1.0
        self.elapsed += seconds

    def track_position(self, progress: float) -> Point3:
        """Interpola por longitud de arco para recorrer distancias comparables."""
        if self.track_length < 1e-9:
            return self.track_3d[0]
        distance = (progress % 1.0) * self.track_length
        end = bisect_right(self.track_distances, distance, hi=len(self.track_distances) - 1)
        start = end - 1
        step = self.track_distances[end] - self.track_distances[start]
        fraction = (distance - self.track_distances[start]) / step if step > 0 else 0.0
        x0, y0, z0 = self.track_3d[start]
        x1, y1, z1 = self.track_3d[end]
        return x0 + fraction * (x1 - x0), y0 + fraction * (y1 - y0), z0 + fraction * (z1 - z0)

    def track_direction(self, progress: float) -> tuple[float, float]:
        span = min(0.015, 0.43 / max(1e-9, self.track_length))
        ahead = self.track_position(progress + span)
        behind = self.track_position(progress - span)
        dx, dy, dz = (a - b for a, b in zip(ahead, behind))
        return atan2(dx, dz), atan2(dy, hypot(dx, dz))

    def track_bank(self, progress: float | None = None) -> float:
        """Inclina el riel hacia el interior según la variación local de rumbo."""
        if progress is None:
            progress = self.ride_progress
        span = min(0.02, 0.76 / max(1e-9, self.track_length))
        before, _ = self.track_direction(progress - span)
        after, _ = self.track_direction(progress + span)
        turn = (after - before + pi) % tau - pi
        return max(-0.28, min(0.28, -0.80 * turn))

    @property
    def ride_rate(self) -> float:
        """Ritmo positivo con desaceleración en el andén y cambios en pendientes."""
        _, pitch = self.track_direction(self.ride_progress)
        gap = abs((self.ride_progress - self.station_progress + 0.5) % 1.0 - 0.5)
        station_factor = 0.68 + 0.32 * min(1.0, gap / 0.046)
        return self.ride_speed * station_factor * (1.0 - 0.53 * sin(pitch))

    def coaster_pose(self, progress: float | None = None) -> tuple[Point3, float, float]:
        if progress is None:
            progress = self.ride_progress
        x, y, z = self.track_position(progress)
        yaw, pitch = self.track_direction(progress)
        return (x, y + 0.20, z), yaw, pitch

    def wagon_pose(self) -> tuple[Point3, float]:
        point, yaw, _ = self.coaster_pose()
        return point, yaw

    def add_editor_point(self, point: tuple[float, float]) -> None:
        if len(self.user_points) >= 20:
            self.user_points.pop(0)
        self.user_points.append(point)

    def move_control_point(self, index: int, point: tuple[float, float]) -> None:
        x, z = point
        self.control_points[index] = (max(-TRACK_EDIT_LIMIT, min(TRACK_EDIT_LIMIT, x)),
                                      max(-TRACK_EDIT_LIMIT, min(TRACK_EDIT_LIMIT, z)))
        self.rebuild_track()

    def move_control_height(self, index: int, height: float) -> None:
        self.track_heights[index] = max(MIN_CONTROL_HEIGHT, min(MAX_CONTROL_HEIGHT, height))
        self.rebuild_track()

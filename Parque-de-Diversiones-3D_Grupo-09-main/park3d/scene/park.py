"""Estado independiente del renderizado para el parque de diversiones."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass, field
from itertools import accumulate
from math import atan2, cos, dist, hypot, sin, tau

from park3d.geometry.algorithms import graham_scan, sample_bspline

Point3 = tuple[float, float, float]


@dataclass
class ParkModel:
    """Reúne el plano, la B-spline y el estado animado de las atracciones."""

    control_points: list[tuple[float, float]] = field(
        default_factory=lambda: [(-7.0, -1.0), (-5.5, 5.5), (-0.5, 7.2), (5.8, 5.6), (7.2, 0.0), (4.0, -5.5), (-3.5, -6.4)]
    )
    user_points: list[tuple[float, float]] = field(
        default_factory=lambda: [(-7, -7), (-8, 4), (-3, 8), (4, 8), (8, 3), (7, -7), (0, -8)]
    )
    ride_progress: float = 0.0
    ride_speed: float = 0.045
    wheel_angle: float = 0.0
    carousel_angle: float = 0.0
    paused: bool = False
    fountain_phase: float = 0.0
    elapsed: float = 0.0

    def __post_init__(self) -> None:
        self.rebuild_track()

    def rebuild_track(self) -> None:
        self.track_2d = sample_bspline(self.control_points, samples=240, closed=True)
        self.track_2d[-1] = self.track_2d[0]
        segments = len(self.track_2d) - 1
        self.track_3d = [self._elevated(point, index / segments) for index, point in enumerate(self.track_2d[:-1])]
        self.track_3d.append(self.track_3d[0])
        self.track_distances = list(accumulate((dist(a, b) for a, b in zip(self.track_3d, self.track_3d[1:])), initial=0.0))
        self.track_length = self.track_distances[-1]

    @staticmethod
    def _elevated(point: tuple[float, float], t: float) -> Point3:
        x, z = point
        # Sucesión de lomas y valles con derivadas periódicas también en la junta.
        height = 2.5 + 0.86 * cos(2 * tau * (t - 0.10)) + 0.58 * sin(tau * (t - 0.265)) + 0.26 * sin(3 * tau * (t + 0.08))
        return x, height, z

    @property
    def hull(self) -> list[tuple[float, float]]:
        return graham_scan(self.user_points)

    def tick(self, seconds: float) -> None:
        if self.paused:
            return
        self.ride_progress = (self.ride_progress + self.ride_speed * seconds) % 1.0
        self.wheel_angle = (self.wheel_angle + 10 * seconds) % 360
        self.carousel_angle = (self.carousel_angle + 24 * seconds) % 360
        self.fountain_phase = (self.fountain_phase + 1.5 * seconds) % 1.0
        self.elapsed += seconds

    def track_position(self, progress: float) -> Point3:
        """Interpola por longitud de arco para mantener la marcha uniforme."""
        distance = (progress % 1.0) * self.track_length
        end = bisect_right(self.track_distances, distance, hi=len(self.track_distances) - 1)
        start = end - 1
        step = self.track_distances[end] - self.track_distances[start]
        fraction = (distance - self.track_distances[start]) / step if step > 0 else 0.0
        x0, y0, z0 = self.track_3d[start]
        x1, y1, z1 = self.track_3d[end]
        return x0 + fraction * (x1 - x0), y0 + fraction * (y1 - y0), z0 + fraction * (z1 - z0)

    def track_direction(self, progress: float) -> tuple[float, float]:
        ahead = self.track_position(progress + 0.003)
        behind = self.track_position(progress - 0.003)
        dx, dy, dz = (a - b for a, b in zip(ahead, behind))
        return atan2(dx, dz), atan2(dy, hypot(dx, dz))

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
        self.control_points[index] = (max(-9.0, min(9.0, point[0])), max(-9.0, min(9.0, point[1])))
        self.rebuild_track()

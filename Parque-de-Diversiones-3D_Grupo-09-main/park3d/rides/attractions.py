"""Construcción y dibujo de las atracciones sobre el contexto OpenGL activo."""

from __future__ import annotations

from math import atan2, cos, degrees, hypot, radians, sin, tau
from typing import TYPE_CHECKING, Callable

from OpenGL.GL import (
    GL_COMPILE,
    GL_EMISSION,
    GL_FRONT_AND_BACK,
    GL_QUADS,
    GL_TRIANGLES,
    glBegin,
    glCallList,
    glColor3f,
    glDeleteLists,
    glEnd,
    glEndList,
    glGenLists,
    glMaterialfv,
    glNewList,
    glNormal3f,
    glPopMatrix,
    glPushMatrix,
    glRotatef,
    glScalef,
    glTranslatef,
    glVertex3f,
)
from OpenGL.GLU import gluSphere

if TYPE_CHECKING:
    from park3d.scene.park import ParkModel, Point3


STEEL = (0.35, 0.42, 0.44)
IVORY = (0.91, 0.83, 0.65)
GOLD = (0.76, 0.47, 0.16)
TERRACOTTA = (0.65, 0.21, 0.115)
SUPPORT = (0.235, 0.30, 0.31)
RIM = (0.62, 0.77, 0.72)
CANOPY = (0.36, 0.10, 0.095)
RUBBER = (0.095, 0.107, 0.104)
GLASS = (0.24, 0.43, 0.46)
GONDOLA_COLORS = (
    (0.55, 0.17, 0.15),
    (0.19, 0.42, 0.40),
    (0.69, 0.43, 0.14),
    (0.33, 0.35, 0.55),
)
WHEEL_CENTER = (7.0, 3.65, -7.0)
WHEEL_RADIUS = 2.62
CAROUSEL_CENTER = (-7.1, 0.0, 5.5)


class AttractionsMixin:
    """Mallas reutilizables y animaciones de la montaña rusa, rueda y carrusel."""

    def _ride_list(self, name: str, draw: Callable[[], None]) -> None:
        # Cada instancia del renderizador pertenece a un único contexto OpenGL.
        if not hasattr(self, "_ride_lists"):
            self._ride_lists: dict[str, int] = {}
        if name not in self._ride_lists:
            handle = glGenLists(1)
            if not handle:
                draw()
                return
            glNewList(handle, GL_COMPILE)
            try:
                draw()
            finally:
                glEndList()
            self._ride_lists[name] = handle
        glCallList(self._ride_lists[name])

    def _ride_sphere(self, x, y, z, scale, color, slices=12) -> None:
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(*scale)
        glColor3f(*color)
        gluSphere(self.quadric, 1, slices, 8)
        glPopMatrix()

    @staticmethod
    def _closed_ride_pipe(centers, radius, color, sides=8, plane=None) -> None:
        """Extruye una sección circular alrededor de una trayectoria cerrada."""
        rings = []
        count = len(centers)
        circle = [(cos(tau * j / sides), sin(tau * j / sides)) for j in range(sides)]
        for i, (x, y, z) in enumerate(centers):
            prev, after = centers[i - 1], centers[(i + 1) % count]
            dx, dy, dz = (a - b for a, b in zip(after, prev))
            length = hypot(dx, dy, dz)
            if length < 1e-9:
                tangent = (0.0, 0.0, 1.0)
            else:
                tangent = dx / length, dy / length, dz / length
            if plane == "xy":
                side = (0.0, 0.0, 1.0)
            else:
                horizontal = hypot(dx, dz)
                side = (dz / horizontal, 0.0, -dx / horizontal) if horizontal > 1e-9 else (1.0, 0.0, 0.0)
            tx, ty, tz = tangent
            sx, sy, sz = side
            up = (ty * sz - tz * sy, tz * sx - tx * sz, tx * sy - ty * sx)
            ring = []
            for a, b in circle:
                normal = tuple(a * s + b * u for s, u in zip(side, up))
                ring.append((normal, (x + radius * normal[0], y + radius * normal[1], z + radius * normal[2])))
            rings.append(ring)

        glColor3f(*color)
        glBegin(GL_QUADS)
        for i, ring in enumerate(rings):
            next_ring = rings[(i + 1) % count]
            for j in range(sides):
                k = (j + 1) % sides
                for normal, vertex in (ring[j], ring[k], next_ring[k], next_ring[j]):
                    glNormal3f(*normal)
                    glVertex3f(*vertex)
        glEnd()

    def _track_structure(self, park: ParkModel) -> None:
        track = park.track_3d[:-1]
        rails: list[list[Point3]] = [[], []]
        spine = []
        for i, (x, y, z) in enumerate(track):
            previous, following = track[i - 1], track[(i + 1) % len(track)]
            dx, dz = following[0] - previous[0], following[2] - previous[2]
            heading = atan2(dx, dz)
            for side, points in zip((-0.34, 0.34), rails):
                points.append((x + cos(heading) * side, y, z - sin(heading) * side))
            spine.append((x, y - 0.26, z))
        for rail in rails:
            self._closed_ride_pipe(rail, 0.062, TERRACOTTA)
        self._closed_ride_pipe(spine, 0.103, (0.42, 0.15, 0.105))

        ties = max(1, round(park.track_length / 0.42))
        for i in range(ties):
            progress = i / ties
            x, y, z = park.track_position(progress)
            heading, pitch = park.track_direction(progress)
            glPushMatrix()
            glTranslatef(x, y, z)
            glRotatef(degrees(heading), 0, 1, 0)
            glRotatef(-degrees(pitch), 1, 0, 0)
            self.box(0, -0.09, 0, 0.43, 0.038, 0.048, STEEL)
            self.tube((-0.31, -0.10, 0), (0, -0.255, 0), 0.034, TERRACOTTA, 5)
            self.tube((0.31, -0.10, 0), (0, -0.255, 0), 0.034, TERRACOTTA, 5)
            glPopMatrix()

        frames = max(1, round(park.track_length / 2.4))
        for i in range(frames):
            progress = (i + 0.27) / frames
            x, y, z = park.track_position(progress)
            heading, _ = park.track_direction(progress)
            glPushMatrix()
            glTranslatef(x, 0, z)
            glRotatef(degrees(heading), 0, 1, 0)
            top = y - 0.36
            base = 0.52 + 0.061 * top
            self.box(0, top, 0, 0.49, 0.065, 0.11, SUPPORT)
            for side in (-1, 1):
                self.box(side * base, 0.055, 0, 0.16, 0.055, 0.17, (0.55, 0.54, 0.48))
                self.tube((side * base, 0.13, 0), (side * 0.35, top, 0), 0.083, SUPPORT, 6)
                self.tube((side * base, 0.26, 0), (-side * 0.40, top * 0.73, 0), 0.032, STEEL, 5)
            glPopMatrix()

        self._coaster_platform(park)

    def _coaster_platform(self, park: ParkModel) -> None:
        """Andén y escalera del tramo bajo, al lado externo de los rieles."""
        x, y, z = park.track_position(0.875)
        heading, _ = park.track_direction(0.875)
        deck = y + 0.07
        timber = (0.37, 0.24, 0.15)
        oak = (0.62, 0.43, 0.253)
        glPushMatrix()
        glTranslatef(x, 0, z)
        glRotatef(degrees(heading), 0, 1, 0)
        self.box(-1.09, deck - 0.07, 0, 0.55, 0.07, 1.23, timber)
        for i in range(13):
            self.box(-1.09, deck - 0.004, -1.15 + i * 0.191, 0.548, 0.013, 0.091, oak)
        self.box(-0.559, deck + 0.006, 0, 0.026, 0.024, 1.19, GOLD)
        for rz in (-1.12, 0, 1.12):
            for rx in (-1.58, -0.63):
                self.box(rx, deck * 0.47, rz, 0.054, deck * 0.47, 0.065, timber)
                self.box(rx, 0.045, rz, 0.11, 0.045, 0.104, STEEL)
        for rz in (-1.2, -0.4, 0.4, 1.2):
            self.box(-1.59, deck + 0.37, rz, 0.041, 0.37, 0.049, timber)
        for level in (deck + 0.40, deck + 0.72):
            self.box(-1.59, level, 0, 0.032, 0.033, 1.21, oak)
        steps = max(1, round(deck / 0.15))
        for i in range(steps):
            tread = deck * (steps - i - 0.5) / steps
            self.box(-1.09, tread * 0.5, -1.26 - i * 0.21, 0.43, tread * 0.5, 0.11, oak)
        for side in (-1.52, -0.66):
            tip = -1.25 - (steps - 1) * 0.21
            self.tube((side, deck + 0.63, -1.20), (side, 0.73, tip), 0.034, timber, 6)
            self.box(side, 0.37, tip, 0.025, 0.37, 0.026, timber)
        for sz in (-1.10, 1.10):
            for sx in (-1.6, -0.67):
                self.box(sx, deck + 0.86, sz, 0.049, 0.86, 0.051, timber)
        for side in (-1, 1):
            glPushMatrix()
            glTranslatef(-1.135 + side * 0.35, deck + 1.76, 0)
            glRotatef(-side * 16, 0, 0, 1)
            self.box(0, 0, 0, 0.39, 0.045, 1.30, CANOPY)
            glPopMatrix()
        self.box(-1.135, deck + 1.86, 0, 0.038, 0.035, 1.32, GOLD)
        glPopMatrix()

    def _coaster_car(self, lead: bool) -> None:
        body = TERRACOTTA if lead else (0.17, 0.36, 0.37)
        self.box(0, 0.012, 0, 0.40, 0.085, 0.47, RUBBER)
        self.box(0, 0.12, 0, 0.40, 0.066, 0.49, body)
        self.box(0, 0.225, 0.40, 0.40, 0.115, 0.10, body)
        self.box(0, 0.31, 0.41, 0.35, 0.042, 0.12, GOLD)
        self.box(0, 0.20, -0.42, 0.39, 0.08, 0.069, body)
        self.box(0, 0.065, -0.54, 0.078, 0.037, 0.09, STEEL)
        for x in (-0.397, 0.397):
            self.box(x, 0.21, -0.04, 0.037, 0.09, 0.37, body)
            self.box(x * 1.075, 0.20, -0.035, 0.011, 0.022, 0.27, GOLD)
            for z in (-0.295, 0.295):
                self.tube((x - 0.055, -0.12, z), (x + 0.055, -0.12, z), 0.088, RUBBER, 10)
                self._ride_sphere(x, -0.12, z, (0.067, 0.040, 0.041), STEEL)
        for x in (-0.18, 0.18):
            self.box(x, 0.215, -0.11, 0.125, 0.036, 0.17, RUBBER)
            self.box(x, 0.335, -0.27, 0.129, 0.137, 0.052, RUBBER)
            self.box(x, 0.481, -0.27, 0.091, 0.047, 0.062, IVORY)
            self.tube((x - 0.10, 0.31, 0.15), (x + 0.10, 0.31, 0.15), 0.023, STEEL, 6)
        if lead:
            self.box(0, 0.165, 0.499, 0.32, 0.028, 0.017, GOLD)
            for x in (-0.25, 0.25):
                self._ride_sphere(x, 0.23, 0.51, (0.069, 0.047, 0.025), IVORY)

    def draw_coaster(self, park: ParkModel) -> None:
        if getattr(self, "_coaster_track", None) is not park.track_3d:
            display_lists = getattr(self, "_ride_lists", {})
            old = display_lists.pop("coaster_track", None)
            if old:
                glDeleteLists(old, 1)
            self._coaster_track = park.track_3d
        self._ride_list("coaster_track", lambda: self._track_structure(park))

        for i in range(3):
            progress = park.ride_progress - i * 1.12 / park.track_length
            point, heading, pitch = park.coaster_pose(progress)
            glPushMatrix()
            glTranslatef(*point)
            glRotatef(degrees(heading), 0, 1, 0)
            glRotatef(-degrees(pitch), 1, 0, 0)
            self._ride_list("lead_car" if i == 0 else "trailer", lambda: self._coaster_car(i == 0))
            glPopMatrix()

    def _wheel_foundation(self) -> None:
        self.box(0, 0.10, 0, 2.82, 0.10, 1.53, (0.46, 0.45, 0.39))
        self.box(0, 0.21, 0, 2.76, 0.025, 1.46, (0.61, 0.56, 0.43))
        self.box(0.64, 0.32, 1.07, 1.12, 0.093, 0.46, SUPPORT)
        self.box(0.64, 0.14, 1.58, 1.12, 0.07, 0.13, (0.62, 0.57, 0.48))
        self.box(0.64, 0.07, 1.77, 1.12, 0.065, 0.12, (0.62, 0.57, 0.48))
        for z in (-0.96, 0.96):
            for x in (-1.82, 1.82):
                self.box(x, 0.28, z, 0.23, 0.06, 0.23, STEEL)
                self.tube((x, 0.34, z), (0, 3.65, z * 0.57), 0.124, SUPPORT, 8)
                self.tube((x, 0.50, z), (x * 0.40, 2.56, -z * 0.61), 0.041, STEEL, 6)
            self.tube((-1.39, 1.14, z * 0.84), (1.39, 1.14, z * 0.84), 0.052, SUPPORT, 7)
        self.tube((0, 3.65, -0.66), (0, 3.65, 0.66), 0.15, STEEL, 14)

    def _wheel_rotor(self) -> None:
        for z in (-0.24, 0.24):
            ring = [(WHEEL_RADIUS * cos(i * tau / 72), WHEEL_RADIUS * sin(i * tau / 72), z) for i in range(72)]
            self._closed_ride_pipe(ring, 0.078, RIM, plane="xy")
            self._ride_sphere(0, 0, z * 1.32, (0.30, 0.30, 0.12), GOLD)
        for i in range(12):
            theta = i * tau / 12
            x, y = WHEEL_RADIUS * cos(theta), WHEEL_RADIUS * sin(theta)
            for z in (-0.24, 0.24):
                self.tube((0, 0, z), (x, y, z), 0.036, STEEL, 6)
            self.tube((x, y, -0.24), (x, y, 0.42), 0.042, GOLD, 7)
            for j in range(3):
                a = theta + (j + 0.5) * tau / 36
                u, v = WHEEL_RADIUS * cos(a), WHEEL_RADIUS * sin(a)
                self._ride_sphere(u, v, 0.285, (0.045, 0.045, 0.040), IVORY, 8)

    def _wheel_lights(self) -> None:
        for i in range(36):
            angle = (i + 0.5) * tau / 36
            x, y = WHEEL_RADIUS * cos(angle), WHEEL_RADIUS * sin(angle)
            self._ride_sphere(x, y, 0.308, (0.044, 0.044, 0.036), IVORY, 8)

    def _wheel_gondola(self, paint) -> None:
        self.tube((0, -0.043, 0), (0, -0.27, 0), 0.034, STEEL, 7)
        self._ride_sphere(0, -0.27, 0, (0.275, 0.085, 0.23), IVORY)
        self.box(0, -0.430, 0, 0.239, 0.145, 0.186, paint)
        self.box(0, -0.566, 0, 0.254, 0.043, 0.197, STEEL)
        for side in (-1, 1):
            self.box(0, -0.404, side * 0.189, 0.191, 0.075, 0.012, GLASS)
            self.box(side * 0.242, -0.404, 0, 0.012, 0.075, 0.118, GLASS)
            self.box(0, -0.404, side * 0.203, 0.013, 0.078, 0.008, IVORY)
            self.box(0, -0.511, side * 0.192, 0.190, 0.011, 0.008, GOLD)

    def draw_wheel(self, park: ParkModel) -> None:
        cx, cy, cz = WHEEL_CENTER
        glPushMatrix()
        glTranslatef(cx, 0, cz)
        self._ride_list("wheel_foundation", self._wheel_foundation)
        glTranslatef(0, cy, 0)
        glPushMatrix()
        glRotatef(park.wheel_angle, 0, 0, 1)
        self._ride_list("wheel_rotor", self._wheel_rotor)
        if not self.day_mode:
            glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.77, 0.47, 0.19, 1.0))
            self._ride_list("wheel_lights", self._wheel_lights)
            glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.0, 0.0, 0.0, 1.0))
        glPopMatrix()
        for i in range(12):
            theta = radians(park.wheel_angle) + i * tau / 12
            index = i % len(GONDOLA_COLORS)
            glPushMatrix()
            glTranslatef(WHEEL_RADIUS * cos(theta), WHEEL_RADIUS * sin(theta), 0.32)
            self._ride_list(f"gondola_{index}", lambda: self._wheel_gondola(GONDOLA_COLORS[index]))
            glPopMatrix()
        glPopMatrix()

    def _carousel_ground(self) -> None:
        self.cylinder(0, 0.01, 0, 2.29, 0.16, (0.51, 0.45, 0.36), 48)
        # Una corona externa de pilotes marca el límite de la plataforma.
        for i in range(12):
            if i in (2, 3, 4):
                continue
            a = i * tau / 12
            x, z = 2.20 * cos(a), 2.20 * sin(a)
            self.cylinder(x, 0.13, z, 0.029, 0.63, GOLD, 8)
            self._ride_sphere(x, 0.76, z, (0.052, 0.05, 0.052), GOLD, 8)
        self.box(0, 0.07, 2.26, 0.49, 0.07, 0.16, (0.62, 0.55, 0.41))

    def _carousel_turntable(self) -> None:
        self.cylinder(0, 0.174, 0, 2.07, 0.20, CANOPY, 48)
        self.cylinder(0, 0.38, 0, 0.16, 2.65, GOLD, 16)
        for i in range(12):
            a, b = i * tau / 12, (i + 1) * tau / 12
            glColor3f(*(IVORY if i % 2 else (0.66, 0.47, 0.285)))
            glBegin(GL_TRIANGLES)
            glNormal3f(0, 1, 0)
            glVertex3f(0, 0.375, 0)
            glVertex3f(2.07 * cos(b), 0.375, 2.07 * sin(b))
            glVertex3f(2.07 * cos(a), 0.375, 2.07 * sin(a))
            glEnd()
        for i in range(12):
            self._carousel_canopy_panel(i)
            a = (i + 0.5) * tau / 12
            x, z = 2.12 * cos(a), 2.12 * sin(a)
            self._ride_sphere(x, 2.68, z, (0.074, 0.075, 0.074), GOLD, 8)
        self._ride_sphere(0, 3.43, 0, (0.17, 0.16, 0.17), GOLD)
        self.cylinder(0, 3.42, 0, 0.043, 0.34, GOLD, 10)
        self._ride_sphere(0, 3.78, 0, (0.065, 0.076, 0.065), GOLD)
        for i in range(8):
            a = i * tau / 8
            self.cylinder(1.40 * cos(a), 0.38, 1.40 * sin(a), 0.028, 2.41, GOLD, 8)

    def _carousel_canopy_panel(self, index: int) -> None:
        colors = (CANOPY, IVORY)
        profile = ((0.02, 3.47), (0.58, 3.33), (1.23, 3.04), (1.77, 2.86), (2.16, 2.80), (2.17, 2.66))
        for lo, hi in zip(profile, profile[1:]):
            r0, y0 = lo
            r1, y1 = hi
            length = hypot(y1 - y0, r1 - r0)
            nx, ny = (y0 - y1) / length, (r1 - r0) / length
            glColor3f(*colors[index % 2])
            glBegin(GL_QUADS)
            for j in range(5):
                a = (index + j / 5) * tau / 12
                b = (index + (j + 1) / 5) * tau / 12
                for radius, y, angle in ((r0, y0, a), (r0, y0, b), (r1, y1, b), (r1, y1, a)):
                    glNormal3f(nx * cos(angle), ny, nx * sin(angle))
                    glVertex3f(radius * cos(angle), y, radius * sin(angle))
            glEnd()

    def _carousel_horse(self, coat, saddle) -> None:
        self._ride_sphere(0, 0, 0, (0.166, 0.17, 0.36), coat)
        self._ride_sphere(0, 0.119, 0.20, (0.123, 0.22, 0.143), coat)
        self._ride_sphere(0, 0.282, 0.294, (0.125, 0.132, 0.195), coat)
        self._ride_sphere(0, 0.235, 0.423, (0.106, 0.081, 0.115), (0.68, 0.51, 0.38))
        self._ride_sphere(0, 0.185, -0.048, (0.179, 0.071, 0.164), saddle)
        self._ride_sphere(0, 0.16, 0.105, (0.102, 0.18, 0.092), RUBBER)
        self.tube((0, 0.018, -0.29), (0, -0.211, -0.42), 0.068, RUBBER, 8)
        for side in (-1, 1):
            x = side * 0.090
            self._ride_sphere(side * 0.056, 0.394, 0.229, (0.033, 0.074, 0.039), coat, 8)
            self._ride_sphere(side * 0.111, 0.303, 0.319, (0.018, 0.017, 0.016), RUBBER, 8)
            front_knee = (x, -0.233, 0.29 if side > 0 else 0.39)
            front_hoof = (x, -0.384 if side > 0 else -0.33, 0.28 if side > 0 else 0.45)
            hind_knee = (x, -0.239, -0.30)
            hind_hoof = (x, -0.386 if side < 0 else -0.34, -0.41 if side < 0 else -0.28)
            for knee, hoof, z in ((front_knee, front_hoof, 0.22), (hind_knee, hind_hoof, -0.24)):
                self.tube((x, -0.059, z), knee, 0.055, coat, 8)
                self.tube(knee, hoof, 0.041, coat, 8)
                self._ride_sphere(*hoof, (0.058, 0.045, 0.061), RUBBER, 8)

    def draw_carousel(self, park: ParkModel) -> None:
        glPushMatrix()
        glTranslatef(*CAROUSEL_CENTER)
        self._ride_list("carousel_ground", self._carousel_ground)
        glRotatef(park.carousel_angle, 0, 1, 0)
        self._ride_list("carousel_turntable", self._carousel_turntable)
        if not self.day_mode:
            glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.88, 0.57, 0.26, 1.0))
            self._ride_list("carousel_lights", self._carousel_lights)
            glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.0, 0.0, 0.0, 1.0))
        for i in range(8):
            a = i * tau / 8
            glPushMatrix()
            glTranslatef(1.40 * cos(a), 1.19 + 0.17 * sin(radians(park.carousel_angle * 3) + a), 1.40 * sin(a))
            glRotatef(-degrees(a), 0, 1, 0)
            self._ride_list(
                f"horse_{i % 2}",
                lambda: self._carousel_horse(IVORY if i % 2 else (0.76, 0.54, 0.38), CANOPY if i % 2 else GONDOLA_COLORS[1]),
            )
            glPopMatrix()
        glPopMatrix()

    def _carousel_lights(self) -> None:
        for i in range(24):
            angle = (i + 0.5) * tau / 24
            x, z = 2.142 * cos(angle), 2.142 * sin(angle)
            self._ride_sphere(x, 2.655, z, (0.041, 0.037, 0.041), IVORY, 8)

"""Terrain, ground materials and architecture for the 3D park.

Coordinates use Y as height. The developed park sits at Y=0 so the editor
and the rides retain a common plan, with terrain rolling off beyond the fence.
"""

from __future__ import annotations

from math import atan2, cos, degrees, hypot, pi, sin
from random import Random

from OpenGL.GL import (
    GL_AMBIENT_AND_DIFFUSE, GL_COLOR_MATERIAL, GL_EMISSION, GL_FRONT_AND_BACK,
    GL_LIGHTING, GL_LIGHTING_BIT, GL_LINEAR, GL_LINEAR_MIPMAP_LINEAR, GL_QUADS, GL_REPEAT,
    GL_RGB, GL_SHININESS, GL_SPECULAR, GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T, GL_TRIANGLES, GL_TRIANGLE_FAN, GL_UNSIGNED_BYTE,
    glBegin, glBindTexture, glColor3f, glColor4f, glColorMaterial, glDepthMask, glDisable, glEnable, glEnd,
    glGenTextures, glMaterialf, glMaterialfv, glNormal3f, glPopAttrib, glPopMatrix,
    glPushAttrib, glPushMatrix, glRotatef, glScalef,
    glTexCoord2f, glTexParameteri, glTranslatef, glVertex3f,
)
from OpenGL.GLU import gluBuild2DMipmaps, gluSphere

from park3d.geometry.algorithms import bezier_point, sample_bezier

GRASS = (0.49, 0.60, 0.35)
PATH = (0.86, 0.78, 0.67)
IVORY = (0.82, 0.74, 0.59)
IRON = (0.16, 0.24, 0.24)
WOOD = (0.55, 0.35, 0.22)
COPPER = (0.80, 0.52, 0.25)
LETTERING = (0.97, 0.89, 0.70, 1)
LAGOON = (13.6, 4.25, 3.45, 2.82)
OVERLOOK = (14.6, 8.9)
KIOSKS = (
    (-9.8, -2.0, (0.61, 0.33, 0.27), "BOCADOS"),
    (10.4, 7.7, (0.36, 0.51, 0.45), "RECUERDOS"),
    (-8.7, -8.4, (0.49, 0.56, 0.60), "CAFÉ DEL PARQUE"),
)
WALKERS = (
    ((-0.68, 4.5), (-0.68, 11.7), (0.63, 0.34, 0.20), (0.62, 0.39, 0.26)),
    ((0.56, 12.9), (0.56, 3.0), (0.31, 0.43, 0.63), (0.76, 0.53, 0.38)),
    ((-3.14, 0.4), (-2.54, 2.89), (0.72, 0.57, 0.28), (0.86, 0.67, 0.49)),
    ((2.86, -2.80), (5.53, -6.15), (0.45, 0.30, 0.43), (0.53, 0.32, 0.21)),
    ((-3.94, 4.03), (-5.44, 5.52), (0.40, 0.60, 0.53), (0.81, 0.57, 0.39)),
    ((5.62, 5.51), (8.84, 8.12), (0.76, 0.72, 0.59), (0.72, 0.51, 0.36)),
    ((11.12, 9.12), (15.54, 10.72), (0.49, 0.53, 0.35), (0.79, 0.52, 0.35)),
    ((-8.36, 2.87), (-10.31, 2.37), (0.49, 0.26, 0.29), (0.72, 0.49, 0.38)),
)


class LandscapeMixin:
    """Static scene geometry, drawn with the renderer's current environment."""

    def prepare_landscape(self) -> None:
        """Upload tiled material bitmaps before compiling a display list."""
        self.landscape_materials = {
            name: self._land_texture(name)
            for name in ("grass", "stone", "brick")
        }
        for label in ("PARQUE VISUAL", "MIRADOR", *(kiosk[3] for kiosk in KIOSKS)):
            self._text_texture(label, 30, LETTERING)

    @staticmethod
    def _land_texture(material: str) -> int:
        size = 256 if material == "grass" else 128
        rng = Random(2017)
        grass_cells = [[rng.uniform(-11, 11) for _ in range(16)] for _ in range(16)] if material == "grass" else []
        pixels = bytearray()
        for v in range(size):
            for u in range(size):
                grain = rng.randrange(-20, 21)
                if material == "grass":
                    col, du = divmod(u, 16)
                    row, dv = divmod(v, 16)
                    a, b = du / 16, dv / 16
                    first, second = grass_cells[row], grass_cells[(row + 1) % 16]
                    mottling = ((1 - b) * (first[col] * (1 - a) + first[(col + 1) % 16] * a)
                                + b * (second[col] * (1 - a) + second[(col + 1) % 16] * a))
                    tone = mottling + grain * 0.77
                    rgb = (131 + tone, 151 + tone, 102 + tone)
                else:
                    brick = material == "brick"
                    width, height = (32, 16) if brick else (64, 32)
                    col, x = divmod(u + (v // height % 2) * width // 2, width)
                    row, y = divmod(v, height)
                    tone = (col * 23 + row * 19) % 22
                    if x < 2 or y < 2:
                        base = (159, 145, 129) if brick else (132, 124, 111)
                    elif x <= 3 or y <= 3:
                        base = (185, 146, 113) if brick else (214, 202, 183)
                    else:
                        base = (143 + tone, 104 + tone, 84 + tone) if brick else (179 + tone, 165 + tone, 145 + tone)
                    rgb = tuple(channel + grain * 0.42 for channel in base)
                pixels.extend(max(0, min(255, round(channel))) for channel in rgb)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, size, size, GL_RGB, GL_UNSIGNED_BYTE, bytes(pixels))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        return texture

    def _ground_material(self, material: str, color: tuple[float, float, float]) -> None:
        if self.show_texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.landscape_materials[material])
        glColor3f(*color)

    @staticmethod
    def _terrain_height(x: float, z: float) -> float:
        margin = max(abs(x) - 21, -z - 19, z - 15)
        wind = max(0, min(1.0, margin / 13))
        rolling = 0.7 + 1.25 * sin(x * 0.18 + z * 0.08) + 0.9 * cos(z * 0.20 + x * 0.05)
        return -0.025 + wind * wind * rolling

    def _terrain(self) -> None:
        # All cell indices share vertices, so UVs stay continuous across edges.
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0, 0, 0, 1))
        self._ground_material("grass", (0.82, 0.87, 0.69))
        coordinates = range(-68, 68, 2)
        glBegin(GL_QUADS)
        for z in coordinates:
            for x in coordinates:
                for px, pz in ((x, z), (x, z + 2), (x + 2, z + 2), (x + 2, z)):
                    h = self._terrain_height(px, pz)
                    glNormal3f(h - self._terrain_height(px + 0.5, pz), 0.5, h - self._terrain_height(px, pz + 0.5))
                    tint = 0.93 + 0.08 * sin(px * 0.52 + 2 * cos(pz * 0.28)) * cos(pz * 0.35)
                    tint += 0.03 * cos((px - pz) * 0.81)
                    base = (0.82, 0.87, 0.69) if self.show_texture else GRASS
                    glColor3f(*(tint * component for component in base))
                    glTexCoord2f((px + 0.24 * pz) / 4.6, (pz - 0.24 * px) / 4.6)
                    glVertex3f(px, h, pz)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    @staticmethod
    def _ribbon(points, width: float, y: float) -> None:
        offsets = []
        for index, (x, z) in enumerate(points):
            ax, az = points[max(0, index - 1)]
            bx, bz = points[min(len(points) - 1, index + 1)]
            factor = width / (2 * hypot(bx - ax, bz - az))
            offsets.append(((x + (bz - az) * factor, z - (bx - ax) * factor),
                            (x - (bz - az) * factor, z + (bx - ax) * factor)))
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        for (right, left), (right_next, left_next) in zip(offsets, offsets[1:]):
            for x, z in (left, left_next, right_next, right):
                glTexCoord2f(x * 0.63, z * 0.63)
                glVertex3f(x, y, z)
        glEnd()

    @staticmethod
    def _disk(x: float, y: float, z: float, rx: float, rz: float, color, slices: int = 36) -> None:
        glColor3f(*color)
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 1, 0)
        glTexCoord2f(x * 0.63, z * 0.63)
        glVertex3f(x, y, z)
        for index in range(slices + 1):
            angle = -2 * pi * index / slices
            px, pz = x + rx * cos(angle), z + rz * sin(angle)
            glTexCoord2f(px * 0.63, pz * 0.63)
            glVertex3f(px, y, pz)
        glEnd()

    def _paths(self) -> None:
        branches = (
            (3.2, [(0, 15), (0, 9), (0, 6), (0, 1)]),
            (2.1, [(0, 0), (-2.0, 1.5), (-3.0, 5.8), (-6.0, 5.6)]),
            (2.3, [(1.0, -1), (2.8, -2.0), (1.5, -6.8), (6.9, -7.5)]),
            (1.9, [(2.4, 1.0), (6.0, 1.4), (6.5, 7.8), (10.5, 8.8)]),
            (1.55, [(-3, -1), (-5, -3), (-7, -2.1), (-10.5, -2)]),
            (1.4, [(-2.2, 0.43), (-5.2, 2.15), (-8.9, 3.45), (-10.36, 2.14)]),
            (1.6, [(-1.5, -2.2), (-3.6, -4.9), (-5.5, -6.4), (-8.8, -8.4)]),
            (1.60, [(10.4, 8.8), (12.8, 9.80), (14.1, 11.2), (16.35, 10.4)]),
            (1.45, [(16.35, 10.4), (18.35, 9.4), (18.4, 6.5), (18.55, 3.1)]),
            (1.26, [(-8.8, -8.4), (-8.7, -11.1), (-6.9, -11.2), (-3.7, -11.25)]),
            (1.22, [(-3.7, -11.25), (-0.1, -11.2), (1.95, -9.6), (5.26, -8.02)]),
        )
        ribbons = [(width, sample_bezier(points, 25)) for width, points in branches]
        for width, points in ribbons:
            glColor3f(0.46, 0.42, 0.32)
            self._ribbon(points, width + 0.24, 0.012)
        self._disk(0, 0.013, -0.2, 4.18, 3.75, (0.43, 0.37, 0.29))
        self._disk(-3.6, 0.013, -11.18, 2.00, 1.19, (0.43, 0.37, 0.29))
        self._disk(18.55, 0.013, 3.1, 1.28, 1.24, (0.43, 0.37, 0.29))
        for width, points in ribbons:
            self._ground_material("stone", PATH)
            self._ribbon(points, width, 0.021)
        self._disk(0, 0.025, -0.2, 4.05, 3.62, PATH)
        self._disk(-3.6, 0.025, -11.18, 1.88, 1.08, PATH)
        self._disk(18.55, 0.025, 3.1, 1.17, 1.11, PATH)
        glDisable(GL_TEXTURE_2D)

    def _contact_shadows(self) -> None:
        footprints = (
            (0, -0.63, 1.95, 1.78), (0, 8.95, 2.80, 1.67),
            (-2.33, 13.04, 0.76, 0.72), (2.33, 13.04, 0.76, 0.72),
            (-7.1, 5.5, 2.78, 2.78), (7.0, -7.0, 2.6, 1.4),
            (-4.1, 1.6, 1.24, 0.84), (3.8, -3.3, 1.20, 0.92),
            (3.3, 7.0, 1.30, 0.90), (8.8, -3.4, 1.22, 0.97),
            (*OVERLOOK, 2.5, 1.8), (16.9, 11.4, 1.20, 1.10),
            *((x, z, 1.9, 1.55) for x, z, _, _ in KIOSKS),
        )
        glDisable(GL_LIGHTING)
        glDepthMask(False)
        for x, z, rx, rz in footprints:
            glBegin(GL_TRIANGLE_FAN)
            alpha = 0.29 if self.day_mode else 0.37
            glColor4f(0.09, 0.12, 0.08, alpha)
            glVertex3f(x + 0.12, 0.030, z - 0.10)
            glColor4f(0.09, 0.12, 0.08, 0.0)
            for step in range(25):
                theta = -step * 2 * pi / 24
                glVertex3f(x + 0.23 + rx * cos(theta), 0.030, z - 0.19 + rz * sin(theta))
            glEnd()
        glDepthMask(True)
        glEnable(GL_LIGHTING)

    def _sphere(self, x, y, z, sx, sy, sz, color, detail=9) -> None:
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(sx, sy, sz)
        gluSphere(self.quadric, 1, detail, detail - 2)
        glPopMatrix()

    def _orchard_tree(self, x: float, z: float, scale: float, seed: int) -> None:
        y = self._terrain_height(x, z)
        self.cylinder(x, y, z, 0.092 * scale, 1.47 * scale, (0.36, 0.25, 0.16), 7)
        rng = Random(seed)
        palette = ((0.20, 0.34, 0.15), (0.26, 0.40, 0.17), (0.32, 0.45, 0.20), (0.40, 0.49, 0.24))
        if seed % 6 == 2:
            palette = ((0.44, 0.23, 0.18), (0.52, 0.28, 0.20), (0.59, 0.37, 0.21), (0.67, 0.44, 0.27))
        for index in range(8):
            theta = index * (2 * pi / 7) + rng.random() * 0.45
            spread = 0.40 if index < 7 else 0.0
            cx, cz = x + scale * spread * cos(theta), z + scale * spread * sin(theta)
            cy = y + scale * (1.58 + rng.random() * 0.48 if index < 7 else 2.35)
            radius = scale * (0.44 + rng.random() * 0.14)
            if index in (0, 2, 4):
                self.tube((x, y + 0.86 * scale, z), (cx, cy - 0.23 * scale, cz), 0.039 * scale, WOOD, 6)
            self._sphere(cx, cy, cz, radius, radius * 1.08, radius, palette[index % 4])

    def _planting(self) -> None:
        trees = (
            (-10.75, -7.42, 1.42), (-15.7, -4.0, 1.36), (-15.65, 3.7, 1.10), (-14.2, 6.3, 1.13),
            (-11, 10.4, 1.42), (-8.0, 12.1, 1.09), (-5.3, 12.64, 0.96),
            (5.0, 13.05, 0.90), (9.8, 10.8, 1.0), (16.9, 11.4, 1.08), (19.15, 6.2, 0.98),
            (12.8, -6.5, 1.35), (12.5, -9.8, 1.42), (9.1, -10.9, 1.28), (3.5, -10.6, 0.95),
            (-1.8, -12.20, 1.18), (-6.1, -12.43, 1.34), (-9.3, -11.2, 1.32),
            (-4.1, 1.6, 0.74), (3.8, -3.3, 0.78), (3.3, 7.0, 0.84), (8.8, -3.4, 0.83),
            (-16.7, -8.1, 1.30), (-16.2, -11.8, 1.15), (-13.4, -15.9, 1.44), (-7.4, -17.5, 1.10),
            (2.0, -17.0, 1.26), (7.4, -16.9, 0.96), (11.1, -17.35, 1.22),
            (15.25, -16.65, 1.27), (18.45, -13.6, 0.97), (19.25, -7.7, 0.97),
            (18.7, -2.4, 1.27), (18.1, 0.52, 0.92), (11.3, 0.9, 0.83),
        )
        for index, (x, z, scale) in enumerate(trees):
            self._orchard_tree(x, z, scale, index + 20)
        rng = Random(190)
        for index in range(47):
            angle = index * 2 * pi / 47
            radius = rng.uniform(24, 42)
            x, z = radius * cos(angle), radius * sin(angle)
            if x > -8 and z > 13:
                continue
            self._orchard_tree(x, z, rng.uniform(0.9, 1.7), index + 120)
        for index, (x, z, size) in enumerate((
            (-4, 11.95, 1.5), (4, 12.05, 1.5), (-3.5, 5.0, 1.3), (2.7, 4.3, 1.4),
            (9, 7.7, 1.25), (8.7, 6.3, 1.0), (-4, -3.0, 1.1), (2.0, -8.5, 1.3),
            (-9, -5.5, 1.6), (5.7, -10.6, 1.7), (10.0, 3.0, 1.0),
            (-4.0, -10.3, 1.26), (-3.8, -12.25, 1.45), (17.8, 8.8, 1.31),
            (17.0, 10.0, 1.15), (19.35, 3.6, 1.14), (17.55, 0.4, 1.4),
        )):
            self._disk(x, 0.031, z, size * 0.63, size * 0.31, (0.42, 0.34, 0.25), 18)
            self._disk(x, 0.039, z, size * 0.56, size * 0.25, (0.23, 0.19, 0.12), 18)
            for side in (-1, 1):
                self._sphere(x + side * size * 0.24, 0.15, z, 0.34, 0.29, 0.27, (0.25, 0.39, 0.18), 8)
            for bloom in range(11):
                bx, bz = x + rng.uniform(-0.46, 0.46) * size, z + rng.uniform(-0.18, 0.18) * size
                petal = ((0.94, 0.69, 0.32), (0.88, 0.44, 0.37), (0.72, 0.64, 0.85))[(index + bloom) % 3]
                self._sphere(bx, rng.uniform(0.10, 0.25), bz, 0.067, 0.066, 0.067, petal, 7)

    def _fences(self) -> None:
        perimeter = ((-2.5, 12.9), (-5.0, 13.9), (-15.6, 13.9), (-18.0, 11.6), (-18.0, -15.3),
                     (-15.5, -18.4), (16.4, -18.4), (20.0, -15.0), (20.0, 11.6), (17.6, 13.9),
                     (5.5, 13.9), (2.5, 12.9))
        for (x, z), (tx, tz) in zip(perimeter, perimeter[1:]):
            count = max(1, round(hypot(tx - x, tz - z) / 1.45))
            for y in (0.40, 0.69):
                self.tube((x, y, z), (tx, y, tz), 0.022, IRON, 5)
            for index in range(count + 1):
                t = index / count
                px, pz = x * (1 - t) + tx * t, z * (1 - t) + tz * t
                self.box(px, 0.4, pz, 0.065, 0.39, 0.065, IRON)
                self.box(px, 0.81, pz, 0.085, 0.032, 0.085, COPPER)
                for i in range(1, 5) if index < count else ():
                    self.cylinder(px + (tx - x) * i / (5 * count), 0.36,
                                  pz + (tz - z) * i / (5 * count), 0.014, 0.36, IRON, 5)

    def _bench(self, x: float, z: float, angle: float) -> None:
        glPushMatrix()
        glTranslatef(x, 0, z)
        glRotatef(angle, 0, 1, 0)
        for leg in (-0.44, 0.44):
            for depth in (-0.20, 0.18):
                self.box(leg, 0.17, depth, 0.033, 0.17, 0.031, IRON)
            self.box(leg, 0.53, -0.20, 0.027, 0.22, 0.027, IRON)
            self.box(leg, 0.47, 0.0, 0.032, 0.026, 0.24, IRON)
        for depth in (-0.17, -0.07, 0.03, 0.13):
            self.box(0, 0.35, depth, 0.60, 0.026, 0.044, WOOD)
        for height in (0.56, 0.66):
            self.box(0, height, -0.20, 0.60, 0.042, 0.022, WOOD)
        glPopMatrix()

    def _lamppost(self, x: float, z: float) -> None:
        self.cylinder(x, 0.025, z, 0.16, 0.13, IVORY, 9)
        self.cylinder(x, 0.11, z, 0.070, 1.95, IRON, 8)
        self.cylinder(x, 0.11, z, 0.115, 0.31, IRON, 8)
        self._sphere(x, 2.09, z, 0.15, 0.045, 0.15, COPPER, 9)
        if not self.day_mode:
            glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.48, 0.29, 0.09, 1))
        self._sphere(x, 2.22, z, 0.115, 0.16, 0.115, (0.93, 0.72, 0.40), 9)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0, 0, 0, 1))
        self._sphere(x, 2.36, z, 0.14, 0.067, 0.14, IRON, 9)

    def _lagoon(self, x: float, z: float, rx: float, rz: float) -> None:
        """Piedra, grava y agua en anillos de un contorno irregular compartido."""
        count = 48
        shore = []
        for index in range(count):
            theta = -2 * pi * index / count
            irregular = 1 + 0.061 * sin(3 * theta + 0.8) + 0.073 * cos(5 * theta - 0.7)
            shore.append((irregular * rx * cos(theta), irregular * rz * sin(theta)))

        def ring_vertex(point, scale, height):
            px, pz = point
            glTexCoord2f(px * 0.7, pz * 0.7)
            glVertex3f(x + px * scale, height, z + pz * scale)

        self._ground_material("stone", (0.78, 0.72, 0.60))
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 1, 0)
        ring_vertex((0, 0), 1, 0.004)
        for point in (*shore, shore[0]):
            ring_vertex(point, 1.09, 0.004)
        glEnd()
        glDisable(GL_TEXTURE_2D)

        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 1, 0)
        glColor3f(0.19, 0.37, 0.40)
        ring_vertex((0, 0), 1, 0.020)
        for index, point in enumerate((*shore, shore[0])):
            light = 0.5 + 0.5 * cos(2 * pi * index / count)
            glColor3f(0.30 + 0.11 * light, 0.47 + 0.10 * light, 0.47 + 0.075 * light)
            ring_vertex(point, 1, 0.020)
        glEnd()

        rng = Random(327)
        for index, (dx, dz) in enumerate(shore):
            if index not in range(8, 14) and rng.random() < 0.60:
                scale = rng.uniform(0.10, 0.29)
                gray = rng.uniform(0.32, 0.50)
                self._sphere(x + dx, scale * 0.22, z + dz, scale * 1.65, scale * 0.62,
                             scale, (gray, gray * 1.03, gray * 0.92), 7)
            if index % 7 in (0, 1) and index not in range(8, 14):
                for blade in range(5):
                    px, pz = x + dx + rng.uniform(-0.20, 0.20), z + dz + rng.uniform(-0.16, 0.16)
                    height = rng.uniform(0.22, 0.43)
                    self.tube((px, 0.025, pz), (px + 0.065, height, pz - 0.03), 0.018,
                              (0.40 + blade * 0.023, 0.47, 0.23), 5)

    def _overlook(self, x: float, z: float) -> None:
        """Mirador de madera con bancos y un tejado de cuatro aguas."""
        glPushMatrix()
        glTranslatef(x, 0, z)
        self.box(0, 0.12, 0, 1.92, 0.12, 1.39, (0.40, 0.29, 0.22))
        for index in range(16):
            shade = 0.55 + 0.019 * (index * 3 % 5)
            self.box(0, 0.248, -1.29 + index * 0.171, 1.90, 0.022, 0.080,
                     (shade, 0.66 * shade, 0.42 * shade))
        self.box(0, 0.114, 1.51, 0.82, 0.086, 0.17, WOOD)
        for dx in (-1.52, 1.52):
            glPushMatrix()
            glTranslatef(0, 0.27, 0)
            self._bench(dx * 0.55, -0.80, 0)
            glPopMatrix()
            for dz in (-1.06, 1.06):
                self.box(dx, 1.27, dz, 0.073, 1.03, 0.076, WOOD)
                self.box(dx, 0.295, dz, 0.105, 0.095, 0.108, IRON)
                self.tube((dx, 1.89, dz), (dx * 0.71, 2.22, dz), 0.045, WOOD, 5)
            for height in (0.66, 0.98):
                self.box(dx, height, 0, 0.034, 0.034, 1.06, IRON)
        for height in (0.66, 0.98):
            self.box(0, height, -1.06, 1.52, 0.034, 0.034, IRON)
        self.box(0, 2.29, 0, 1.69, 0.095, 1.23, IRON)
        roof = ((-1.99, 2.38, 1.39), (1.99, 2.38, 1.39),
                (1.99, 2.38, -1.39), (-1.99, 2.38, -1.39))
        glBegin(GL_TRIANGLES)
        for index, point in enumerate(roof):
            nx, nz = ((0, 0.39), (0.3, 0), (0, -0.39), (-0.3, 0))[index]
            factor = 0.96 - 0.08 * (index % 2)
            glColor3f(0.30 * factor, 0.38 * factor, 0.34 * factor)
            glNormal3f(nx, 0.91, nz)
            glVertex3f(*point)
            glVertex3f(*roof[(index + 1) % 4])
            glVertex3f(0, 2.99, 0)
        glEnd()
        for point in roof:
            self.tube(point, (0, 3.00, 0), 0.026, (0.45, 0.47, 0.37), 5)
        self._sphere(0, 3.05, 0, 0.059, 0.11, 0.059, COPPER, 8)
        self.box(0, 2.21, 1.26, 0.91, 0.12, 0.030, IRON)
        self.world_label("MIRADOR", 0, 2.205, 1.298, 1.26, LETTERING)
        glPopMatrix()

    def _fountain(self) -> None:
        x, z = 0.0, -0.63
        self.cylinder(x, 0.02, z, 1.42, 0.18, (0.45, 0.43, 0.39), 36)
        self.cylinder(x, 0.19, z, 1.50, 0.10, IVORY, 36)
        self._disk(x, 0.295, z, 1.46, 1.46, IVORY)
        self._disk(x, 0.30, z, 1.33, 1.33, (0.31, 0.53, 0.52))
        self.cylinder(x, 0.27, z, 0.26, 0.68, (0.64, 0.58, 0.44), 18)
        self._sphere(x, 0.5, z, 0.29, 0.16, 0.29, IVORY)
        self._sphere(x, 0.97, z, 0.55, 0.12, 0.55, IVORY, 16)
        self._disk(x, 1.049, z, 0.44, 0.44, (0.43, 0.64, 0.64), 26)
        self.cylinder(x, 1.04, z, 0.065, 0.22, COPPER, 10)

    def draw_water(self, phase: float) -> None:
        """Gotas de la fuente y reflejos que se desplazan en la laguna."""
        glBegin(GL_TRIANGLES)
        glNormal3f(0, 1, 0)
        for direction in range(10):
            angle = direction * 2 * pi / 10
            ax, az = cos(angle), sin(angle)
            for step in range(11):
                t = (phase + step / 11 + direction * 0.121) % 1
                radius = 0.14 + t * 1.05
                y = 1.12 + t * (1.35 - 2.13 * t)
                x, z = radius * ax, -0.63 + radius * az
                glColor3f(0.76, 0.87, 0.86)
                glVertex3f(x + az * 0.014, y, z - ax * 0.014)
                glVertex3f(x - az * 0.014, y, z + ax * 0.014)
                glVertex3f(x + 0.045 * ax, y + 0.065 * (1 - 2 * t), z + 0.045 * az)
        glEnd()

        x, z, rx, rz = LAGOON
        glDisable(GL_LIGHTING)
        glBegin(GL_QUADS)
        for index in range(25):
            angle = index * 2.4
            radius = 0.74 * ((index + 1) / 25) ** 0.5
            px, pz = x + rx * radius * cos(angle), z + rz * radius * sin(angle)
            swell = 0.5 + 0.5 * sin(phase * 2 * pi + index * 0.83)
            span = 0.10 + 0.20 * swell
            opacity = (0.11 if self.day_mode else 0.048) * swell
            glColor4f(0.74, 0.87, 0.86, opacity)
            glVertex3f(px - span, 0.027, pz - 0.013)
            glVertex3f(px - span * 0.83, 0.027, pz + 0.026)
            glVertex3f(px + span, 0.027, pz + 0.015)
            glVertex3f(px + span * 0.94, 0.027, pz - 0.004)
        glEnd()
        glEnable(GL_LIGHTING)

    def draw_visitors(self, seconds: float) -> None:
        """Figuras pequeñas con pasos alternos que recorren los senderos."""
        pants = (0.24, 0.28, 0.29)
        for index, ((ax, az), (bx, bz), coat, skin) in enumerate(WALKERS):
            distance = hypot(bx - ax, bz - az)
            phase = (seconds * 0.61 / distance + index * 0.251 + 0.15) % 2
            t = 1 - abs(1 - phase)
            heading = degrees(atan2(bx - ax, bz - az)) + (180 if phase > 1 else 0)
            glPushMatrix()
            glTranslatef(ax + (bx - ax) * t, 0.03, az + (bz - az) * t)
            glRotatef(heading, 0, 1, 0)
            scale = 0.85 + 0.1 * sin(index + 1)
            glScalef(scale, scale, scale)
            self._sphere(0, 0.92, 0, 0.158, 0.27, 0.103, coat, 8)
            self._sphere(0, 1.23, 0.014, 0.102, 0.12, 0.095, skin, 9)
            self._sphere(0, 1.30, -0.023, 0.104, 0.063, 0.102, (0.20, 0.15, 0.12), 8)
            stride = 0.145 * sin(seconds * 9.0 + index * 2.1)
            for side in (-1, 1):
                foot = side * stride
                lift = max(0.0, foot) * 0.33
                self.tube((side * 0.071, 0.76, 0), (side * 0.080, 0.39, foot * 0.66), 0.056, pants, 6)
                self.tube((side * 0.080, 0.41, foot * 0.66), (side * 0.081, 0.09 + lift, foot), 0.046, pants, 6)
                self.box(side * 0.081, 0.064 + lift, foot + 0.028, 0.046, 0.036, 0.088, pants)
                self.tube((side * 0.125, 1.06, 0), (side * 0.201, 0.75, -foot), 0.036, coat, 6)
                self._sphere(side * 0.201, 0.725, -foot, 0.033, 0.047, 0.032, skin, 6)
            glPopMatrix()

    def _kiosk(self, x: float, z: float, color: tuple[float, float, float], label: str) -> None:
        self.box(x, 0.11, z, 1.31, 0.11, 0.98, IVORY)
        self.box(x, 0.94, z - 0.35, 1.15, 0.82, 0.59, color)
        self.box(x, 0.52, z + 0.48, 1.16, 0.43, 0.23, color)
        self.box(x, 0.99, z + 0.57, 1.26, 0.064, 0.24, WOOD)
        self.box(x, 1.29, z + 0.28, 1.02, 0.24, 0.028, (0.25, 0.32, 0.31))
        self.box(x, 1.46, z + 0.35, 1.18, 0.039, 0.044, IVORY)
        for dx in (-1.1, 0, 1.1):
            self.box(x + dx, 1.42, z + 0.54, 0.048, 0.44, 0.047, IVORY)
        for dx in (-0.79, -0.52, 0.58, 0.81):
            self._sphere(x + dx, 1.08, z + 0.47, 0.065, 0.15, 0.067, COPPER, 8)
        self.box(x, 1.89, z, 1.26, 0.09, 1.00, IVORY)
        self.box(x, 1.87, z + 1.006, 1.03, 0.12, 0.022, IRON)
        self.world_label(label, x, 1.87, z + 1.032, 1.53, LETTERING)
        self._awning(x, z, color)
        glColor3f(*color)
        glBegin(GL_TRIANGLES)
        glNormal3f(0, 0, 1)
        glVertex3f(x - 1.31, 1.98, z + 0.99); glVertex3f(x + 1.31, 1.98, z + 0.99); glVertex3f(x, 2.62, z + 0.99)
        glNormal3f(0, 0, -1)
        glVertex3f(x + 1.31, 1.98, z - 0.99); glVertex3f(x - 1.31, 1.98, z - 0.99); glVertex3f(x, 2.62, z - 0.99)
        glEnd()
        for side in (-1, 1):
            glPushMatrix()
            glTranslatef(x + 0.66 * side, 2.29, z)
            glRotatef(-26 * side, 0, 0, 1)
            self.box(0, 0, 0, 0.80, 0.06, 1.11, IRON)
            for depth in (-1.00, -0.67, -0.34, 0, 0.34, 0.67, 1.00):
                self.box(0, 0.06, depth, 0.79, 0.015, 0.012, (0.27, 0.36, 0.34))
            glPopMatrix()

    def _awning(self, x, z, color):
        # Una curva Bézier de perfil y dos filas intermedias componen la lona.
        # Las columnas tienen profundidades distintas para simular el festón.
        glDisable(GL_COLOR_MATERIAL)
        for stripe in range(8):
            left, right = x - 1.18 + 0.295 * stripe, x - 1.18 + 0.295 * (stripe + 1)
            cloth = color if stripe % 2 else (0.87, 0.76, 0.58)
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, (*cloth, 1))

            def point(u, v):
                fringe = 0.032 * sin(pi * u)
                depth, y = bezier_point(((1.029, 1.75), (1.26, 1.73),
                                         (1.48, 1.61), (1.63, 1.57 - fringe)), v)
                return left + u * (right - left), y, z + depth

            glBegin(GL_QUADS)
            for col in range(3):
                u0, u1 = col / 3, (col + 1) / 3
                glNormal3f(0, 0.96, 0.27)
                for row in range(4):
                    v0, v1 = row / 4, (row + 1) / 4
                    for u, v in ((u0, v0), (u0, v1), (u1, v1), (u1, v0)):
                        glVertex3f(*point(u, v))
                glNormal3f(0, 0, 1)
                for u, offset in ((u0, -0.09), (u1, -0.09), (u1, 0), (u0, 0)):
                    px, py, pz = point(u, 1)
                    glVertex3f(px, py + offset, pz)
            glEnd()
        glEnable(GL_COLOR_MATERIAL)

    def _gate(self) -> None:
        z = 13.04
        for x in (-2.33, 2.33):
            self.box(x, 0.13, z, 0.42, 0.13, 0.44, IVORY)
            self.box(x, 1.06, z, 0.28, 0.93, 0.30, (0.62, 0.49, 0.36))
            for y in (0.36, 0.71, 1.06, 1.41, 1.76):
                self.box(x, y, z, 0.295, 0.027, 0.312, IVORY)
            self.box(x, 2.02, z, 0.38, 0.10, 0.39, IVORY)
            self._sphere(x, 2.17, z, 0.17, 0.16, 0.17, COPPER)
        arch = [(2.33 * cos(i * pi / 14), 1.97 + 0.90 * sin(i * pi / 14), z) for i in range(15)]
        for start, end in zip(arch, arch[1:]):
            self.tube(start, end, 0.085, IRON, 8)
        self.box(0, 2.63, z, 1.24, 0.28, 0.093, (0.29, 0.44, 0.39))
        self.box(0, 2.89, z, 1.28, 0.044, 0.102, COPPER)
        self.box(0, 2.36, z, 1.28, 0.044, 0.102, COPPER)
        self.world_label("PARQUE VISUAL", 0, 2.61, z + 0.101, 2.18, LETTERING)

    def _pedestrian_arch(self) -> None:
        """Boundary of a masonry vault minus the space of a smaller vault."""
        z0, z1, outer, inner, base = 8.1, 9.75, 2.08, 1.72, 0.46
        self._ground_material("brick", (0.79, 0.72, 0.59))
        sectors = 22
        glBegin(GL_QUADS)
        for step in range(sectors):
            a, b = (step * pi / sectors, (step + 1) * pi / sectors)
            for radius, side in ((outer, 1), (inner, -1)):
                profile = ((a, z0), (b, z0), (b, z1), (a, z1))
                for theta, z in (profile if side == 1 else reversed(profile)):
                    glNormal3f(side * cos(theta), side * sin(theta), 0)
                    glTexCoord2f(z * 0.8, theta * radius * 0.65)
                    glVertex3f(radius * cos(theta), base + radius * sin(theta), z)
            for z, side in ((z0, -1), (z1, 1)):
                glNormal3f(0, 0, side)
                profile = ((outer, a), (outer, b), (inner, b), (inner, a))
                for radius, theta in (profile if side == 1 else reversed(profile)):
                    x, y = radius * cos(theta), base + radius * sin(theta)
                    glTexCoord2f(x * 0.76, y * 0.76)
                    glVertex3f(x, y, z)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        for z in (z0 - 0.06, z1 + 0.06):
            for index in range(13):
                a0, a1 = (index * pi / 13 + 0.012, (index + 1) * pi / 13 - 0.012)
                glColor3f(*(IVORY if index % 2 else (0.69, 0.60, 0.46)))
                glBegin(GL_QUADS)
                glNormal3f(0, 0, -1 if z < z0 else 1)
                profile = ((outer + 0.055, a0), (outer + 0.055, a1), (inner - 0.030, a1), (inner - 0.030, a0))
                for radius, a in (profile if z > z1 else reversed(profile)):
                    glVertex3f(radius * cos(a), base + radius * sin(a), z)
                glEnd()
        for side in (-1, 1):
            x = side * (outer + inner) / 2
            self.box(x, 0.23, (z0 + z1) / 2, 0.20, 0.23, (z1 - z0) / 2, (0.65, 0.52, 0.40))
            self.box(x, 0.055, (z0 + z1) / 2, 0.25, 0.055, (z1 - z0) / 2 + 0.12, IVORY)

    def draw_landscape(self) -> None:
        glPushAttrib(GL_LIGHTING_BIT)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.10, 0.10, 0.08, 1))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 18)
        self._terrain()
        self._paths()
        self._lagoon(*LAGOON)
        self._contact_shadows()
        self._fences()
        self._planting()
        self._fountain()
        self._pedestrian_arch()
        self._gate()
        self._overlook(*OVERLOOK)
        for x, z, color, label in KIOSKS:
            self._kiosk(x, z, color, label)
        for x, z, angle in ((-2.75, 2.25, 125), (2.65, -1.95, -55), (-2.70, -2.06, 42),
                            (3.95, 6.34, -30), (-8.76, -0.71, 0), (6.51, -5.12, 150),
                            (-4.56, -11.3, -60), (-2.61, -11.27, 60), (18.99, 2.62, -31),
                            (17.54, 7.05, -58)):
            self._bench(x, z, angle)
        for x, z in ((-2.12, 12.35), (2.12, 12.35), (-1.97, 6.48), (1.94, 5.21),
                     (-5.1, 3.58), (-3.54, -2.82), (2.84, -4.34), (7.91, -4.93),
                     (8.92, 7.08), (-8.9, -1.05), (-7.4, -7.93), (-8.2, 3.78),
                     (11.5, 9.05), (16.2, 11.1), (18.15, 5.8), (-5.65, -10.87)):
            self._lamppost(x, z)
        glPopAttrib()

"""Escena 3D, cámaras y primitivas compartidas en OpenGL."""

from __future__ import annotations

from math import acos, cos, degrees, dist, hypot, pi, sin, tau
from random import Random

import pygame
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLU import gluCylinder, gluDisk, gluLookAt, gluNewQuadric, gluPerspective

from park3d.rendering.interface import INK, PAPER, InterfaceMixin
from park3d.rendering.studio import EditorMixin
from park3d.rides.attractions import AttractionsMixin
from park3d.scenery.landscape import LandscapeMixin


CAMERA_HOME = {"yaw": 0.61, "pitch": 0.40, "distance": 32.5}
OVERVIEW_TARGET = (0.0, 1.50, 0.1)
RIDE_VIEWS = (
    ((0.0, 1.85, 0.0), 0.60, 0.44, 22.0),
    ((7.0, 3.9, -7.0), 0.82, 0.24, 16.5),
    ((-7.1, 1.8, 5.5), 0.45, 0.26, 12.5),
)
DAY_HAZE = (0.80, 0.85, 0.79)
NIGHT_HAZE = (0.16, 0.22, 0.35)


class Renderer(InterfaceMixin, EditorMixin, AttractionsMixin, LandscapeMixin):
    def __init__(self, size: tuple[int, int]) -> None:
        self.width, self.height = size
        self.fonts = {}
        self.textures = {}
        self._landscape_lists = {}
        self._sky_lists = {}
        self.day_mode = self.show_texture = self.antialias = self.perspective = True
        self.depth_test = self.smooth_shading = True
        self.wireframe = False
        self.selected_ride = None
        self.gl_version = (glGetString(GL_VERSION) or b"").decode(errors="replace").split(" ")[0]
        self.gl_device = (glGetString(GL_RENDERER) or b"").decode(errors="replace")[:44]
        self.quadric = gluNewQuadric()
        self.stencil_available = glGetIntegerv(GL_STENCIL_BITS) > 0
        glClearColor(*INK)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_NORMALIZE)
        self._cube = self._compile(self._unit_box)
        self.resize(size)
        self.prepare_landscape()

    def resize(self, size: tuple[int, int]) -> None:
        self.physical_size = size
        scale = min(1.0, size[0] / 980, size[1] / 650)
        self.width, self.height = (round(dimension / scale) for dimension in size)
        self.editor_bounds = self.editor_layout()
        glViewport(0, 0, *size)

    def logical_position(self, position):
        x, y = position
        width, height = self.physical_size
        return x * self.width / width, y * self.height / height

    @staticmethod
    def _compile(draw):
        model = glGenLists(1)
        glNewList(model, GL_COMPILE)
        try:
            draw()
        finally:
            glEndList()
        return model

    def _font(self, size: int):
        if size not in self.fonts:
            family = "georgia" if size >= 22 else "segoeui"
            self.fonts[size] = pygame.font.SysFont(family, size, bold=size >= 16)
        return self.fonts[size]

    def _text_texture(self, value, size, color):
        rgb = tuple(round(channel * 255) for channel in color[:3])
        key = (value, size, rgb)
        if key not in self.textures:
            surface = self._font(size).render(value, True, rgb)
            # Tanto el HUD como los letreros asignan V=0 al borde superior.
            data = pygame.image.tobytes(surface, "RGBA", False)
            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, *surface.get_size(), 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            self.textures[key] = (texture, *surface.get_size())
        return self.textures[key]

    def _overlay_begin(self):
        glDisable(GL_FOG)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

    def _overlay_end(self):
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

    def rect(self, x, y, w, h, color):
        glColor4f(*color)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

    def line2(self, points, color, width=1.0, closed=False):
        if not points:
            return
        if self.antialias:
            glEnable(GL_LINE_SMOOTH)
        glLineWidth(width)
        glColor4f(*color)
        glBegin(GL_LINE_LOOP if closed else GL_LINE_STRIP)
        for point in points:
            glVertex2f(*point)
        glEnd()
        glDisable(GL_LINE_SMOOTH)

    def text(self, value, x, y, size=15, color=PAPER):
        texture, width, height = self._text_texture(value, size, color)
        x, y = round(x), round(y)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor4f(1, 1, 1, color[3])
        glBegin(GL_QUADS)
        for u, v in ((0, 0), (1, 0), (1, 1), (0, 1)):
            glTexCoord2f(u, v)
            glVertex2f(x + u * width, y + v * height)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def world_label(self, value, x, y, z, width, color=(1, 1, 1, 1)):
        texture, pixels, lines = self._text_texture(value, 30, color)
        height = width * lines / pixels
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor4f(1, 1, 1, color[3])
        glBegin(GL_QUADS)
        for u, v in ((0, 1), (1, 1), (1, 0), (0, 0)):
            glTexCoord2f(u, v)
            glVertex3f(x + (u - 0.5) * width, y + (0.5 - v) * height, z)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)

    @staticmethod
    def _color(color):
        glColor3f(*color)

    @staticmethod
    def _unit_box():
        glBegin(GL_QUADS)
        for normal, vertices in (
            ((0, 0, 1), ((-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1))),
            ((0, 0, -1), ((1, -1, -1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1))),
            ((1, 0, 0), ((1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1))),
            ((-1, 0, 0), ((-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1))),
            ((0, 1, 0), ((-1, 1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1))),
            ((0, -1, 0), ((-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1))),
        ):
            glNormal3f(*normal)
            for vertex in vertices:
                glVertex3f(*vertex)
        glEnd()

    def box(self, x, y, z, sx, sy, sz, color):
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(sx, sy, sz)
        glCallList(self._cube)
        glPopMatrix()

    def cylinder(self, x, y, z, radius, height, color, slices=20):
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(self.quadric, radius, radius, height, slices, 1)
        glTranslatef(0, 0, height)
        gluDisk(self.quadric, 0, radius, slices, 1)
        glPopMatrix()

    def tube(self, start, end, radius, color, slices=10):
        length = dist(start, end)
        if length < 1e-6:
            return
        dx, dy, dz = (b - a for a, b in zip(start, end))
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(*start)
        if hypot(dx, dy) > 1e-6:
            glRotatef(degrees(acos(max(-1.0, min(1.0, dz / length)))), -dy, dx, 0)
        elif dz < 0:
            glRotatef(180, 1, 0, 0)
        gluCylinder(self.quadric, radius, radius, length, slices, 1)
        glPopMatrix()

    def world_to_editor(self, point):
        left, top, right, bottom = self.editor_bounds
        x, z = point
        return left + (x + 10) / 20 * (right - left), bottom - (z + 10) / 20 * (bottom - top)

    def editor_to_world(self, point):
        left, top, right, bottom = self.editor_bounds
        x, y = point
        return (x - left) / (right - left) * 20 - 10, (bottom - y) / (bottom - top) * 20 - 10

    def _sky_geometry(self):
        """Cúpula graduada con velos de nubes o estrellas según la hora."""
        haze = DAY_HAZE if self.day_mode else NIGHT_HAZE
        zenith = (0.28, 0.55, 0.73) if self.day_mode else (0.035, 0.066, 0.152)
        for band in range(16):
            glBegin(GL_QUAD_STRIP)
            for slice_index in range(49):
                azimuth = tau * slice_index / 48
                for ring in (band, band + 1):
                    elevation = -pi / 2 + pi * ring / 16
                    blend = min(1, max(0, (sin(elevation) + 0.055) * 1.9)) ** 0.6
                    glColor3f(*(a + (b - a) * blend for a, b in zip(haze, zenith)))
                    glVertex3f(105 * cos(elevation) * cos(azimuth), 105 * sin(elevation),
                               105 * cos(elevation) * sin(azimuth))
            glEnd()
        rng = Random(802)
        if self.day_mode:
            for index in range(15):
                a = index * tau / 15 + rng.uniform(-0.15, 0.15)
                radius = rng.uniform(57, 82)
                center = (radius * cos(a), rng.uniform(5, 17), radius * sin(a))
                width = rng.uniform(8, 17)
                glBegin(GL_TRIANGLE_FAN)
                glColor4f(1.0, 0.99, 0.92, rng.uniform(0.28, 0.48))
                glVertex3f(*center)
                glColor4f(1.0, 0.99, 0.92, 0)
                for segment in range(19):
                    b = tau * segment / 18
                    offset = width * cos(b)
                    glVertex3f(center[0] + sin(a) * offset, center[1] + sin(b) * width * 0.15,
                               center[2] - cos(a) * offset)
                glEnd()
        else:
            glPointSize(1.5)
            glBegin(GL_POINTS)
            for _ in range(340):
                a, e = rng.uniform(0, tau), rng.uniform(0.04, 1.45)
                glColor4f(0.83, 0.89, 1, rng.uniform(0.28, 0.9))
                glVertex3f(96 * cos(e) * cos(a), 96 * sin(e), 96 * cos(e) * sin(a))
            glEnd()
            glPointSize(1)
        self._distant_ridges()

    def _distant_ridges(self):
        """Dos perfiles de montañas detrás de las lomas del terreno."""
        colors = ((0.58, 0.69, 0.69), (0.49, 0.61, 0.60)) if self.day_mode else (
            (0.124, 0.178, 0.264), (0.098, 0.151, 0.217))
        for row, radius in enumerate((101, 88)):
            glBegin(GL_QUAD_STRIP)
            for index in range(129):
                a = index * tau / 128
                height = 6.75 - row * 2.45 + 3.25 * sin(a * 3 + row) ** 2
                height *= 0.68 + 0.42 * sin(a * 5 + 1.5 * row) ** 2
                height += 0.5 * cos(a * 19) + 0.68 * sin(a * 11 + row)
                x, z = radius * cos(a), radius * sin(a)
                glColor3f(*(DAY_HAZE if self.day_mode else NIGHT_HAZE))
                glVertex3f(x, -45, z)
                glColor3f(*colors[row])
                glVertex3f(x, height, z)
            glEnd()

    def _sky(self, eye):
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glDepthMask(GL_FALSE)
        glPushMatrix()
        glTranslatef(*eye)
        if self.day_mode not in self._sky_lists:
            self._sky_lists[self.day_mode] = self._compile(self._sky_geometry)
        glCallList(self._sky_lists[self.day_mode])
        glPopMatrix()
        glDepthMask(GL_TRUE)
        glEnable(GL_CULL_FACE)

    def _light_scene(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.36, 0.39, 0.40, 1) if self.day_mode else (0.30, 0.34, 0.43, 1))
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, (-0.44, 0.83, 0.46, 0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.80, 0.74, 0.59, 1) if self.day_mode else (0.26, 0.35, 0.52, 1))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (0.55, 0.52, 0.45, 1))
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, (0.72, 0.55, -0.41, 0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.23, 0.29, 0.33, 1) if self.day_mode else (0.14, 0.24, 0.40, 1))
        for light, x, z in ((GL_LIGHT2, 0, 8), (GL_LIGHT3, 7.2, -7), (GL_LIGHT4, -7, 5.5)):
            if self.day_mode:
                glDisable(light)
                continue
            glEnable(light)
            glLightfv(light, GL_POSITION, (x, 3.1, z, 1))
            glLightfv(light, GL_DIFFUSE, (0.88, 0.60, 0.32, 1))
            glLightf(light, GL_LINEAR_ATTENUATION, 0.21)
            glLightf(light, GL_QUADRATIC_ATTENUATION, 0.12)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.21, 0.21, 0.19, 1))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 30)
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, 24)
        glFogf(GL_FOG_END, 93)
        glFogfv(GL_FOG_COLOR, (*(DAY_HAZE if self.day_mode else NIGHT_HAZE), 1))

    def _begin_scene(self, park, camera, rider_camera):
        height = max(1, self.height - self.header_height - self.footer_height)
        width_px, height_px = self.physical_size
        glViewport(0, round(self.footer_height * height_px / self.height),
                   round(self.scene_width * width_px / self.width), round(height * height_px / self.height))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self.scene_width / height
        distance = camera["distance"]
        if self.perspective or rider_camera:
            gluPerspective(61 if rider_camera else 47, aspect, 0.08, 170)
        else:
            span = max(4, distance * 0.40)
            glOrtho(-span * aspect, span * aspect, -span, span, 0.08, 170)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        if rider_camera:
            (x, y, z), heading, pitch = park.coaster_pose()
            eye = (x, y + 0.76, z)
            target = (x + sin(heading) * 5, eye[1] + 4.0 * sin(pitch) - 0.28, z + cos(heading) * 5)
        else:
            yaw, pitch = camera["yaw"], camera["pitch"]
            target = camera.get("target", OVERVIEW_TARGET)
            eye = (target[0] + distance * cos(pitch) * sin(yaw), target[1] + distance * sin(pitch),
                   target[2] + distance * cos(pitch) * cos(yaw))
        gluLookAt(*eye, *target, 0, 1, 0)
        glDisable(GL_FOG)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glShadeModel(GL_SMOOTH)
        self._sky(eye)
        if self.depth_test:
            glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH if self.smooth_shading else GL_FLAT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if self.wireframe else GL_FILL)
        self._light_scene()

    def render_park(self, park, camera, rider_camera):
        self._begin_scene(park, camera, rider_camera)
        key = (self.day_mode, self.show_texture)
        if key not in self._landscape_lists:
            self._landscape_lists[key] = self._compile(self.draw_landscape)
        glCallList(self._landscape_lists[key])
        self.draw_coaster(park)
        self.draw_wheel(park)
        self.draw_carousel(park)
        if self.day_mode and self.depth_test and self.stencil_available and not self.wireframe:
            self._ride_shadows(park)
        self.draw_water(park.fountain_phase)
        self.draw_visitors(park.elapsed)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glViewport(0, 0, *self.physical_size)
        self._draw_park_hud(park, rider_camera)

    def _ride_shadows(self, park):
        """Proyección direccional recortada al suelo con profundidad y stencil."""
        plane = 0.046
        glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        glDisable(GL_LIGHTING)
        glDisable(GL_CULL_FACE)
        glEnable(GL_STENCIL_TEST)
        glDepthMask(GL_FALSE)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        glStencilFunc(GL_ALWAYS, 1, 1)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
        glPushMatrix()
        glMultMatrixf((1, 0, 0, 0, 0.44 / 0.83, 0, -0.46 / 0.83, 0,
                       0, 0, 1, 0, 0, plane, 0, 1))
        self.draw_coaster(park)
        self.draw_wheel(park)
        self.draw_carousel(park)
        glPopMatrix()
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glStencilFunc(GL_EQUAL, 1, 1)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
        glColor4f(0.12, 0.16, 0.17, 0.29)
        glBegin(GL_QUADS)
        for x, z in ((-14, -14), (-14, 14), (14, 14), (14, -14)):
            glVertex3f(x, plane, z)
        glEnd()
        glPopAttrib()

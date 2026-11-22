"""Laboratorio visual 2D con herramientas para explorar el mismo plano del parque."""

from __future__ import annotations

from math import ceil, cos, sin, tau
from typing import TYPE_CHECKING

from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_TRIANGLE_FAN
from OpenGL.GL import glBegin, glClear, glColor4f, glEnd, glVertex2f

from park3d.geometry.algorithms import (
    basic_line, bresenham_circle, bresenham_line, cohen_sutherland, coverage_line, dda_line,
    koch_curve, midpoint_circle, sample_bezier,
)
from park3d.geometry.transforms import identity3, rotate2, scale2, shear2, transform2, translate2

if TYPE_CHECKING:
    from park3d.scene.park import ParkModel


INK = (0.063, 0.094, 0.086, 1.0)
CARD = (0.111, 0.153, 0.138, 1.0)
WELL = (0.079, 0.122, 0.108, 1.0)
BORDER = (0.217, 0.283, 0.253, 1.0)
CREAM = (0.955, 0.931, 0.857, 1.0)
SAGE = (0.645, 0.731, 0.677, 1.0)
JADE = (0.49, 0.82, 0.67, 1.0)
CORAL = (0.98, 0.54, 0.43, 1.0)
SAND = (0.95, 0.8, 0.52, 1.0)
LILAC = (0.76, 0.67, 0.91, 1.0)

LAYERS = ("Plano", "Rasterización", "Curvas", "Matrices 2D")
TRANSFORMS = (
    ("Identidad", identity3()),
    ("Traslación", translate2(3, 2)),
    ("Rotación · 35°", rotate2(35)),
    ("Escala · 1.4 × 0.7", scale2(1.4, 0.7)),
    ("Reflexión · eje Z", scale2(-1, 1)),
    ("Cizallamiento", shear2(0.7, 0)),
)
BEZIER_PATH = sample_bezier([(-8, -6), (-2, -2), (3, -9), (8, -4)])
KOCH_PATH = koch_curve((-7, 1), (7, 1), 3)


class EditorMixin:
    """Panel de demostración, edición del trazado y transformaciones homogéneas."""

    editor_layer = 0
    editor_transform = 0
    editor_selected_control: int | None = None

    @property
    def editor_extent(self) -> int:
        return 21 if self.editor_layer in (0, 2) else 10

    def _studio_frames(self):
        margin = 26
        top = 158 if self.height >= 590 else 139
        bottom = self.height - 26
        panel_width = min(330, max(232, int(self.width * 0.29)))
        panel_left = self.width - margin - panel_width
        return margin, top, panel_left - 16, bottom, panel_left, panel_width

    def editor_layout(self) -> tuple[float, float, float, float]:
        left, top, right, bottom, _, _ = self._studio_frames()
        board_top = top + 39
        available_height = bottom - board_top - 42
        side = max(24, min(right - left - 55, available_height))
        x = (left + right - side) / 2
        y = board_top + (available_height - side) / 2
        return x, y, x + side, y + side

    def _editor_buttons(self):
        _, top, _, _, x, width = self._studio_frames()
        row = 39 if self.height >= 610 else 34
        for index, action in enumerate(("layer", "transform", "clip", "aa", "reset")):
            yield action, (x + 14, top + 47 + index * (row + 6), width - 28, row)

    def editor_action_at(self, position: tuple[float, float]) -> str | None:
        mx, my = position
        for action, (x, y, width, height) in self._editor_buttons():
            if x <= mx < x + width and y <= my < y + height:
                return action
        return None

    def cycle_editor_layer(self) -> None:
        self.editor_layer = (self.editor_layer + 1) % len(LAYERS)

    def cycle_editor_transform(self) -> None:
        if self.editor_layer == 3:
            self.editor_transform = (self.editor_transform + 1) % len(TRANSFORMS)
        self.editor_layer = 3

    def reset_editor_demos(self) -> None:
        self.editor_layer = self.editor_transform = 0
        self.editor_selected_control = None

    def adjust_editor_height(self, park: ParkModel, change: float) -> None:
        selected = self.editor_selected_control
        if self.editor_layer in (0, 2) and selected is not None:
            park.move_control_height(selected, park.track_heights[selected] + change)

    @staticmethod
    def _studio_fill(points, color) -> None:
        glColor4f(*color)
        glBegin(GL_TRIANGLE_FAN)
        for point in points:
            glVertex2f(*point)
        glEnd()

    def _map_line(self, points, color, width=1, closed=False) -> None:
        self.line2([self.world_to_editor(point) for point in points], color, width, closed)

    def _map_mark(self, point, color, size=7) -> None:
        x, y = self.world_to_editor(point)
        self.rect(x - size / 2, y - size / 2, size, size, color)

    def _studio_grid(self) -> None:
        left, top, right, bottom = self.editor_bounds
        self.rect(left, top, right - left, bottom - top, WELL)
        extent = self.editor_extent
        interval = 2 if extent > 10 else 1
        edge = extent - extent % interval
        for value in range(-edge, edge + 1, interval):
            x, _ = self.world_to_editor((value, 0))
            _, y = self.world_to_editor((0, value))
            major = value % (5 * interval) == 0
            color = BORDER if major else (0.144, 0.201, 0.168, 1.0)
            if not value:
                color = (0.35, 0.49, 0.41, 1.0)
            self.line2([(x, top), (x, bottom)], color)
            self.line2([(left, y), (right, y)], color)
            if major:
                label = str(value)
                label_width = self._font(11).size(label)[0]
                self.text(label, x - label_width / 2, bottom + 3, 11, SAGE)
                self.text(label, left - label_width - 6, y - 8, 11, SAGE)
        self.text("X", right + 16, bottom - 10, 12, JADE)
        self.text("Z", left - 17, top - 22, 12, JADE)

    def _studio_park(self, park: ParkModel) -> None:
        hull = [self.world_to_editor(point) for point in park.hull]
        if len(hull) > 2:
            self._studio_fill(hull, (0.27, 0.52, 0.39, 0.17))
        self.line2(hull, (0.45, 0.76, 0.62, 0.66), 1.6, True)
        for point in park.user_points:
            self._map_mark(point, JADE, 5)

        landmarks = (
            ((7, -7), 1.5, "Rueda"),
            ((-7.1, 5.5), 1.8, "Carrusel"),
        )
        for (cx, cz), radius, name in landmarks:
            circle = [(cx + radius * cos(tau * i / 40), cz + radius * sin(tau * i / 40)) for i in range(40)]
            self._map_line(circle, (0.75, 0.72, 0.52, 0.65), 1.4, True)
            self._map_mark((cx, cz), SAND, 4)
            x, y = self.world_to_editor((cx, cz - radius))
            self.text(name, x - 18, y + 3, 11, SAND)

        self._map_line(BEZIER_PATH, (0.74, 0.69, 0.85, 0.56), 1.5)
        self._studio_track(park)

    def _studio_track(self, park: ParkModel) -> None:
        self._map_line(park.control_points, (0.94, 0.67, 0.45, 0.44), 1, True)
        self._map_line(park.track_2d, (0.43, 0.18, 0.13, 1), 5)
        self._map_line(park.track_2d, CORAL, 2.4)
        for index, point in enumerate(park.control_points):
            selected = index == self.editor_selected_control
            self._map_mark(point, INK, 15 if selected else 9)
            self._map_mark(point, JADE if selected else SAND, 10 if selected else 5)
            if selected:
                x, y = self.world_to_editor(point)
                self.text(f"P{index + 1:02}", x + 9, y - 15, 12, JADE)
        station_x, _, station_z = park.track_position(park.station_progress)
        sx, sy = self.world_to_editor((station_x, station_z))
        self.rect(sx - 4, sy - 4, 8, 8, JADE)
        self.text("Estación", sx + 7, sy + 6, 11, JADE)
        x, _, z = park.track_position(park.ride_progress)
        self._map_mark((x, z), INK, 11)
        self._map_mark((x, z), CREAM, 7)

    def _studio_raster(self) -> None:
        samples = (
            (basic_line((-8, 7), (-1, 4)), SAND, "Ecuación directa"),
            (dda_line((-8, 3), (-1, 0)), JADE, "DDA"),
            (bresenham_line((-8, -1), (-1, -4)), CORAL, "Bresenham · recta"),
            (bresenham_circle((5, 4), 2), LILAC, "Bresenham · círculo"),
            (midpoint_circle((5, -4), 2), SAND, "Punto medio"),
        )
        for pixels, color, label in samples:
            for point in pixels:
                self._map_mark(point, color, 11)
            x, y = self.world_to_editor((min(p[0] for p in pixels), min(p[1] for p in pixels)))
            self.text(label, x - 6, y + 9, 11, color)
        start, end = (-8, -6), (-1, -8)
        if self.antialias:
            for x, y, coverage in coverage_line(start, end):
                self._map_mark((x, y), (*CREAM[:3], coverage), 11)
        else:
            for point in bresenham_line(start, end):
                self._map_mark(point, CREAM, 11)
        x, y = self.world_to_editor((-8, -8))
        self.text("Cobertura activada" if self.antialias else "Cobertura desactivada", x - 6, y + 9, 11, CREAM)

    def _studio_curves(self, park: ParkModel) -> None:
        self._studio_track(park)
        self._map_line([(1.25 * x, z - 7) for x, z in BEZIER_PATH], LILAC, 2.5)
        self._map_line([(1.25 * x, z + 13) for x, z in KOCH_PATH], JADE, 2.1)

    def _studio_matrices(self) -> None:
        _, matrix = TRANSFORMS[self.editor_transform]
        footprint = [(-5, -3), (4, -3), (4, 1), (1, 1), (1, 4), (-5, 4)]
        transformed = [transform2(point, matrix) for point in footprint]
        self._map_line(footprint, SAGE, 2, True)
        self._map_line(transformed, JADE, 3, True)
        for source, result in zip(footprint, transformed):
            self._map_line([source, result], (0.81, 0.60, 0.42, 0.7), 1)
            self._map_mark(source, SAGE, 5)
            self._map_mark(result, SAND, 7)

    def _studio_clip(self) -> None:
        scale = self.editor_extent / 10
        bounds = tuple(value * scale for value in (-4, -9, 4, -4))
        start, end = (-9 * scale, -8 * scale), (8 * scale, -3 * scale)
        x0, z0, x1, z1 = bounds
        self._map_line([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], CREAM, 1.4, True)
        self._map_line([start, end], (0.69, 0.76, 0.70, 0.55), 2)
        clipped = cohen_sutherland(start, end, bounds)
        if clipped:
            self._map_line(clipped, SAND, 3.4)

    def _studio_legend(self, x: float, y: float) -> None:
        legends = (
            ((CORAL, "Trazado"), (SAND, "Puntos de control"), (JADE, "Envolvente de Graham"), (LILAC, "Sendero")),
            ((SAND, "Cada cuadrado representa un píxel calculado"),),
            ((CORAL, "B-spline cúbica"), (LILAC, "Bézier"), (JADE, "Fractal de Koch")),
            ((SAGE, "Antes"), (JADE, "Transformado")),
        )
        for color, label in legends[self.editor_layer]:
            self.rect(x, y + 6, 7, 7, color)
            self.text(label, x + 13, y, 11, CREAM)
            x += self._font(11).size(label)[0] + 27

    def _studio_profile(self, park: ParkModel, x: float, y: float, width: float, bottom: float) -> None:
        elevations = [point[1] for point in park.track_3d]
        peak = max(elevations)
        self.rect(x, y, width, bottom - y, WELL)
        self.text("PERFIL DEL RECORRIDO", x + 11, y + 8, 11, SAGE)
        fields = (
            (str(len(park.control_points)), "Puntos"),
            (f"{park.track_length:.0f} m", "Longitud"),
            (f"{peak:.1f} m", "Altura máx."),
        )
        for column, (value, label) in enumerate(fields):
            column_x = x + 11 + column * (width - 18) / 3
            self.text(value, column_x, y + 23, 17, CREAM)
            self.text(label, column_x, y + 43, 11, SAGE)

        chart_left, chart_right = x + 11, x + width - 11
        chart_top, chart_bottom = y + 62, bottom - 24
        if chart_bottom > chart_top + 8:
            maximum = max(1, ceil(peak))
            plot_width, plot_height = chart_right - chart_left, chart_bottom - chart_top

            def profile_point(progress: float, elevation: float) -> tuple[float, float]:
                return chart_left + progress * plot_width, chart_bottom - elevation / maximum * plot_height

            self.line2([(chart_left, chart_top), (chart_right, chart_top)], BORDER)
            self.line2([(chart_left, chart_bottom), (chart_right, chart_bottom)], BORDER)
            step = max(1, len(park.track_3d) // 96)
            length = max(1e-6, park.track_length)
            profile = [profile_point(park.track_distances[i] / length, elevations[i])
                       for i in range(0, len(elevations) - 1, step)]
            profile.append(profile_point(1.0, elevations[-1]))
            self.line2(profile, CORAL, 1.7)
            station_x, _ = profile_point(park.station_progress, 0)
            self.line2([(station_x, chart_top), (station_x, chart_bottom)], (0.49, 0.82, 0.67, 0.5))
            _, current_height, _ = park.track_position(park.ride_progress)
            train_x, train_y = profile_point(park.ride_progress, current_height)
            self.line2([(train_x, train_y), (train_x, chart_bottom)], (0.92, 0.87, 0.74, 0.40))
            self.rect(train_x - 2.5, train_y - 2.5, 5, 5, CREAM)

        selected = self.editor_selected_control
        hint = ("Arrastra un punto para editar."
                if selected is None else f"P{selected + 1:02} · {park.track_heights[selected]:.2f} m  [ ] Altura")
        self.text(hint, x + 11, bottom - 17, 11, JADE)

    def _studio_panel(self, park: ParkModel, clip_demo: bool) -> None:
        _, top, _, bottom, left, panel_width = self._studio_frames()
        self.rect(left, top, panel_width, bottom - top, CARD)
        self.text("HERRAMIENTAS", left + 17, top + 16, 13, SAGE)
        name, matrix = TRANSFORMS[self.editor_transform]
        buttons = {
            "layer": ("B", LAYERS[self.editor_layer]),
            "transform": ("X", name if self.editor_layer == 3 else "Transformaciones 2D"),
            "clip": ("V", "Recorte activo" if clip_demo else "Recorte de líneas"),
            "aa": ("F", "Suavizado activado" if self.antialias else "Suavizado desactivado"),
            "reset": ("R", "Restaurar plano"),
        }
        for action, (x, y, width, height) in self._editor_buttons():
            key, label = buttons[action]
            selected = action == "layer" or (action == "clip" and clip_demo)
            self.rect(x, y, width, height, BORDER if selected else WELL)
            self.rect(x + 8, y + 7, 25, height - 14, JADE if selected else CARD)
            self.text(key, x + 16, y + (height - 15) / 2, 12, INK if selected else JADE)
            self.text(label, x + 45, y + (height - 18) / 2, 14, CREAM)
            if action in {"layer", "transform"}:
                self.text("›", x + width - 20, y + (height - 18) / 2, 14, JADE)
        matrix_y = bottom - 123
        if self.editor_layer == 3:
            self.rect(left + 14, matrix_y - 8, panel_width - 28, 106, WELL)
            self.text("Matriz homogénea 3 × 3", left + 27, matrix_y + 2, 13, SAGE)
            for row, values in enumerate(matrix):
                for column, value in enumerate(values):
                    self.text(f"{0 if abs(value) < .005 else value:.2f}", left + 29 + column * 54,
                              matrix_y + 28 + row * 18, 12, CREAM)
        elif self.editor_layer == 1:
            self.text("Algoritmos de dibujo", left + 17, matrix_y + 14, 15, CREAM)
            self.text("Compara las rectas y los círculos", left + 17, matrix_y + 46, 13, SAGE)
            self.text("generados sobre la misma cuadrícula.", left + 17, matrix_y + 66, 13, SAGE)
        else:
            profile_y = max(y + height + 12, bottom - 258)
            self._studio_profile(park, left + 14, profile_y, panel_width - 28, bottom - 12)

    def render_editor(self, park: ParkModel, clip_demo: bool = False) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._overlay_begin()
        self.rect(0, 0, self.width, self.height, INK)
        self._navigation("editor")
        left, top, right, bottom, _, _ = self._studio_frames()
        self.text("Editor del parque", left, 91, 28, CREAM)
        if self.height >= 590:
            guides = (
                "Arrastra los puntos del circuito o haz clic en el plano para ampliar su contorno.",
                "Compara los píxeles generados por cada algoritmo en la cuadrícula.",
                "Compara curvas paramétricas y fractales. Los puntos arena editan la B-spline.",
                "Cambia de operación para comparar la figura original con la transformada.",
            )
            self.text(guides[self.editor_layer], left, 127, 14, SAGE)
        self.rect(left, top, right - left, bottom - top, CARD)
        self.text("PLANO CARTESIANO", left + 15, top + 13, 12, SAGE)
        self.text("X / Z", right - 46, top + 13, 12, JADE)
        self._studio_grid()
        if self.editor_layer == 0:
            self._studio_park(park)
        elif self.editor_layer == 1:
            self._studio_raster()
        elif self.editor_layer == 2:
            self._studio_curves(park)
        else:
            self._studio_matrices()
        if clip_demo:
            self._studio_clip()
        self._studio_legend(left + 15, bottom - 20)
        self._studio_panel(park, clip_demo)
        self._overlay_end()

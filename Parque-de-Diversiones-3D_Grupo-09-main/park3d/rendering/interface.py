"""Paneles y navegación compartidos por las vistas del parque."""

from __future__ import annotations

from math import cos, pi, sin

from park3d.scene.park import DEFAULT_RIDE_SPEED

INK = (0.062, 0.100, 0.099, 1)
DEEP = (0.043, 0.075, 0.074, 1)
PANEL = (0.082, 0.131, 0.124, 1)
TILE = (0.112, 0.174, 0.157, 1)
LINE = (0.176, 0.252, 0.223, 1)
PAPER = (0.950, 0.942, 0.875, 1)
MUTED = (0.652, 0.748, 0.701, 1)
MINT = (0.617, 0.815, 0.699, 1)
GOLD = (0.947, 0.767, 0.461, 1)
CORAL = (0.952, 0.595, 0.470, 1)

NAVIGATION = (("park", "Parque 3D", "P"), ("editor", "Editor 2D", "E"),
              ("lessons", "Temario", "A"), ("help", "Ayuda", "H"))

RIDES = (
    ("Montaña rusa", "Circuito del valle · B-spline", CORAL, "coaster"),
    ("Rueda panorámica", "Viaja en una cabina suspendida", MINT, "wheel"),
    ("Carrusel", "Monta uno de los ocho caballos", GOLD, "carousel"),
)

LESSONS = (
    ("Fundamentos gráficos", "GPU, evolución y aplicaciones"),
    ("Geometría 2D", "Plano y cápsula convexa de Graham"),
    ("Rasterización", "DDA, Bresenham y punto medio"),
    ("Atributos de dibujo", "Relleno, grosor y antialiasing"),
    ("Matrices homogéneas", "Transformaciones 2D"),
    ("Transformaciones 3D", "Matrices 4 × 4, cámara y volumen"),
    ("Proyecciones", "Perspectiva y ortográfica"),
    ("Integración 2D", "Editor y recorte Cohen–Sutherland"),
    ("Curvas y continuidad", "Circuito B-spline y perfil de altura"),
    ("Superficies y curvas", "Bézier, mallas y fractal de Koch"),
    ("Representación de fronteras", "Caras y normales de las casetas"),
    ("Sólidos constructivos", "Cavidad del túnel"),
    ("Visibilidad", "Z-buffer y culling"),
    ("Mapeado y texturas", "UV y textura bitmap cargada desde archivo"),
    ("Luz, sombreado y color", "Iluminación, RGB y conversión HSV"),
    ("Demostración final", "Editor, circuito y diagnóstico"),
)


class InterfaceMixin:
    """Controles visibles con las mismas áreas activas que usa el mouse."""

    header_height = 74
    footer_height = 48

    @property
    def scene_width(self) -> int:
        return self.width - (278 if self.width >= 1080 else 250)

    def _navigation_items(self):
        start = max(260, (self.width - 418) // 2)
        for index, (action, label, key) in enumerate(NAVIGATION):
            yield action, label, key, (start + index * 104, 19, 100, 36)

    def _park_items(self, rider_camera=False):
        left, width = self.scene_width + 17, self.width - self.scene_width - 34
        if self.selected_ride is not None or rider_camera:
            yield "overview", (left, 123, width, 31)
        for index in range(len(RIDES)):
            yield f"ride{index}", (left, 163 + index * 64, width, 55)
        half = (width - 8) / 2
        for index, action in enumerate(("camera", "lighting", "projection", "texture", "mesh", "pause")):
            yield action, (left + index % 2 * (half + 8), 392 + index // 2 * 45, half, 37)
        yield "slower", (self.width - 94, 547, 34, 32)
        yield "faster", (self.width - 52, 547, 34, 32)

    def action_at(self, position, view, rider_camera=False):
        items = [(name, bounds) for name, _, _, bounds in self._navigation_items()]
        if view == "park":
            items += list(self._park_items(rider_camera))
        x, y = position
        return next((name for name, (left, top, width, height) in items
                     if left <= x < left + width and top <= y < top + height), None)

    def _outline(self, x, y, w, h, color=LINE):
        self.rect(x, y, w, 1, color)
        self.rect(x, y + h - 1, w, 1, color)
        self.rect(x, y, 1, h, color)
        self.rect(x + w - 1, y, 1, h, color)

    def _navigation(self, active):
        self.rect(0, 0, self.width, self.header_height, DEEP)
        self.rect(0, self.header_height - 1, self.width, 1, LINE)
        self.rect(24, 21, 32, 32, TILE)
        self.line2([(29, 44), (36, 32), (42, 40), (49, 28)], GOLD, 2)
        self.line2([(29, 48), (50, 48)], MINT, 1)
        self.text("Mirador del Valle", 68, 13, 23, PAPER)
        self.text("Parque Visual 3D", 69, 43, 13, MUTED)
        for action, label, key, (x, y, w, h) in self._navigation_items():
            if action == active:
                self.rect(x, y, w, h, TILE)
                self.rect(x, y + h - 2, w, 2, MINT)
            self.text(label, x + 10, y + 9, 15, PAPER if action == active else MUTED)
            self.text(key, x + w - 16, y + 11, 12, MINT)
        if self.width >= 1080:
            self.text("Computación Visual", self.width - 165, 28, 15, MUTED)

    def _ride_icon(self, kind, x, y, color):
        if kind == "wheel":
            rim = [(x + 10 * cos(i * pi / 12), y + 10 * sin(i * pi / 12)) for i in range(24)]
            self.line2(rim, color, 1.4, closed=True)
            for i in range(0, 24, 4):
                self.line2([(x, y), rim[i]], color, 1)
        elif kind == "carousel":
            self.line2([(x - 11, y - 1), (x, y - 9), (x + 11, y - 1),
                        (x - 11, y - 1)], color, 1.5)
            self.line2([(x, y - 1), (x, y + 8)], color, 1.5)
            self.line2([(x - 9, y + 8), (x + 9, y + 8)], color, 1.5)
        else:
            self.line2([(x - 11, y + 6), (x - 7, y - 4), (x - 3, y - 7),
                        (x + 3, y + 4), (x + 7, y + 4), (x + 11, y - 2)], color, 1.7)
            self.line2([(x - 7, y - 4), (x - 7, y + 8)], color)
            self.line2([(x, y), (x, y + 8)], color)

    def _draw_park_hud(self, park, rider_camera):
        self._overlay_begin()
        self._navigation("park")
        panel_x = self.scene_width
        self.rect(panel_x, self.header_height, self.width - panel_x, self.height - self.header_height, INK)
        self.rect(panel_x, self.header_height, 1, self.height - self.header_height, LINE)
        self.text("Atracciones", panel_x + 17, 94, 23, PAPER)
        if self.selected_ride is None and not rider_camera:
            self.text("Elige una atracción y pulsa C.", panel_x + 17, 130, 14, MUTED)
        self.text("Vista y simulación", panel_x + 17, 355, 20, PAPER)
        settings = {
            "overview": ("‹  Vista general", ""),
            "camera": ("Bajar" if rider_camera else "Subir", "C"),
            "lighting": ("Día" if self.day_mode else "Noche", "L"),
            "projection": ("Perspectiva" if self.perspective or rider_camera else "Ortográfica", "O"),
            "texture": ("Texturas" if self.show_texture else "Color plano", "T"),
            "mesh": ("Malla" if self.wireframe else "Sólidos", "M"),
            "pause": ("Reanudar" if park.paused else "Pausar", ""),
            "slower": ("−", ""),
            "faster": ("+", ""),
        }
        for action, (x, y, w, h) in self._park_items(rider_camera):
            if action.startswith("ride"):
                index = int(action[-1])
                name, detail, color, icon = RIDES[index]
                active = self.selected_ride == index or rider_camera and self.onboard_ride == index
                self.rect(x, y, w, h, TILE if active else PANEL)
                self._outline(x, y, w, h, color if active else LINE)
                self._ride_icon(icon, x + 22, y + 27, color)
                self.text(name, x + 41, y + 7, 16, PAPER)
                self.text(detail, x + 41, y + 29, 12, MUTED)
                self.text(str(index + 1), x + w - 17, y + 11, 11, color)
            else:
                label, key = settings[action]
                self.rect(x, y, w, h, TILE if action == "camera" else PANEL)
                self._outline(x, y, w, h, MINT if action == "camera" else LINE)
                if action in ("slower", "faster"):
                    self.text(label, x + 11, y + 6, 15, GOLD)
                else:
                    self.text(label, x + 8, y + 9, 13, PAPER)
                if key:
                    self.text(key, x + w - 16, y + 10, 12, MINT)
        self.text("Ritmo del tren", panel_x + 17, 537, 14, MUTED)
        self.text(f"{park.ride_speed / DEFAULT_RIDE_SPEED:.1f} ×", panel_x + 17, 558, 21, PAPER)
        if not self.depth_test:
            self.text("Z · Profundidad desactivada", panel_x + 17, 588, 13, GOLD)
        if not self.smooth_shading:
            self.text("G · Sombreado plano", panel_x + 17, 608 if not self.depth_test else 588, 13, GOLD)
        footer = self.height - self.footer_height
        self.rect(0, footer, self.width, self.footer_height, DEEP)
        self.rect(0, footer, self.width, 1, LINE)
        if rider_camera:
            ride = self.onboard_ride
            if ride:
                seat_label = "Cabina" if ride == 1 else "Caballo"
                label = f"{seat_label} {self.onboard_seats[ride] + 1:02d} / {self.onboard_seat_count}"
            else:
                label = "Primer vagón"
            self.rect(18, footer - 52, 170, 34, DEEP)
            self.text(label, 30, footer - 44, 14, PAPER)
            seat_hint = "   ·   Tab cambia de asiento" if ride else ""
            hint = f"Arrastra para mirar   ·   C para bajar{seat_hint}   ·   F11 vista inmersiva"
        else:
            hint = "Arrastra para orbitar   ·   Rueda para acercar   ·   C para subir   ·   F11 vista inmersiva"
        self.text(hint, 23, footer + 14, 14, MUTED)
        status = "En pausa" if park.paused else "Simulación activa"
        self.rect(self.width - 161, footer + 20, 6, 6, GOLD if park.paused else MINT)
        self.text(status, self.width - 148, footer + 14, 14, PAPER)
        self._overlay_end()

    def render_lessons(self):
        self._begin_panel("lessons")
        self.text("Computación Visual", 32, 96, 32, PAPER)
        self.text("Dieciséis semanas de teoría y práctica en el parque.", 33, 141, 16, MUTED)
        gap = 10
        width = (self.width - 64 - 3 * gap) / 4
        height = (self.height - 204 - 3 * gap) / 4
        for index, (title, evidence) in enumerate(LESSONS):
            column, row = index % 4, index // 4
            x, y = 32 + column * (width + gap), 176 + row * (height + gap)
            accent = MINT if index < 8 else GOLD if index < 12 else CORAL
            self.rect(x, y, width, height, PANEL)
            self._outline(x, y, width, height)
            padding = max(8, (height - 64) / 2)
            self.rect(x, y + 1, 2, height - 2, accent)
            self.text(f"Semana {index + 1:02}", x + 14, y + padding, 12, accent)
            self.text(title, x + 14, y + padding + 17, 15, PAPER)
            self.text(evidence, x + 14, y + padding + 39, 12, MUTED)
        self._overlay_end()

    def render_help(self):
        self._begin_panel("help")
        self.text("Guía de exploración", 32, 96, 32, PAPER)
        self.text("Teclas y controles del parque y su laboratorio 2D.", 33, 141, 16, MUTED)
        groups = (
            ("Cámara y animación", ("1 / 2 / 3   Seleccionar atracción", "C   Subir a la atracción o bajar",
                                   "Arrastrar   Orbitar o mirar desde el asiento", "Tab   Cambiar de cabina o caballo",
                                   "F11   Vista inmersiva  ·  Inicio   Vista general",
                                   "Espacio   Pausa  ·  − / +   Velocidad del tren")),
            ("Renderizado", ("L   Cambiar día o noche", "T   Activar o desactivar texturas",
                             "O   Cambiar de proyección", "M   Alternar relleno y malla", "Z   Comparar con y sin Z-buffer",
                             "G   Comparar sombreado plano y suave")),
            ("Laboratorio 2D", ("Clic en el plano   Agregar punto para Graham",
                                "Arrastrar un punto de control   Editar la B-spline", "B   Cambiar capa de algoritmos",
                                "− / +   Cambiar altura del punto elegido", "X   Cambiar transformación 2D",
                                "V   Recorte  ·  F   Antialiasing  ·  R   Reiniciar")),
            ("Hardware y aplicaciones", ("La CPU calcula curvas, modelos y animación.",
                                          "OpenGL usa la GPU para proyectar y rasterizar.",
                                          "Las mismas técnicas sirven en CAD y simulación.",
                                          f"OpenGL {self.gl_version}", self.gl_device)),
        )
        w = (self.width - 76) / 2
        h = (self.height - 207) / 2
        for index, (title, details) in enumerate(groups):
            x, y = 32 + index % 2 * (w + 12), 178 + index // 2 * (h + 12)
            self.rect(x, y, w, h, PANEL)
            self._outline(x, y, w, h)
            self.text(title, x + 17, y + 12, 20, MINT)
            for row, detail in enumerate(details):
                self.text(detail, x + 17, y + 47 + 23 * row, 14, PAPER)
        self._overlay_end()

    def _begin_panel(self, view):
        from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glClear

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._overlay_begin()
        self.rect(0, 0, self.width, self.height, INK)
        self._navigation(view)

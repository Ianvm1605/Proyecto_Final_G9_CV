"""Bucle de aplicación e interacción del Parque Visual 3D."""

from __future__ import annotations

from math import exp, pi

import pygame

from park3d.rendering import Renderer
from park3d.rendering.renderer import CAMERA_HOME, OVERVIEW_TARGET, RIDE_VIEWS
from park3d.scene import ParkModel


class ParkApplication:
    """Coordina modelos, vistas e interacción sin mezclarla con los algoritmos."""

    WINDOW_SIZE = (1360, 820)

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Parque Visual 3D · Computación Visual")
        desktop_width, desktop_height = pygame.display.get_desktop_sizes()[0]
        size = (min(self.WINDOW_SIZE[0], desktop_width - 48), min(self.WINDOW_SIZE[1], desktop_height - 100))
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        flags = pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
        try:
            pygame.display.set_mode(size, flags)
        except pygame.error:
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 0)
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 0)
            pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 0)
            pygame.display.set_mode(size, flags)
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(size)
        self.park = ParkModel()
        self.view = "park"
        self.running = True
        self.rider_camera = False
        self.clip_demo = False
        self.drag_control: int | None = None
        self.dragging_camera = False
        self.camera = {**CAMERA_HOME, "target": OVERVIEW_TARGET}
        self.camera_goal = self.camera.copy()

    def _editor_control_at(self, position: tuple[float, float]) -> int | None:
        world = self.renderer.editor_to_world(position)
        for index, point in enumerate(self.park.control_points):
            if (point[0] - world[0]) ** 2 + (point[1] - world[1]) ** 2 < 0.65**2:
                return index
        return None

    def _focus(self, index: int | None) -> None:
        self.renderer.selected_ride = index
        self.rider_camera = False
        if index is None:
            self.camera_goal = {**CAMERA_HOME, "target": OVERVIEW_TARGET}
        else:
            target, yaw, pitch, distance = RIDE_VIEWS[index]
            self.camera_goal = {"yaw": yaw, "pitch": pitch, "distance": distance, "target": target}

    def _act(self, action: str) -> None:
        settings = {
            "lighting": "day_mode", "texture": "show_texture", "projection": "perspective",
            "mesh": "wireframe", "aa": "antialias", "depth": "depth_test", "shade": "smooth_shading",
        }
        if action in ("park", "editor", "lessons", "help"):
            self.view = action
            self.drag_control, self.dragging_camera = None, False
        elif action in settings:
            attribute = settings[action]
            if action == "projection" and self.rider_camera:
                self.rider_camera = False
                self.renderer.perspective = False
                return
            setattr(self.renderer, attribute, not getattr(self.renderer, attribute))
        elif action == "camera":
            self.rider_camera = not self.rider_camera
        elif action == "pause":
            self.park.paused = not self.park.paused
        elif action in ("slower", "faster"):
            speed = self.park.ride_speed + (0.01 if action == "faster" else -0.01)
            self.park.ride_speed = min(0.25, max(0.01, speed))
        elif action == "overview":
            self._focus(None)
        elif action.startswith("ride"):
            self._focus(int(action[-1]))
        elif action == "clip":
            self.clip_demo = not self.clip_demo
        elif action == "layer":
            self.renderer.cycle_editor_layer()
        elif action == "transform":
            self.renderer.cycle_editor_transform()
        elif action == "reset":
            self.park = ParkModel()
            self.clip_demo = False
            self.renderer.reset_editor_demos()

    def _handle_key(self, key: int) -> None:
        general = {pygame.K_p: "park", pygame.K_e: "editor", pygame.K_a: "lessons", pygame.K_h: "help"}
        park_actions = {
            pygame.K_c: "camera", pygame.K_SPACE: "pause", pygame.K_t: "texture", pygame.K_l: "lighting",
            pygame.K_o: "projection", pygame.K_m: "mesh", pygame.K_z: "depth", pygame.K_g: "shade",
            pygame.K_HOME: "overview",
        }
        editor_actions = {pygame.K_v: "clip", pygame.K_c: "clip", pygame.K_f: "aa",
                          pygame.K_b: "layer", pygame.K_x: "transform", pygame.K_r: "reset"}
        current_actions = park_actions if self.view == "park" else editor_actions if self.view == "editor" else {}
        action = general.get(key) or current_actions.get(key)
        if key == pygame.K_ESCAPE:
            self.running = False
        elif action:
            self._act(action)
        elif self.view == "park" and key in (pygame.K_LEFTBRACKET, pygame.K_MINUS, pygame.K_KP_MINUS):
            self._act("slower")
        elif self.view == "park" and key in (pygame.K_RIGHTBRACKET, pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
            self._act("faster")

    def _handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.VIDEORESIZE and event.w > 0 and event.h > 0:
            self.renderer.resize((event.w, event.h))
        elif event.type == pygame.KEYDOWN:
            self._handle_key(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                position = self.renderer.logical_position(event.pos)
                action = self.renderer.action_at(position, self.view)
                if not action and self.view == "editor":
                    action = self.renderer.editor_action_at(position)
                if action:
                    self._act(action)
                    return
                if self.view == "editor":
                    left, top, right, bottom = self.renderer.editor_bounds
                    if self.renderer.editor_layer in (0, 2) and left <= position[0] <= right and top <= position[1] <= bottom:
                        self.drag_control = self._editor_control_at(position)
                        if self.drag_control is None and self.renderer.editor_layer == 0:
                            self.park.add_editor_point(self.renderer.editor_to_world(position))
                elif (self.view == "park" and not self.rider_camera
                      and position[0] < self.renderer.scene_width
                      and self.renderer.header_height <= position[1] < self.renderer.height - self.renderer.footer_height):
                    self.dragging_camera = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drag_control, self.dragging_camera = None, False
        elif event.type == pygame.MOUSEMOTION:
            if self.view == "editor" and self.drag_control is not None:
                position = self.renderer.logical_position(event.pos)
                self.park.move_control_point(self.drag_control, self.renderer.editor_to_world(position))
            elif self.view == "park" and self.dragging_camera and not self.rider_camera:
                dx, dy = event.rel
                self.camera["yaw"] += dx * 0.010
                self.camera["pitch"] = max(0.10, min(pi * 0.47, self.camera["pitch"] - dy * 0.010))
                self.camera_goal.update(yaw=self.camera["yaw"], pitch=self.camera["pitch"])
        elif event.type == pygame.MOUSEWHEEL and self.view == "park" and not self.rider_camera:
            distance = self.camera_goal["distance"] * 0.90**event.y
            self.camera_goal["distance"] = max(8.0, min(58.0, distance))

    def _update_camera(self, seconds: float) -> None:
        blend = 1 - exp(-7 * seconds)
        for value in ("pitch", "distance"):
            self.camera[value] += (self.camera_goal[value] - self.camera[value]) * blend
        yaw_delta = (self.camera_goal["yaw"] - self.camera["yaw"] + pi) % (2 * pi) - pi
        self.camera["yaw"] += yaw_delta * blend
        self.camera["target"] = tuple(a + (b - a) * blend for a, b in zip(self.camera["target"], self.camera_goal["target"]))

    def _draw(self) -> None:
        if self.view == "park":
            self.renderer.render_park(self.park, self.camera, self.rider_camera)
        elif self.view == "editor":
            self.renderer.render_editor(self.park, self.clip_demo)
        elif self.view == "lessons":
            self.renderer.render_lessons()
        else:
            self.renderer.render_help()
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            seconds = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                self._handle_event(event)
            self.park.tick(seconds)
            self._update_camera(seconds)
            self._draw()
        pygame.quit()

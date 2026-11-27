"""Carga de recursos gráficos compartidos por los renderizadores."""

from __future__ import annotations

from pathlib import Path

import pygame
from OpenGL.GL import (
    GL_LINEAR, GL_LINEAR_MIPMAP_LINEAR, GL_REPEAT, GL_RGB, GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T, GL_UNSIGNED_BYTE, glBindTexture, glGenTextures,
    glTexParameteri,
)
from OpenGL.GLU import gluBuild2DMipmaps


def load_texture(path: Path) -> int:
    """Carga una imagen RGB desde disco y la sube a la GPU."""
    surface = pygame.image.load(str(path)).convert()
    width, height = surface.get_size()
    pixels = pygame.image.tobytes(surface, "RGB", True)
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, width, height, GL_RGB, GL_UNSIGNED_BYTE, pixels)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return texture

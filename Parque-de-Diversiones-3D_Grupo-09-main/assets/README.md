# Recursos gráficos

Los recursos del proyecto se guardan bajo `assets/` para que las rutas no dependan del directorio actual de la consola.

## Texturas

- `textures/brick_sample.png`: bitmap de ladrillo usado en la bóveda peatonal como ejemplo de textura procedente de archivo.
- Césped y pavimentos: materiales de mosaico generados de forma procedural por `park3d/scenery/landscape.py`.

La app carga el bitmap de ladrillo con `park3d.assets.load_texture`. Si se reemplaza el archivo, conserva un formato de imagen que Pygame pueda leer y coordenadas UV repetibles. Evita cargar imágenes fuera de `assets/` mediante rutas absolutas.

Para agregar una textura:

1. Coloca el archivo en `assets/textures/`.
2. Cárgalo después de crear la ventana OpenGL.
3. Asigna coordenadas UV a los vértices de la superficie.
4. Actualiza este README y `docs/coverage.md` con el material y la evidencia.

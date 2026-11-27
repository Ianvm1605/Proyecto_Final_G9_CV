# Arquitectura del proyecto

## Límites entre módulos

- `park3d/geometry/` contiene cálculos puros. Los algoritmos no importan OpenGL ni Pygame.
- `park3d/scene/` mantiene el estado del parque, sus recorridos y animación.
- `park3d/rides/` define geometría y poses de las atracciones.
- `park3d/scenery/` define terreno y arquitectura estática.
- `park3d/rendering/` dibuja la escena y administra vistas y controles gráficos.
- `park3d/assets.py` carga imágenes desde `assets/` dentro del contexto OpenGL.
- `park3d/app.py` coordina los eventos, la simulación y las vistas.

## Módulos de geometría

`raster.py`, `hull.py`, `clipping.py` y `curves.py` separan algoritmos por tema. `transforms.py` conserva las transformaciones 2D, `transforms3d.py` las matrices 4 × 4 y `color_models.py` las conversiones de color. `algorithms.py` mantiene los nombres anteriores para que los imports existentes sigan funcionando.

## Reglas para nuevos cambios

1. Mantener fórmulas y datos geométricos fuera de los módulos de dibujo.
2. Hacer que la escena entregue formas o mallas al renderizador; evitar estado del curso dentro de las funciones gráficas.
3. Cargar texturas desde `assets/` mediante `park3d/assets.py` y mantener un material de reserva cuando un recurso sea opcional.
4. Añadir cada evidencia al editor, al mapa del sílabo y a `docs/coverage.md` en el mismo cambio.
5. Documentar los entregables académicos en `docs/`; PE1 y los trabajos colaborativos necesitan evidencia escrita aparte de la aplicación.

# Renderizado

Esta capa representa el estado de `scene/` y las geometrías de `geometry/`, `rides/` y `scenery/` en una ventana OpenGL. La aplicación crea el contexto y construye `Renderer` después de inicializar Pygame.

## Responsabilidades

- `renderer.py`: contexto gráfico, cámara, primitivas, escena principal y composición de los mixins.
- `interface.py`: navegación, controles visibles, ayuda y pantalla de semanas.
- `studio.py`: editor 2D y demostraciones visuales de algoritmos y transformaciones.
- `park3d/assets.py`: decodificación de imágenes y carga de texturas al contexto OpenGL.
- `scenery/landscape.py`: materiales, terreno y arquitectura estática.
- `rides/attractions.py`: mallas y dibujo de la montaña rusa, rueda y carrusel.

## Ciclo de una imagen

1. `ParkApplication` procesa eventos y actualiza el estado del parque.
2. La aplicación selecciona la vista del parque, editor, temario o ayuda.
3. `Renderer` configura cámara, proyección, profundidad, sombreado e iluminación.
4. Los mixins dibujan objetos de escena y paneles de interfaz.
5. Pygame intercambia los buffers al final del ciclo.

## Recursos y contexto

Las texturas OpenGL se deben cargar cuando ya existe un contexto gráfico activo. Usa `park3d.assets.load_texture(Path(...))` para imágenes distribuidas en `assets/`. El helper aplica repetición UV y filtros mipmap; los materiales procedurales pueden funcionar como respaldo.

## Convenciones

- Mantén las fórmulas geométricas fuera de este paquete.
- Mantén el estado del parque fuera de las rutinas de dibujo.
- Agrupa en `interface.py` los elementos de navegación y en `studio.py` las visualizaciones didácticas.
- Si un archivo de renderizado crece demasiado, extrae un mixin por responsabilidad y documenta su contrato antes de cambiar la herencia de `Renderer`.

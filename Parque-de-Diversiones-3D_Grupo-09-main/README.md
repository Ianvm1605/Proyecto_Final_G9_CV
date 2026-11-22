# Mirador del Valle · Parque Visual 3D

Aplicación interactiva en Python y OpenGL para el curso de Computación Visual. El proyecto convierte el contenido del sílabo en un parque de diversiones explorable: primero se construye y analiza en un laboratorio 2D, y luego se recorre como escena 3D.

## Qué incluye

- **Parque 3D:** montaña rusa ampliada con curvas en S, pendientes, peraltes y tres vagones. La rueda tiene doce cabinas y el carrusel, ocho caballos. El recorrido rodea las atracciones y pasa por encima del acceso peatonal.
- **Laboratorio 2D:** edición en planta y altura de la B-spline, perfil de elevación en vivo y demostraciones de Graham, recorte, rasterización, curvas y matrices homogéneas.
- **Renderizado:** cámaras orbital y en primera persona desde las tres atracciones, modo inmersivo, proyecciones, mapeado UV, iluminación día/noche y sombras direccionales.
- **Ruta de aprendizaje:** una pantalla vincula las 16 semanas con su evidencia dentro de la aplicación.

## Ejecutar en Windows

Se requiere Python y un controlador con un perfil OpenGL de compatibilidad. La versión comprobada usa Python 3.12 en Windows y una ventana creada con Pygame/SDL.

Desde la raíz del repositorio, ejecuta en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

También se puede ejecutar con `python -m park3d`.

## Controles principales

| Tecla o acción | Resultado |
|---|---|
| `P`, `E`, `A`, `H` | Parque 3D, editor 2D, ruta de las 16 semanas y ayuda. |
| Clic en una atracción o `1`, `2`, `3` | Seleccionar montaña rusa, rueda o carrusel. |
| `C` / `Tab` | Subir o bajar de la atracción seleccionada. Con Tab, cambiar de cabina o caballo. |
| Arrastrar / rueda del ratón | Orbitar y hacer zoom desde fuera. A bordo, arrastrar para mover la mirada. |
| `F11` / `Inicio` | Ocultar o recuperar los paneles. Con Inicio, volver a la vista general. |
| `Espacio`, `−` y `+` | Pausa y ajuste de velocidad del tren. |
| `T`, `L`, `O`, `M` | Texturas, día/noche, proyección y malla. |
| `Z`, `G` | Comparar profundidad y sombreado plano/suave. |
| Clic en editor | Añadir punto para la cápsula convexa. |
| Arrastrar punto ámbar / `[` y `]` en el editor | Editar la B-spline en planta o ajustar la altura del punto seleccionado. |
| `B`, `X`, `V`, `F`, `R` | Cambiar capa del editor o transformación, mostrar recorte, alternar suavizado o restaurar el plano. |

Consulta el mapeo completo en [docs/coverage.md](docs/coverage.md).

## Organización del repositorio

| Ruta | Contenido |
|---|---|
| `main.py` | Punto de entrada de la aplicación. |
| `park3d/app.py` | Bucle de eventos e interacción del usuario. |
| `park3d/geometry/` | Rasterización, Graham, recorte, Bézier, B-spline y matrices homogéneas. |
| `park3d/scene/` | Estado, animación y plano lógico del parque. |
| `park3d/scenery/` y `park3d/rides/` | Paisaje, arquitectura y modelos animados de las atracciones. |
| `park3d/rendering/` | Ventana OpenGL, interfaz, iluminación, mallas y dibujo de la escena. |
| `docs/` | Cobertura de las 16 semanas y guía técnica. |

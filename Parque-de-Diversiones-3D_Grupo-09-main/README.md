# Mirador del Valle · Parque Visual 3D

Aplicación interactiva en Python y OpenGL para el curso de Computación Visual. El proyecto convierte el contenido del sílabo en un parque de diversiones explorable: primero se construye y analiza en un laboratorio 2D, y luego se recorre como escena 3D.

## Qué incluye

- **Parque 3D:** tren de tres vagones sobre rieles tubulares, rueda con doce cabinas y carrusel de caballos. El terreno incorpora senderos, fuente animada, kioscos, jardín, faroles y un túnel peatonal abovedado.
- **Laboratorio 2D:** edición de la B-spline con el ratón y demostraciones de Graham, recorte, rasterización, curvas y matrices homogéneas.
- **Renderizado:** cámaras orbital, a bordo y por atracción, proyecciones, mapeado UV, iluminación día/noche, sombras direccionales y modos de diagnóstico.
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
| Arrastrar / rueda | Orbitar y acercar la cámara en la vista 3D. |
| Clic en una atracción / `Inicio` | Acercar la cámara a una atracción o recuperar la vista general. |
| `C`, `Espacio`, `−` y `+` | Cámara a bordo, pausa y velocidad del vagón. |
| `T`, `L`, `O`, `M` | Texturas, día/noche, proyección y malla. |
| `Z`, `G` | Comparar profundidad y sombreado plano/suave. |
| Clic en editor | Añadir punto para la cápsula convexa. |
| Arrastrar punto ámbar | Modificar la trayectoria B-spline de la montaña rusa. |
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

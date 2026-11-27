# Mirador del Valle — Computación Visual

Aplicación interactiva en Python, Pygame y OpenGL que reúne demostraciones de geometría 2D, modelado 3D y renderizado en un parque de diversiones explorable. El proyecto se organiza para que el código de los algoritmos se pueda estudiar aparte del código que dibuja la escena.

## Qué puedes explorar

- **Editor de geometría:** cápsula convexa con Graham, rasterización de líneas y circunferencias, recorte Cohen–Sutherland, curvas Bézier/B-spline/Koch y transformaciones homogéneas.
- **Matrices 3D:** operaciones 4 × 4 de traslación, rotación, escala y composición aplicadas a un cubo de demostración.
- **Color:** conversión entre RGB y HSV con muestras visibles.
- **Parque 3D:** montaña rusa sobre una B-spline editable, rueda panorámica, carrusel, arquitectura, terreno y visitantes animados.
- **Renderizado:** cámaras orbitales y a bordo, proyección en perspectiva u ortográfica, prueba de profundidad, sombreado plano o suave, luces, sombras, coordenadas UV y texturas.
- **Mapa del curso:** pantalla con las 16 semanas y la evidencia asociada a cada tema. El mapeo detallado está en [`docs/coverage.md`](docs/coverage.md).

## Requisitos

- Windows 10/11 recomendado.
- Python 3.12 recomendado.
- Controlador gráfico que permita abrir un contexto OpenGL de compatibilidad.
- Pygame, PyOpenGL, PyOpenGL-accelerate y NumPy, instalados desde `requirements.txt`.

La aplicación usa funciones del perfil de compatibilidad de OpenGL. Un controlador que solo ofrezca un perfil Core puede impedir que la ventana dibuje correctamente.

## Instalación y ejecución en Windows

Abre PowerShell en la raíz de este proyecto y ejecuta:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

También puedes iniciar el paquete con:

```powershell
.\.venv\Scripts\python.exe -m park3d
```

En macOS o Linux, crea el entorno virtual con `python3 -m venv .venv`, actívalo, instala `requirements.txt` y ejecuta `python main.py`. Se necesita igualmente un entorno gráfico con OpenGL compatible.

## Controles

### Navegación

| Tecla o acción | Resultado |
|---|---|
| `P` | Abrir el parque 3D. |
| `E` | Abrir el editor de geometría. |
| `A` | Abrir el mapa de semanas del curso. |
| `H` | Abrir ayuda y diagnóstico gráfico. |
| `Esc` | Salir del modo inmersivo, bajar de una atracción o cerrar la aplicación. |

### Parque 3D

| Tecla o acción | Resultado |
|---|---|
| Clic en una atracción o `1`, `2`, `3` | Enfocar montaña rusa, rueda o carrusel. |
| `C` | Subir a la atracción enfocada o bajar de ella. |
| `Tab` | Cambiar de cabina o caballo cuando estás a bordo. |
| Arrastrar con el ratón | Orbitar la cámara; a bordo, cambiar la dirección de la mirada. |
| Rueda del ratón | Acercar o alejar la cámara exterior. |
| `Inicio` | Volver a la vista general. |
| `Espacio` | Pausar o reanudar la simulación. |
| `−` / `+` | Reducir o aumentar la velocidad de la montaña rusa. |
| `T` | Alternar entre texturas y color plano. |
| `L` | Alternar entre iluminación de día y de noche. |
| `O` | Alternar entre perspectiva y proyección ortográfica. |
| `M` | Alternar entre sólidos y vista de malla. |
| `Z` | Activar o desactivar la prueba de profundidad. |
| `G` | Alternar sombreado suave y plano. |
| `F11` o `I` | Entrar o salir del modo inmersivo. |

### Editor

| Tecla o acción | Resultado |
|---|---|
| `B` | Cambiar entre Plano, Rasterización, Curvas, Matrices 2D, Matrices 3D y Color RGB / HSV. |
| `X` | Cambiar la operación de transformación de la capa activa. |
| `V` o `C` | Mostrar u ocultar la demostración de recorte. |
| `F` | Alternar el suavizado de la línea de cobertura. |
| Clic en el plano | Añadir un punto a la envolvente convexa cuando está activa la capa Plano. |
| Arrastrar un punto ámbar | Editar un punto de control del circuito. |
| `[` / `]` | Bajar o subir la altura del punto seleccionado. |
| `R` | Restaurar los datos del editor. |

## Relación con el sílabo

| Semanas | Contenido que se puede demostrar |
|---|---|
| 1–2 | Fundamentos gráficos, hardware, objetos 2D y envolvente de Graham. |
| 3–4 | Rasterización, atributos de primitivas, relleno y antialiasing. |
| 5–7 | Transformaciones 2D y 3D, cámara y proyecciones. |
| 8 | Integración del editor y recorte como actividad de enlace. |
| 9–10 | Curvas, continuidad, Bézier, B-spline, mallas y curvas fractales. |
| 11–12 | Representación de fronteras y una demostración geométrica de diferencia de perfiles extruidos. |
| 13–15 | Visibilidad, texturas UV, iluminación, sombreado y color RGB/HSV. |
| 16 | Recorrido de cierre con las evidencias integradas. |

El cronograma del sílabo adjunto enumera temas en las semanas 1–7 y 9–15; las semanas 8 y 16 de esta tabla son actividades de integración de la aplicación. La cobertura y sus alcances están descritos en [`docs/coverage.md`](docs/coverage.md).

## Organización del código

```text
main.py                       Punto de entrada
park3d/app.py                 Eventos y coordinación entre modelo y vistas
park3d/geometry/              Algoritmos geométricos sin dependencias de OpenGL
park3d/scene/                 Estado, trayectorias y animación del parque
park3d/rides/                 Geometría y pose de las atracciones
park3d/scenery/               Terreno, arquitectura y elementos del entorno
park3d/rendering/             Cámara, interfaz, editor y renderizado OpenGL
park3d/assets.py              Carga de imágenes para texturas OpenGL
assets/textures/              Texturas distribuidas con el proyecto
docs/                         Cobertura del sílabo y documentación técnica
```

Consulta [`docs/architecture.md`](docs/architecture.md) para las responsabilidades de cada capa. La carpeta `park3d/geometry/` contiene módulos temáticos; [`algorithms.py`](park3d/geometry/algorithms.py) conserva una fachada para los imports existentes.

## Evidencias y entregables académicos

La aplicación es una evidencia ejecutable del proyecto. El curso también evalúa un informe de proyecto y trabajos colaborativos. Esos documentos, capturas, división de tareas y presentación del equipo deben adjuntarse por separado según la consigna del docente; el repositorio no los genera automáticamente.

## Solución de problemas

- **La ventana no abre:** confirma que Python y Pygame se ejecuten desde una sesión de escritorio, no desde una consola sin pantalla.
- **Error al crear el contexto OpenGL:** actualiza el controlador de video y comprueba que la tarjeta admita OpenGL de compatibilidad.
- **Pantalla en negro o elementos ausentes:** prueba `H` para revisar la versión y el dispositivo OpenGL; desactiva `M`, `Z`, `T` o `L` para aislar el modo gráfico que causa el problema.
- **Falta una textura:** verifica que `assets/textures/brick_sample.png` exista. El paisaje conserva materiales procedurales de respaldo para el ladrillo.
- **La aplicación no encuentra módulos:** ejecuta `main.py` desde la raíz del proyecto o inicia con `python -m park3d` desde esa misma carpeta.

## Documentación adicional

- [`park3d/geometry/README.md`](park3d/geometry/README.md): algoritmos, matrices y modelos de color.
- [`park3d/rendering/README.md`](park3d/rendering/README.md): ciclo de renderizado, cámara y controles visuales.
- [`assets/README.md`](assets/README.md): recursos gráficos.
- [`docs/README.md`](docs/README.md): guía para navegar la documentación del proyecto.

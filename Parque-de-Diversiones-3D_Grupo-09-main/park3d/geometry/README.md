# Geometría

Esta carpeta contiene cálculos matemáticos reutilizables por el editor y la escena. Sus módulos no dependen de Pygame ni de OpenGL; devuelven coordenadas, píxeles o matrices para que otra capa decida cómo dibujarlos.

## Módulos

| Archivo | Responsabilidad |
|---|---|
| `raster.py` | Línea básica, DDA, Bresenham, cobertura de píxel, Bresenham de circunferencia y punto medio. |
| `hull.py` | Producto cruzado y envolvente convexa con Graham. |
| `clipping.py` | Recorte de segmentos mediante Cohen–Sutherland. |
| `curves.py` | Evaluación y muestreo de Bézier y B-spline; curva fractal de Koch. |
| `transforms.py` | Matrices homogéneas 3 × 3 para operaciones 2D. |
| `transforms3d.py` | Matrices homogéneas 4 × 4 para traslación, escala, rotación y transformación de puntos 3D. |
| `color_models.py` | Conversión entre RGB y HSV. |
| `algorithms.py` | Fachada retrocompatible que reexporta las funciones geométricas usadas por el resto del proyecto. |

## Ejemplos

```python
from park3d.geometry.transforms3d import rotation_y, transform_point

rotated = transform_point((1.0, 0.0, 0.0), rotation_y(90))
```

```python
from park3d.geometry.color_models import hsv_to_rgb, rgb_to_hsv

rgb = hsv_to_rgb((210, 0.65, 0.9))
hsv = rgb_to_hsv(rgb)
```

RGB usa tres canales normalizados de `0.0` a `1.0`. HSV expresa el tono en grados y mantiene saturación y valor normalizados en ese mismo intervalo.

## Convenciones

- Las funciones de este paquete no dibujan y no crean ventanas.
- Los puntos 2D se representan como `(x, y)`; en el plano del parque se interpreta el segundo valor como coordenada horizontal `z`.
- Las matrices transforman vectores columna homogéneos; el orden de composición afecta el resultado.
- `algorithms.py` se conserva para que los módulos existentes puedan migrar gradualmente a imports más específicos.

# Cobertura del sílabo en Parque Visual 3D

Esta tabla sirve como guía de demostración e informe: cada concepto no sólo se menciona, sino que tiene una evidencia observable en la aplicación.

| Semana | Tema | Evidencia en el proyecto |
|---:|---|---|
| 1 | Evolución, impacto y hardware gráfico | `H` muestra GPU, versión de OpenGL y aplicaciones de las técnicas. |
| 2 | Objetos 2D, cápsula convexa, Graham | Plano interactivo y perímetro turquesa que se recalcula al hacer clic. |
| 3 | Rasterización, DDA/Bresenham, punto medio | `B` cambia a Rasterización, donde se comparan tres métodos de línea y dos de circunferencia. |
| 4 | Color, relleno, grosor, aliasing | Relleno de la envolvente, grosores de las capas y comparación con `F` del suavizado por cobertura. |
| 5 | Transformaciones 2D, homogéneas | `X` muestra y aplica matrices de traslación, rotación, escala, reflexión y cizalla. |
| 6 | Transformaciones 3D, cámara, volumen | Cámara orbital, cámara a bordo y matrices OpenGL. |
| 7 | Proyecciones | Tecla `O`: perspectiva u ortográfica. |
| 8 | Integración Unidad I | Modo Editor 2D, demostración y control de recorte. |
| 9 | Curvas, superficies, continuidad | B-spline cúbica cerrada de la montaña rusa. |
| 10 | Mallas, Bézier y otras curvas | Senderos Bézier, terreno mallado y fractal de Koch en la capa Curvas. |
| 11 | B-Rep | Casetas y entrada compuestas por vértices, aristas y caras. |
| 12 | CSG | Bóveda de ladrillo generada directamente como la frontera de la diferencia de dos perfiles extruidos. |
| 13 | Ocultamiento | Comparación del Z-buffer con `Z`, descarte de caras posteriores y modo de malla con `M`. |
| 14 | Mapeado y texturas | Mapas de bits procedurales para césped, pavimento y ladrillo, coordenadas UV y tecla `T`. |
| 15 | Iluminación, sombreado y color | Luz ambiental, difusa y especular, color RGB, faroles, sombras planares y controles `G` y `L`. |
| 16 | Cierre | Temario de la aplicación y guion para la demostración integrada. |

## Guion recomendado para la demostración

1. Abrir el mapa de aprendizaje con `A` y explicar la cobertura.
2. Entrar con `E`; añadir puntos, mostrar Graham, Bresenham, punto medio y activar `V`.
3. Arrastrar un punto ámbar para probar que la B-spline se recalcula.
4. Volver con `P`; recorrer el parque y usar `C`, `O`, `M`, `T` y `L`.
5. Mostrar cómo el túnel (CSG), las casetas (B-Rep) y la textura/iluminación representan las unidades II y III.

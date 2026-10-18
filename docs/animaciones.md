# Cómo se hicieron las animaciones

Casi todo lo visual sale de código chico y de datos. El deck y el video comparten las mismas láminas.

| Pieza | Con qué |
|---|---|
| Las 7 láminas del video y la de validación | Manim, sobre el motor de animación nemaxyz |
| La pantalla del trato (maqueta del flujo) | Remotion |
| La voz | Voz sintética de Microsoft Edge TTS (es-BO-MarceloNeural) |
| La música | Sintetizada por el motor, un clima por escena |
| La mezcla y las uniones | ffmpeg |
| El PDF del deck | Las imágenes finales de cada lámina, unidas con Pillow |

## El motor no está en este repo

El motor de animación (`nemaxyz-motor`: estilo, auditores, síntesis de música) es un repositorio privado y no se incluye. Las láminas lo usan a través de la variable de entorno `NEMAXYZ_MOTOR`, que apunta a su carpeta. Lo que está acá son las láminas y el orquestador; los videos ya renderizados están en [`video/`](../video/).

## Cada imagen dura lo que dura su frase

El texto hablado vive en [`animaciones/guion.py`](../animaciones/guion.py), una línea por beat visual. Primero se sintetiza la voz y se mide cuánto dura cada frase. Después cada lámina deja cada imagen en pantalla exactamente ese tiempo. Así la voz nunca habla de algo que ya salió de cuadro. Si se cambia una frase, se regenera todo.

## Para volver a generarlo

Hace falta Python 3.13 con `manim`, `edge-tts`, `pydub` y `Pillow`; Node 22 o más nuevo; ffmpeg; y el motor.

```bash
cd animaciones/remotion && npm install && cd ../..
export NEMAXYZ_MOTOR=/ruta/a/nemaxyz-motor
python animaciones/producir_pitch.py            # todas las etapas
python animaciones/producir_pitch.py deck       # solo el deck
```

Las etapas son `voz`, `laminas`, `flujo`, `video`, `mezcla` y `deck`. El trabajo intermedio va a una carpeta corta (`QHATU_TRABAJO`, por defecto `~/qh`), porque Windows corta las rutas de más de 260 caracteres.

## Lo que se cambia sin tocar código

[`datos/proyecto.json`](../datos/proyecto.json) tiene el equipo, la cantidad de entrevistas y su hallazgo, y los hashes de las transacciones de testnet. Cuando existan transacciones reales, se escriben ahí, se cambia `estado` a `real` y se vuelve a correr: la maqueta pasa a mostrar la red de pruebas y el relato del video cambia de «maqueta» a «lo que pasó».

## Una voz propia

La voz sintética es un borrador honesto. Para usar una voz humana: el video sin voz (`qhatu-pitch-3min_SIN_VOZ.mp4`) tiene solo música, y [`video/guion.md`](../video/guion.md) trae cada frase con su tiempo y quién la lee.

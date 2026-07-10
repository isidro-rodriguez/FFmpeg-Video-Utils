# ffmpeg-utils.py

## Resumen

ffmpeg-utils.py es un script en Python 3 que ofrece utilidades sencillas para manipular vídeos usando FFmpeg/FFprobe. Permite:

- Recortar bordes.
- Reducir la resolución.
- Dividir un vídeo en segmentos.
- Unir varios vídeos en uno solo.

El script está pensado para uso local desde la línea de comandos.

## Requisitos

- Python 3.8+ (o superior)
- ffmpeg y ffprobe en PATH (disponibles desde <https://ffmpeg.org>)

## Instalación

1. Asegurarse de tener Python 3 instalado.
2. Instalar FFmpeg y comprobar que "ffmpeg" y "ffprobe" estén accesibles desde la terminal.
3. Clonar o descargar este repositorio.

## Uso

Desde la carpeta del proyecto, ejecutar:

```bash
    python ffmpeg-utils.py video1.mp4 [video2.mp4 ...]
```

El script acepta uno o varios archivos de vídeo como argumentos. Después de iniciar mostrará un menú interactivo con las operaciones disponibles en función del número de vídeos proporcionados.

## Operaciones disponibles

- Recortar (opción 1):
  - Elimina píxeles de los bordes del vídeo(s) especificando 4 números separados por comas: izquierda,derecha,arriba,abajo
  - Ejemplo: si quieres quitar 10px izquierda, 10px derecha, 20px arriba y 20px abajo, introducir "10,10,20,20".
  - Genera archivos con sufijo `.crop.mp4`.

- Reducir resolución (opción 2):
  - Permite elegir entre 1440p, 1080p o 720p.
  - Si la resolución de origen es menor o igual que la seleccionada, se deja sin cambios.
  - El script intenta reutilizar un códec equivalente al del archivo de entrada (mapa interno CODECS). Si el códec no está en la lista, se usa libx264 por defecto.
  - Genera un archivo con sufijo indicando la nueva altura (por ejemplo: `video.720p.mp4`).

- Dividir vídeo en segmentos (opción 3):
  - Solo funciona si se pasa un único vídeo como argumento.
  - Pide una lista de tiempos de corte en formato `HH:MM:SS` separados por comas.
  - Valida el formato y que los tiempos queden dentro de la duración del vídeo.
  - Usa el demuxer de segmentación de FFmpeg y mantiene códecs con "-c copy".
  - Salida: archivos nombrados como `video_00.ext`, `video_01.ext`, ...

- Unir vídeos (opción 4):
  - Solo para unir múltiples archivos. Pide el nombre de salida (por defecto VIDEO_UNIDO).
  - Crea un archivo temporal con la lista de rutas (compatibilidades de ruta para FFmpeg) y ejecuta `ffmpeg -f concat -safe 0 -i list.txt -c copy output`
  - Todos los vídeos deben ser compatibles (mismo códec, resolución, FPS, pistas de audio) para que la concatenación sin recodificación funcione correctamente.

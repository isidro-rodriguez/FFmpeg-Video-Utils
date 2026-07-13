import os
import subprocess
from src.utils import mostrar_error, mostrar_exito

# ------------------------------------------------------------
# Recortar vídeos
# ------------------------------------------------------------
# Se recortan píxeles de los bordes del vídeo.
# Se pide al usuario que introduzca cuatro números separados por comas, que
# representan los píxeles a eliminar de la izquierda, derecha, arriba y abajo.

def recortar(videos):

    print("\n=== RECORTAR VÍDEOS ===\n")

    entrada = input(
        "Píxeles a eliminar (izquierda, derecha, arriba, abajo): "
    )

    try:
        valores = entrada.split(",")

        if len(valores) != 4:
            raise ValueError

        izquierda, derecha, arriba, abajo = map(int, valores)

    except ValueError:
        mostrar_error("Debe introducir cuatro números separados por comas.")
        recortar(videos)

    for video in videos:
        nuevo_ancho = video["ancho"] - izquierda - derecha
        nuevo_alto = video["alto"] - arriba - abajo

        if nuevo_ancho <= 0 or nuevo_alto <= 0:
            mostrar_error(f"{video}: recorte inválido.")
            continue

        salida = video['nombre'] + ".cortado." + video['extension']

        comando = [
            "ffmpeg",
            "-i", video['ruta'],
            "-vf",
            f"crop={nuevo_ancho}:{nuevo_alto}:{izquierda}:{arriba}",
            "-c:a", "copy",
            salida
        ]

        print("\nEjecutando:")
        print(" ".join(comando))
        print()

        subprocess.run(comando)

        mostrar_exito(f"{video}: recortado a {nuevo_ancho}x{nuevo_alto}.")
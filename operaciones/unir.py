import os
import subprocess
import tempfile

from src.utils import mostrar_exito, mostrar_error

# ------------------------------------------------------------
# Unir vídeos
# ------------------------------------------------------------

def unir(videos):

    salida = input("Nombre del archivo de salida [VIDEO_UNIDO]: ").strip()

    if salida == "":
        salida = "VIDEO_UNIDO"

    # Crear archivo temporal con la lista de vídeos
    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        suffix=".txt",
        encoding="utf-8"
    ) as lista:

        for video in videos:
            ruta = video['ruta'].replace("\\", "/")
            lista.write(f"file '{ruta}'\n")

        lista_txt = lista.name
        
    comando = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", lista_txt,
        "-c", "copy",
        f"{salida}.mp4"
    ]


    try:
        subprocess.run(comando, check=True)
        mostrar_exito(f"\nVídeo generado: {salida}")
    except subprocess.CalledProcessError:
        mostrar_error(
        "Error al unir los vídeos.\n" \
        "Probablemente no tienen el mismo formato.\n" \
        "Todos deben tener el mismo códec, resolución, FPS y pistas de audio." \
        )

    finally:
       os.remove(lista_txt)
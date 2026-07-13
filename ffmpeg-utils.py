#!/usr/bin/env python3

import os
import subprocess
import sys
import tempfile

from src.constants import CODECS

# Importar funciones utilitarias
from src.utils import (
    mostrar_error,
    mostrar_exito,
    mostrar_desactivado,
    mostrar_info,
    obtener_info_video,
    segundos_a_hms,
    hms_a_segundos,
    validar_hora
)

import operaciones.recortar as recortar

# =============================================================================
# Variables globales
# =============================================================================

# Almacenar información de los vídeos en una lista
video_info = []

# =============================================================================
# Funciones principales
# =============================================================================

# ------------------------------------------------------------
# Mostrar menú
# ------------------------------------------------------------

def mostrar_menu(num_videos):
    print("\n========================================")
    print("          FFmpeg Video Utils")
    print("========================================\n")

    print("1. Recortar")
    print("2. Reducir resolución")
    print("3. Rotar")
        
    if num_videos == 1:
        print("3. Dividir en segmentos")
    else:
        mostrar_desactivado("3. Dividir en segmentos")

    if num_videos > 1:
        print("4. Unir múltiples vídeos")
    else:
        mostrar_desactivado("4. Unir múltiples vídeos")

    print("----------------------------------------")
    print("Q. Salir\n")
    
# ------------------------------------------------------------
# 2. Reducir resolución
# ------------------------------------------------------------

def reducir_resolucion(videos):

    # Dar la opción al usuario de elegir entre h264 o h265

    for video in videos:
        mostrar_info(f"{video} : {video_info['ancho']}x{video_info['alto']} , {video_info['codec']}")

    print("\n=== Elegir códec ===\n")

    print("1. Mantener códec original")
    print("2. H.264")
    print("3. H.265")

    opcion = input("Seleccione el códec (1): ").strip()
    
    match opcion:
        case "1":
            codec_target = None
        case "2":
            codec_target = "libx264"
        case "3":
            codec_target = "libx265"
        case "":
            codec_target = None
        case _:
            mostrar_error("Opción no válida.")
            return

    print("\n=== Reducir resolución ===\n")

    print("1. 1440")
    print("2. 1080")
    print("3. 720")

    opcion = input("Resolución destino: ").strip()

    match opcion:
        case "1":
            altura = 1440
        case "2":
            altura = 1080
        case "3":
            altura = 720
        case _:
            print("Opción no válida.")
            return
    
    for video in videos:
            
            salida = f"{video_info['nombre']}.{altura}p{video_info['extension']}"

            if altura >= video_info["alto"]:
                mostrar_info(f"{video}: resolución original {video_info['ancho']}x{video_info['alto']}, no se puede reducir a {altura}.")
                continue

            if codec_target is None:
                if CODECS.get(video_info['codec']) is not None:
                    codec_target = video_info['codec']
                else:  
                    mostrar_info(f"Códec '{video_info['codec']}' no soportado. Se utilizará H.264.")
                    codec_target = "libx264"
                    
            comando = [
                "ffmpeg",
                "-i", video,
                "-vf", f"scale=-2:{altura}",
                "-c:v", codec_target,
                "-crf", "18",
                "-preset", "medium",
                "-c:a", "copy",
                salida
            ]

            subprocess.run(comando)
            
            mostrar_exito(f"{video}: reduciendo a {altura}...")

# ------------------------------------------------------------
# 3. Rotar vídeos
# ------------------------------------------------------------

def rotar(videos):

    print("\n=== ROTAR VÍDEOS ===\n")

    print("1. 90°")
    print("2. 180°")
    print("3. 270°")

    opcion = input("Seleccione la rotación: ").strip()

    match opcion:
        case "1":
            filtro = "transpose=1"
        case "2":
            filtro = "transpose=2,transpose=2"
        case "3":
            filtro = "transpose=2"
        case _:
            mostrar_error("Opción no válida.")
            return

    for video in videos:

        salida = f"{video_info['nombre']}_rotado{video_info['extension']}"

        comando = [
            "ffmpeg",
            "-i", video,
            "-vf", filtro,
            "-c:a", "copy",
            salida
        ]

        subprocess.run(comando)

        mostrar_exito(f"{video}: rotado.")

# ------------------------------------------------------------
# 4. Dividir vídeo en segmentos
# ------------------------------------------------------------

def dividir_video(videos):

    mostrar_info(f"Duración del vídeo: {segundos_a_hms(video_info[0]['duracion'])}")

    entrada = input("Puntos de corte (HH:MM:SS,HH:MM:SS,...): ")
    tiempos = entrada.strip().split(",")

    cortes = []

    for t in tiempos:

        if not validar_hora(t, video_info[0]['duracion']):
            mostrar_error(f"ERROR: hora inválida: {t}")
            return

        cortes.append(hms_a_segundos(t))

    cortes = sorted(set(cortes))

    comando = [
            "ffmpeg",
            "-i", videos[0],
            "-c", "copy",
            "-f", "segment",
            "-segment_times", ",".join(str(t) for t in cortes),
            "-reset_timestamps", "1",
            f"{video_info[0]['nombre']}_%02d{video_info[0]['extension']}"
        ]

    subprocess.run(comando)

    mostrar_exito("\nVídeo dividido.")

# ------------------------------------------------------------
# 5. Unir vídeos
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
            ruta = os.path.abspath(video).replace("\\", "/")
            lista.write(f"file '{ruta}'\n")

        lista_txt = lista.name

    comando = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", lista_txt,
        "-c", "copy",
        f"{salida}{video_info[0]['extension']}"
    ]

    try:
        subprocess.run(comando, check=True)
        mostrar_exito(f"\nVídeo generado: {salida}")
    except subprocess.CalledProcessError:
        mostrar_error(
        "Error al unir los vídeos." \
        "Probablemente no tienen el mismo formato." \
        "Todos deben tener el mismo códec, resolución, FPS y pistas de audio." \
        )

    finally:
        os.remove(lista_txt)

# =============================================================================
# Programa principal
# =============================================================================

def main():

    # Recoger argumentos
    videos = sys.argv[1:]

    if (len(videos) == 0):
        mostrar_error("No hay vídeos con los que trabajar.")
        mostrar_info("Uso: python ffmpeg-utils.py video1.mp4 video2.mp4 ...")
        exit(1)

    # Comprobar existencia
    for video in videos:
        if not os.path.isfile(video):
            mostrar_error(f"No existe: {video}")
            sys.exit(1)
    
    # Obtener información de los vídeos
    for video in videos:
        info = obtener_info_video(video)
        video_info.append(info)

    while True:

        mostrar_menu(len(videos))

        opcion = input("Seleccione una opción: ").strip().upper()

        match opcion:

            case "1":
                recortar(video_info)

            case "2":
                reducir_resolucion(videos)
            
            case "3":
                rotar(videos)

            case "4":        
                if len(videos) != 1:
                    mostrar_error("ERROR: Esta operación sólo admite un vídeo.")
                    return
                dividir_video(videos)

            case "5":        
                if len(videos) < 2:
                    mostrar_error("ERROR: Esta operación sólo se admite para múltipless vídeos.")            
                unir(videos)

            case "Q":
                print("\nHasta luego.")
                break

            case _:
                mostrar_error("\nOpción no válida.\n")


if __name__ == "__main__":
    main()
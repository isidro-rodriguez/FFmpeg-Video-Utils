#!/usr/bin/env python3

import os
import sys

from src.utils import (
    mostrar_error,
    mostrar_desactivado,
    mostrar_info,
    obtener_info_video,
)

from operaciones.dividir import dividir
from operaciones.recortar import recortar
from operaciones.reducir_resolucion import reducir_resolucion
from operaciones.rotar import rotar
from operaciones.unir import unir


# =============================================================================
# Variables globales
# =============================================================================

# Almacenar información de los vídeos en una lista
video_info = []

# =============================================================================
# Mostrar Menú
# =============================================================================

def mostrar_menu(num_videos):
    print("\n========================================")
    print("          FFmpeg Video Utils")
    print("========================================\n")

    print("1. Recortar")
    print("2. Reducir resolución")
    print("3. Rotar")
        
    if num_videos == 1:
        print("4. Dividir en segmentos")
    else:
        mostrar_desactivado("4. Dividir en segmentos")

    if num_videos > 1:
        print("5. Unir múltiples vídeos")
    else:
        mostrar_desactivado("5. Unir múltiples vídeos")

    print("----------------------------------------")
    print("Q. Salir\n")

# =============================================================================
# Programa principal
# =============================================================================

def main():

    # Recoger argumentos
    video_list = sys.argv[1:]

    if (len(video_list) == 0):
        mostrar_error("No hay vídeos con los que trabajar.")
        mostrar_info("Uso: python ffmpeg-utils.py video1.mp4 video2.mp4 ...")
        exit(1)

    # Comprobar existencia
    for video in video_list:
        if not os.path.isfile(video):
            mostrar_error(f"No existe: {video}")
            sys.exit(1)
    
    # Obtener información de los vídeos
    for video in video_list:
        info = obtener_info_video(video)
        video_info.append(info)

    while True:

        mostrar_menu(len(video_list))

        opcion = input("Seleccione una opción: ").strip().upper()

        match opcion:

            case "1":
                recortar(video_info)

            case "2":
                reducir_resolucion(video_info)
            
            case "3":
                rotar(video_info)

            case "4":        
                if len(video_list) != 1:
                    mostrar_error("ERROR: Esta operación sólo admite un vídeo.")
                    return
                dividir(video_info)

            case "5":        
                if len(video_list) < 2:
                    mostrar_error("ERROR: Esta operación sólo se admite para múltipless vídeos.")     
                    return       
                unir(video_info)

            case "Q":
                print("\nHasta luego.")
                break

            case _:
                mostrar_error("\nOpción no válida.\n")


if __name__ == "__main__":
    main()
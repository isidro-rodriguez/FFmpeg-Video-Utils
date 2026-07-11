#!/usr/bin/env python3

import os
import subprocess
import sys
import tempfile

# =============================================================================
# Índice de contenidos
# ============================================================================
# 1. Colores ANSI
# 2. Funciones utilitarias
# 3. Funciones principales
# 4. Programa principal

# =============================================================================
# Constantes
# =============================================================================

RESET = "\033[0m"

ERROR = "\033[91m"      # Rojo claro
SUCCESS = "\033[92m"    # Verde claro
DISABLED = "\033[90m"   # Gris oscuro
INFO = "\033[94m"       # Azul claro

CODECS = {
    "h264": "libx264",
    "hevc": "libx265",
    "h265": "libx265",
    "av1": "libsvtav1",
    "vp9": "libvpx-vp9",
    "vp8": "libvpx",
    "mpeg4": "mpeg4",
    "mpeg2video": "mpeg2video",
}

# =============================================================================
# Funciones utilitarias
# =============================================================================

# Limpiar pantalla
def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")

# Mostrar mensajes de error, éxito, desactivado e información
def mostrar_error(texto):
    limpiar_pantalla()
    print(f"{ERROR}{texto}{RESET}\n")

def mostrar_exito(texto):
    print(f"{SUCCESS}{texto}{RESET}\n")

def mostrar_desactivado(texto):
    print(f"{DISABLED}{texto}{RESET}")

def mostrar_info(texto):
    print(f"\n{INFO}{texto}{RESET}\n")

# Función para obtener la resolución de un vídeo
def obtener_resolucion(video):

    resultado = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0:s=x",
            video
        ],
        capture_output=True,
        text=True
    )

    ancho, alto = resultado.stdout.strip().split("x")

    return int(ancho), int(alto)

# Función para obtener el codec de un vídeo
def obtener_codec(video):

    comando = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_name",
        "-of", "csv=p=0",
        video
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True
    )

    return resultado.stdout.strip()

# Función para obtener la duración de un vídeo en segundos
def obtener_duracion(video):

    comando = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True
    )

    return int(float(resultado.stdout.strip()))

# Función para convertir segundos a formato HH:MM:SS
def segundos_a_hms(segundos):

    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60

    return f"{h:02}:{m:02}:{s:02}"

# Función para convertir formato HH:MM:SS a segundos
def hms_a_segundos(texto):

    h, m, s = map(int, texto.split(":"))

    return h * 3600 + m * 60 + s

# Función para validar punto de corte en formato HH:MM:SS
def validar_hora(tiempo, duracion):

    h, m, s = map(int, tiempo.split(":"))
    if h < 0 or m < 0 or m >= 60 or s < 0 or s >= 60 or s >= duracion: 
        return False
    try:
        s = hms_a_segundos(tiempo)
    except:
        return False
    return True

# =============================================================================
# Funciones principales
# =============================================================================

# ------------------------------------------------------------
# Mostrar menú
# ------------------------------------------------------------
# Como el menú depende del número de vídeos, se pasa como argumento.

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
# 1. Recortar vídeos
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

        # Obtener resolución
        resultado = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=p=0:s=x",
                video
            ],
            capture_output=True,
            text=True
        )

        ancho, alto = map(int, resultado.stdout.strip().split("x"))

        nuevo_ancho = ancho - izquierda - derecha
        nuevo_alto = alto - arriba - abajo

        if nuevo_ancho <= 0 or nuevo_alto <= 0:
            mostrar_error(f"{video}: recorte inválido.")
            continue

        salida = os.path.splitext(video)[0] + ".crop.mp4"

        comando = [
            "ffmpeg",
            "-i", video,
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
    
# ------------------------------------------------------------
# 2. Reducir resolución
# ------------------------------------------------------------

def reducir_resolucion(videos):

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

        ancho, alto = obtener_resolucion(video)

        if altura >= alto:
            mostrar_info(f"{video}: resolución original {ancho}x{alto}, no se puede reducir a {altura}.")
            continue
        
        else:
            codec_original = obtener_codec(video)

            codec_ffmpeg = CODECS.get(codec_original)

            if codec_ffmpeg is None:
                mostrar_info(f"Códec '{codec_original}' no soportado. Se utilizará H.264.")
                codec_ffmpeg = "libx264"

            nombre, extension = os.path.splitext(video)
    
            salida = f"{nombre}.{altura}p{extension}"

            comando = [
                "ffmpeg",
                "-i", video,
                "-vf", f"scale=-2:{altura}",
                "-c:v", codec_ffmpeg,
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

        nombre, extension = os.path.splitext(video)
        salida = f"{nombre}_rotado{extension}"

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

    video = videos[0]

    duracion = obtener_duracion(video)

    mostrar_info(f"Duración del vídeo: {segundos_a_hms(duracion)}")

    entrada = input("Puntos de corte (HH:MM:SS,HH:MM:SS,...): ")
    tiempos = entrada.strip().split(",")

    cortes = []

    for t in tiempos:

        if not validar_hora(t, duracion):
            mostrar_error(f"ERROR: hora inválida: {t}")
            return

        cortes.append(hms_a_segundos(t))

    cortes = sorted(set(cortes))

    nombre, extension = os.path.splitext(video)

    comando = [
            "ffmpeg",
            "-i", video,
            "-c", "copy",
            "-f", "segment",
            "-segment_times", ",".join(str(t) for t in cortes),
            "-reset_timestamps", "1",
            f"{nombre}_%02d{extension}"
        ]

    subprocess.run(comando)

    mostrar_exito("\nVídeo dividido.")

# ------------------------------------------------------------
# 5. nir vídeos
# ------------------------------------------------------------

def unir(videos):

    salida = input("Nombre del archivo de salida [VIDEO_UNIDO]: ").strip()
    nombre, extension = os.path.splitext(videos[0])

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
        f"{salida}{extension}"
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

    while True:

        mostrar_menu(len(videos))

        opcion = input("Seleccione una opción: ").strip().upper()

        match opcion:

            case "1":
                recortar(videos)

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
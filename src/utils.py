import os
import subprocess
from src.constants import ERROR, SUCCESS, DISABLED, INFO, RESET

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

# Función para obtener información completa de un vídeo
def obtener_info_video(video):

    ancho, alto = obtener_resolucion(video)
    codec = obtener_codec(video)
    duracion = obtener_duracion(video)
    nombre, extension = os.path.splitext(os.path.basename(video))

    return {
        'ruta': os.path.abspath(video),
        'nombre': nombre,
        'extension': extension,
        'ancho': ancho,
        'alto': alto,
        'codec': codec,
        'duracion': duracion
    }

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

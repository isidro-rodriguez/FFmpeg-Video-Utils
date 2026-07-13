import subprocess

from src.constants import CODECS
from src.utils import mostrar_info, mostrar_exito, mostrar_error

# ------------------------------------------------------------
# Reducir resolución
# ------------------------------------------------------------

def reducir_resolucion(videos):

    # Dar la opción al usuario de elegir entre h264 o h265
    for video in videos:
        mostrar_info(f"{video['nombre']} : {video['ancho']}x{video['alto']} , {video['codec']}")

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
            
            salida = f"{video['nombre']}.{altura}p{video['extension']}"

            if altura >= video['alto']:
                mostrar_info(f"{video['nombre']}: resolución original {video['ancho']}x{video['alto']}, no se puede reducir a {altura}.")
                continue

            if codec_target is None:
                if CODECS.get(video['codec']) is not None:
                    codec_target = video['codec']
                else:  
                    mostrar_info(f"Códec '{video['codec']}' no soportado. Se utilizará H.264.")
                    codec_target = "libx264"
                    
            comando = [
                "ffmpeg",
                "-i", video['ruta'],
                "-vf", f"scale=-2:{altura}",
                "-c:v", codec_target,
                "-crf", "18",
                "-preset", "medium",
                "-c:a", "copy",
                salida
            ]

            subprocess.run(comando)
            
            mostrar_exito(f"{video}: reduciendo a {altura}...")
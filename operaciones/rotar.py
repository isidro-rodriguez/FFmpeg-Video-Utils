import subprocess

from src.utils import mostrar_exito, mostrar_error

# ------------------------------------------------------------
# Rotar vídeos
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

        salida = f"{video['nombre']}_rotado{video['extension']}"

        comando = [
            "ffmpeg",
            "-i", video['ruta'],
            "-vf", filtro,
            "-c:a", "copy",
            salida
        ]

        subprocess.run(comando)

        mostrar_exito(f"{video['nombre']}: rotado.")
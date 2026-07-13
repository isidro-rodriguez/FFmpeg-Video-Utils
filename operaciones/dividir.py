import subprocess

from src.utils import mostrar_info, mostrar_exito, mostrar_error, segundos_a_hms, hms_a_segundos, validar_hora

# ------------------------------------------------------------
# Dividir vídeo en segmentos
# ------------------------------------------------------------

def dividir(videos):

    video = videos[0]

    mostrar_info(f"Duración del vídeo: {segundos_a_hms(video['duracion'])}")

    entrada = input("Puntos de corte (HH:MM:SS,HH:MM:SS,...): ")
    tiempos = entrada.strip().split(",")

    cortes = []

    for t in tiempos:

        if not validar_hora(t, video['duracion']):
            mostrar_error(f"ERROR: hora inválida: {t}")
            return

        cortes.append(hms_a_segundos(t))

    cortes = sorted(set(cortes))

    comando = [
            "ffmpeg",
            "-i", video['ruta'],
            "-c", "copy",
            "-f", "segment",
            "-segment_times", ",".join(str(t) for t in cortes),
            "-reset_timestamps", "1",
            f"{video['nombre']}_%02d{video['extension']}"
        ]

    subprocess.run(comando)

    mostrar_exito("\nVídeo dividido.")
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
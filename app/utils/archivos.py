"""
Utilidades para validación segura de archivos subidos.
Actividad 10: Verificación por firma de bytes (magic numbers).
"""

# Firmas de bytes de los formatos de imagen permitidos
FIRMAS = (
    b"\xff\xd8\xff",        # JPEG / JPG
    b"\x89PNG\r\n\x1a\n",  # PNG
    b"RIFF",               # WebP  (los primeros 4 bytes; bytes 8-11 son "WEBP")
)


def parece_imagen(contenido: bytes) -> bool:
    """
    Devuelve True si el contenido comienza con la firma de bytes de
    uno de los formatos de imagen soportados (JPG, PNG, WebP).
    No confía en la extensión ni en el Content-Type declarado por el cliente.
    """
    return contenido.startswith(FIRMAS)

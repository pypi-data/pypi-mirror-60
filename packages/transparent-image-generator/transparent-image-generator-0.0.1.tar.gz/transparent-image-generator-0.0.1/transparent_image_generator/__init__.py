from base64 import b64encode
from io import BytesIO

from png import Writer


def tig(width: int, height: int) -> bytes:
    with BytesIO() as image:
        palette = [(0xFF, 0xFF, 0xFF, 0x00)]
        writer = Writer(width, height, palette=palette, bitdepth=1, compression=9)
        writer.write(image, [[0 for _ in range(width)] for _ in range(height)])
        image.seek(0)
        return image.read()


def tig_data_url(width: int, height: int) -> str:
    return 'data:image/png;base64,' + b64encode(tig(width, height)).decode()

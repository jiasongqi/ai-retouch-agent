"""把 Brand Kit 叠到已排好的画幅上：角标 logo、不改主体。"""

from PIL import Image

from app.listing.fit import as_rgba, parse_hex, png
from app.schemas.brand import BrandKit


def overlay(data: bytes, kit: BrandKit, logo: bytes | None = None) -> bytes:
    image = as_rgba(data)
    if kit.show_logo and logo:
        image = _paste_logo(image, logo, kit.safe_margin)
    return png(image)


def bar_color(kit: BrandKit) -> tuple[int, int, int]:
    return parse_hex(kit.primary_color)


def _paste_logo(canvas: Image.Image, logo: bytes, safe_margin: float) -> Image.Image:
    mark = as_rgba(logo)
    max_h = max(16, int(canvas.height * 0.07))
    max_w = max(16, int(canvas.width * 0.22))
    scale = min(max_h / mark.height, max_w / mark.width)
    size = (max(1, int(mark.width * scale)), max(1, int(mark.height * scale)))
    mark = mark.resize(size, Image.Resampling.LANCZOS)
    margin_x = int(canvas.width * safe_margin)
    margin_y = int(canvas.height * safe_margin)
    x = canvas.width - mark.width - margin_x
    y = margin_y
    canvas.paste(mark, (x, y), mark)
    return canvas

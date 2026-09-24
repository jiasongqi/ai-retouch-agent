"""主体裁切、按占比放入画幅。平台导出、场景合成、套图共用。"""

import io

from PIL import Image

from app.edits.pixels import remove_background


def png(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def as_rgba(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGBA")


def has_cutout(image: Image.Image) -> bool:
    extrema = image.getchannel("A").getextrema()
    return extrema is not None and extrema[0] < 255


def cutout(data: bytes) -> Image.Image:
    """有透明通道则直接用，否则四角/主体抠图。"""
    image = as_rgba(data)
    if has_cutout(image):
        return image
    return as_rgba(remove_background(data))


def bbox_of(image: Image.Image) -> tuple[int, int, int, int] | None:
    return image.getchannel("A").getbbox()


def fill_of(placed: tuple[int, int], canvas: tuple[int, int]) -> float:
    width, height = canvas
    if width <= 0 or height <= 0:
        return 0.0
    return max(placed[0] / width, placed[1] / height)


def parse_hex(value: str) -> tuple[int, int, int]:
    raw = value.lstrip("#")
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def place_subject(
    subject: Image.Image,
    width: int,
    height: int,
    *,
    fill_ratio: float,
    background: tuple[int, int, int, int],
    safe_margin: float = 0.08,
) -> tuple[Image.Image, float]:
    """把抠好的主体按占比居中放入目标画幅，不裁切。"""
    box = bbox_of(subject)
    source = subject.crop(box) if box else subject
    if source.width == 0 or source.height == 0:
        canvas = Image.new("RGBA", (width, height), background)
        return canvas, 0.0

    inner_w = max(1, int(width * (1 - 2 * safe_margin)))
    inner_h = max(1, int(height * (1 - 2 * safe_margin)))
    target = min(inner_w, inner_h) * fill_ratio
    scale = target / max(source.width, source.height)
    placed_w = max(1, int(round(source.width * scale)))
    placed_h = max(1, int(round(source.height * scale)))
    if placed_w > inner_w or placed_h > inner_h:
        scale = min(inner_w / placed_w, inner_h / placed_h)
        placed_w = max(1, int(round(placed_w * scale)))
        placed_h = max(1, int(round(placed_h * scale)))

    resized = source.resize((placed_w, placed_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (width, height), background)
    left = (width - placed_w) // 2
    top = (height - placed_h) // 2
    canvas.paste(resized, (left, top), resized)
    return canvas, fill_of((placed_w, placed_h), (inner_w, inner_h))

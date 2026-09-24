"""影棚精修：接触阴影 + 倒影。尺寸保持不变，方便写回图层。"""

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from app.listing.fit import bbox_of, cutout, png


class EmptySubject(Exception):
    """没有可精修的不透明主体。"""


def apply_studio_finish(
    data: bytes,
    *,
    shadow: bool = True,
    reflection: bool = True,
    intensity: float = 0.55,
    background: tuple[int, int, int, int] = (255, 255, 255, 255),
) -> bytes:
    subject = cutout(data)
    box = bbox_of(subject)
    if box is None:
        raise EmptySubject
    intensity = max(0.0, min(1.0, intensity))

    canvas = Image.new("RGBA", subject.size, background)
    if reflection:
        canvas = Image.alpha_composite(canvas, _reflection(subject, box, intensity))
    if shadow:
        canvas = Image.alpha_composite(canvas, _contact_shadow(subject.size, box, intensity))
    canvas.paste(subject, (0, 0), subject)
    return png(canvas)


def _contact_shadow(
    size: tuple[int, int], box: tuple[int, int, int, int], intensity: float
) -> Image.Image:
    left, _top, right, bottom = box
    width = max(4, right - left)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    radius_x = int(width * 0.42)
    radius_y = max(3, int(width * 0.07))
    cx = (left + right) // 2
    cy = min(size[1] - 1, bottom + radius_y // 3)
    alpha = int(90 * intensity)
    draw.ellipse(
        (cx - radius_x, cy - radius_y, cx + radius_x, cy + radius_y),
        fill=(20, 18, 16, alpha),
    )
    blur = max(3, int(width * 0.045))
    return layer.filter(ImageFilter.GaussianBlur(radius=blur))


def _reflection(
    subject: Image.Image, box: tuple[int, int, int, int], intensity: float
) -> Image.Image:
    left, _top, right, bottom = box
    crop = subject.crop(box)
    flipped = crop.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    fade = Image.new("L", flipped.size, 0)
    pixels = fade.load()
    height = flipped.height
    max_alpha = int(140 * intensity)
    for y in range(height):
        level = int(max_alpha * max(0.0, 1 - (y / max(1, height * 0.55)) ** 1.4))
        for x in range(flipped.width):
            pixels[x, y] = level
    flipped.putalpha(ImageChops.multiply(flipped.getchannel("A"), fade))

    layer = Image.new("RGBA", subject.size, (0, 0, 0, 0))
    layer.paste(flipped, (left, bottom), flipped)
    return layer

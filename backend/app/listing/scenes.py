from dataclasses import dataclass

from PIL import Image, ImageDraw

from app.listing.fit import cutout, parse_hex, place_subject, png


@dataclass(frozen=True)
class Scene:
    id: str
    label: str
    hint: str
    swatch: str
    prompt: str
    colors: tuple[str, ...]


SCENES: tuple[Scene, ...] = (
    Scene("white", "纯白", "最干净的主图底", "#F7F7F7", "纯白摄影棚背景，柔和顶光", ("#FFFFFF", "#F4F4F4")),
    Scene("marble", "大理石", "浅色石纹台面", "#E8E4DC", "浅色大理石台面，细密纹理", ("#F4F0E8", "#D9D2C5")),
    Scene("oak", "原木", "暖色木纹桌面", "#C4A574", "温暖橡木桌面，顺纹光泽", ("#D7B48A", "#A67C4E")),
    Scene("linen", "亚麻", "米白织物", "#E8DCC8", "米白亚麻布面，柔软纹理", ("#F3E6D0", "#D9C4A4")),
    Scene("concrete", "水泥", "冷灰工业风", "#B5B3AE", "浅水泥墙面，细颗粒", ("#C8C6C1", "#9E9B95")),
    Scene("sage", "鼠尾草", "低饱和绿", "#B7C4B2", "鼠尾草绿背景，柔光", ("#C9D4C4", "#9AAF96")),
    Scene("charcoal", "炭灰", "深色棚拍", "#3A3A38", "深灰影棚背景，低调光", ("#4A4A46", "#2A2A28")),
    Scene("cream", "奶油", "暖白静物", "#F3E6D0", "奶油色静物背景", ("#F8EDDA", "#E6D3B4")),
    Scene("terrazzo", "水磨石", "斑点台面", "#DDD6CC", "浅色水磨石台面", ("#E8E0D4", "#C9C0B4")),
    Scene("slate", "岩板", "蓝灰岩面", "#8A93A0", "蓝灰岩板背景", ("#9AA3B0", "#6E7886")),
    Scene("sand", "沙色", "暖黄地面", "#E2C9A0", "细沙色背景，暖光", ("#EDD7B0", "#C9A878")),
    Scene("studio", "影棚灰", "渐变灰底", "#C9C9C6", "影棚灰渐变背景", ("#E8E8E6", "#B0B0AC")),
)

_BY_ID = {scene.id: scene for scene in SCENES}


class UnknownScene(Exception):
    pass


def get(scene_id: str) -> Scene:
    scene = _BY_ID.get(scene_id)
    if scene is None:
        raise UnknownScene(f"未知场景：{scene_id}")
    return scene


def catalog() -> list[dict]:
    return [
        {
            "id": scene.id,
            "label": scene.label,
            "hint": scene.hint,
            "swatch": scene.swatch,
            "prompt": scene.prompt,
        }
        for scene in SCENES
    ]


def render(scene_id: str, width: int, height: int) -> Image.Image:
    scene = get(scene_id)
    canvas = _gradient(width, height, scene.colors)
    _grain(canvas, salt=sum(ord(ch) for ch in scene.id))
    if scene.id == "marble":
        _veins(canvas, (210, 205, 196), 9)
    elif scene.id == "oak":
        _grain_lines(canvas, (140, 96, 58), 14)
    elif scene.id == "terrazzo":
        _specks(canvas, count=180)
    return canvas


def composite(
    data: bytes,
    scene_id: str,
    width: int,
    height: int,
    *,
    fill_ratio: float = 0.72,
    safe_margin: float = 0.08,
) -> bytes:
    backdrop = render(scene_id, width, height)
    canvas, _ratio = place_subject(
        cutout(data),
        width,
        height,
        fill_ratio=fill_ratio,
        background=(0, 0, 0, 0),
        safe_margin=safe_margin,
    )
    return png(Image.alpha_composite(backdrop, canvas))


def _gradient(width: int, height: int, colors: tuple[str, ...]) -> Image.Image:
    top = parse_hex(colors[0])
    bottom = parse_hex(colors[-1])
    image = Image.new("RGBA", (width, height))
    pixels = image.load()
    for y in range(height):
        t = y / max(1, height - 1)
        tone = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom, strict=True))
        for x in range(width):
            pixels[x, y] = (*tone, 255)
    return image


def _grain(image: Image.Image, *, salt: int) -> None:
    small = Image.new("RGBA", (max(1, image.width // 6), max(1, image.height // 6)))
    pixels = small.load()
    for y in range(small.height):
        for x in range(small.width):
            delta = ((x * 17 + y * 31 + salt) % 13) - 6
            pixels[x, y] = (128 + delta, 128 + delta, 128 + delta, abs(delta) * 6)
    overlay = small.resize(image.size, Image.Resampling.BILINEAR)
    image.alpha_composite(overlay)


def _veins(image: Image.Image, color: tuple[int, int, int], count: int) -> None:
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for index in range(count):
        y = int(height * (0.08 + 0.85 * index / max(1, count)))
        draw.line(
            (0, y + (index % 5), width, y + ((index * 3) % 11) - 5),
            fill=(*color, 90),
            width=1,
        )


def _grain_lines(image: Image.Image, color: tuple[int, int, int], count: int) -> None:
    draw = ImageDraw.Draw(image)
    height = image.height
    for index in range(count):
        y = int(height * (index + 0.5) / count)
        draw.line((0, y, image.width, y + (index % 3) - 1), fill=(*color, 50), width=2)


def _specks(image: Image.Image, count: int) -> None:
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for index in range(count):
        x = (index * 47 + 13) % width
        y = (index * 89 + 29) % height
        tone = 140 + (index * 17) % 80
        draw.ellipse((x, y, x + 3, y + 2), fill=(tone, tone - 8, tone - 16, 140))

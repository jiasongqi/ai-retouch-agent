import enum
from dataclasses import dataclass

from PIL import Image

from app.edits.studio import apply_studio_finish
from app.listing.fit import as_rgba, bbox_of, cutout, place_subject, png


class PlatformId(enum.StrEnum):
    TAOBAO_MAIN = "taobao_main"
    AMAZON_MAIN = "amazon_main"
    DOUYIN_COVER = "douyin_cover"


@dataclass(frozen=True)
class PlatformSpec:
    id: PlatformId
    label: str
    hint: str
    width: int
    height: int
    fill_ratio: float
    min_side: int
    require_white: bool
    background: tuple[int, int, int, int]


PLATFORMS: dict[PlatformId, PlatformSpec] = {
    PlatformId.TAOBAO_MAIN: PlatformSpec(
        id=PlatformId.TAOBAO_MAIN,
        label="淘宝主图",
        hint="1:1 白底，主体约占 85%，符合主图安全边距。",
        width=1200,
        height=1200,
        fill_ratio=0.85,
        min_side=800,
        require_white=True,
        background=(255, 255, 255, 255),
    ),
    PlatformId.AMAZON_MAIN: PlatformSpec(
        id=PlatformId.AMAZON_MAIN,
        label="亚马逊主图",
        hint="正方形白底，边长 ≥ 1000，主体居中约占 85%。",
        width=1600,
        height=1600,
        fill_ratio=0.85,
        min_side=1000,
        require_white=True,
        background=(255, 255, 255, 255),
    ),
    PlatformId.DOUYIN_COVER: PlatformSpec(
        id=PlatformId.DOUYIN_COVER,
        label="抖音封面",
        hint="9:16 竖版封面，主体约占 72%，上下留白给标题。",
        width=1080,
        height=1920,
        fill_ratio=0.72,
        min_side=720,
        require_white=False,
        background=(247, 244, 239, 255),
    ),
}


@dataclass(frozen=True)
class FitResult:
    data: bytes
    width: int
    height: int
    fill_ratio: float
    issues: tuple[str, ...]


def spec_of(platform: PlatformId | str) -> PlatformSpec:
    return PLATFORMS[PlatformId(platform)]


def fit_platform(
    data: bytes,
    platform: PlatformId | str,
    *,
    studio: bool = True,
    safe_margin: float = 0.08,
    background: tuple[int, int, int, int] | None = None,
) -> FitResult:
    spec = spec_of(platform)
    source = apply_studio_finish(data) if studio else png(cutout(data))
    fill = background or spec.background
    canvas, ratio = place_subject(
        cutout(source) if studio else as_rgba(source),
        spec.width,
        spec.height,
        fill_ratio=spec.fill_ratio,
        background=fill,
        safe_margin=safe_margin,
    )
    output = png(canvas)
    return FitResult(
        data=output,
        width=spec.width,
        height=spec.height,
        fill_ratio=ratio,
        issues=tuple(compliance(output, spec, ratio)),
    )


def compliance(data: bytes, spec: PlatformSpec, fill_ratio: float | None = None) -> list[str]:
    image = as_rgba(data)
    issues: list[str] = []
    if image.size != (spec.width, spec.height):
        issues.append("画幅尺寸与平台预设不符")
    if min(image.size) < spec.min_side:
        issues.append(f"边长不足 {spec.min_side}")
    ratio = fill_ratio if fill_ratio is not None else _estimated_fill(image, spec)
    if ratio + 1e-6 < spec.fill_ratio - 0.12:
        issues.append("主体占比过小")
    if ratio > spec.fill_ratio + 0.12:
        issues.append("主体占比过大，可能顶到安全边")
    if spec.require_white and not _corners_white(image):
        issues.append("四角不是白底")
    return issues


def _estimated_fill(image: Image.Image, spec: PlatformSpec) -> float:
    if spec.require_white:
        matte = _white_as_transparent(image)
        box = bbox_of(matte)
        if box is None:
            return 0.0
        return max((box[2] - box[0]) / image.width, (box[3] - box[1]) / image.height)
    box = bbox_of(image)
    if box is None:
        return 1.0
    return max((box[2] - box[0]) / image.width, (box[3] - box[1]) / image.height)


def _white_as_transparent(image: Image.Image) -> Image.Image:
    clone = image.copy()
    pixels = clone.load()
    for y in range(clone.height):
        for x in range(clone.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha < 8 or (red > 245 and green > 245 and blue > 245):
                pixels[x, y] = (red, green, blue, 0)
    return clone


def _corners_white(image: Image.Image, tolerance: int = 18) -> bool:
    samples = (
        (2, 2),
        (image.width - 3, 2),
        (2, image.height - 3),
        (image.width - 3, image.height - 3),
    )
    pixels = image.load()
    for x, y in samples:
        red, green, blue, _alpha = pixels[x, y]
        if abs(red - 255) > tolerance or abs(green - 255) > tolerance or abs(blue - 255) > tolerance:
            return False
    return True


def platform_catalog() -> list[dict]:
    return [
        {
            "id": spec.id.value,
            "label": spec.label,
            "hint": spec.hint,
            "width": spec.width,
            "height": spec.height,
            "fill_ratio": spec.fill_ratio,
        }
        for spec in PLATFORMS.values()
    ]

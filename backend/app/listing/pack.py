"""一键套图：白底主图 + 场景图 + 卖点图 + 竖版封面。全程本地像素，不调模型。"""

from PIL import Image, ImageDraw, ImageFont

from app.edits.studio import apply_studio_finish
from app.listing import brand as brand_overlay
from app.listing.fit import as_rgba, parse_hex, png
from app.listing.platforms import PlatformId, fit_platform
from app.listing.scenes import composite
from app.schemas.brand import BrandKit

PACK_STEPS = ("white", "scene", "selling", "cover")


def build_pack(
    data: bytes,
    *,
    kit: BrandKit | None = None,
    scene_id: str | None = None,
    caption: str = "核心卖点",
    logo: bytes | None = None,
) -> list[dict]:
    kit = kit or BrandKit()
    scene_id = scene_id or kit.default_scene_id or "marble"
    studio = apply_studio_finish(data)
    white = fit_platform(studio, PlatformId.TAOBAO_MAIN, studio=False, safe_margin=kit.safe_margin)
    scene = composite(
        data,
        scene_id,
        1080,
        1350,
        fill_ratio=0.70,
        safe_margin=kit.safe_margin,
    )
    selling = selling_point(studio, caption, kit)
    cover = fit_platform(
        data,
        PlatformId.DOUYIN_COVER,
        studio=True,
        safe_margin=kit.safe_margin,
    )
    framed = [
        ("white", white.data, white.width, white.height, white.fill_ratio, list(white.issues)),
        ("scene", scene, 1080, 1350, 0.70, []),
        ("selling", selling, 1080, 1350, 0.62, []),
        ("cover", cover.data, cover.width, cover.height, cover.fill_ratio, list(cover.issues)),
    ]
    items = []
    for kind, raw, width, height, fill, issues in framed:
        branded = brand_overlay.overlay(raw, kit, logo)
        items.append(
            {
                "kind": kind,
                "data": branded,
                "width": width,
                "height": height,
                "fill_ratio": fill,
                "issues": issues,
                "scene_id": scene_id if kind == "scene" else None,
            }
        )
    return items


def selling_point(data: bytes, caption: str, kit: BrandKit) -> bytes:
    canvas = Image.new("RGBA", (1080, 1350), (*parse_hex(kit.accent_color), 255))
    product = as_rgba(data)
    max_w, max_h = 820, 900
    scale = min(max_w / product.width, max_h / product.height, 1.0)
    size = (max(1, int(product.width * scale)), max(1, int(product.height * scale)))
    product = product.resize(size, Image.Resampling.LANCZOS)
    canvas.paste(product, ((1080 - size[0]) // 2, 80), product)

    bar = Image.new("RGBA", (1080, 220), (*brand_overlay.bar_color(kit), 255))
    canvas.paste(bar, (0, 1130))
    text = (caption or "核心卖点").strip()[:18]
    draw = ImageDraw.Draw(canvas)
    font = _font(56)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    draw.text(((1080 - text_w) // 2, 1195), text, fill=(255, 255, 255, 255), font=font)
    return png(canvas)


def _font(size: int) -> ImageFont.ImageFont:
    for path in (
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()

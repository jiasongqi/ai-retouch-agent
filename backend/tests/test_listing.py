from io import BytesIO

from PIL import Image, ImageDraw

from app.edits.studio import EmptySubject, apply_studio_finish
from app.listing.brand import overlay
from app.listing.fit import as_rgba
from app.listing.pack import build_pack
from app.listing.platforms import PlatformId, compliance, fit_platform, spec_of
from app.listing.scenes import SCENES, catalog, composite, get
from app.schemas.brand import BrandKit
import pytest


def _png(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _subject(size=(240, 240)) -> bytes:
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    inset = 50
    ImageDraw.Draw(image).ellipse(
        (inset, inset, size[0] - inset, size[1] - inset), fill=(30, 90, 180, 255)
    )
    return _png(image)


def test_studio_keeps_size_and_adds_shadow():
    source = _subject()
    output = apply_studio_finish(source, shadow=True, reflection=True)
    image = as_rgba(output)
    assert image.size == (240, 240)
    # 四角仍接近白底，底部中央因阴影更暗
    corner = image.getpixel((4, 4))[:3]
    assert all(channel > 240 for channel in corner)
    mid_bottom = image.getpixel((120, 198))[:3]
    assert sum(mid_bottom) < sum(corner)


def test_studio_empty_cutout_raises():
    blank = _png(Image.new("RGBA", (80, 80), (0, 0, 0, 0)))
    with pytest.raises(EmptySubject):
        apply_studio_finish(blank)


def test_platform_fill_and_white_corners():
    fitted = fit_platform(_subject((200, 140)), PlatformId.TAOBAO_MAIN, studio=True)
    assert fitted.width == fitted.height == 1200
    assert 0.73 <= fitted.fill_ratio <= 0.92
    assert fitted.issues == ()
    spec = spec_of(PlatformId.TAOBAO_MAIN)
    assert compliance(fitted.data, spec, fitted.fill_ratio) == []


def test_amazon_meets_min_side():
    fitted = fit_platform(_subject(), PlatformId.AMAZON_MAIN, studio=False)
    assert min(fitted.width, fitted.height) >= 1000
    assert fitted.issues == ()


def test_scene_catalog_has_twelve_looks():
    assert len(SCENES) == 12
    assert {item["id"] for item in catalog()} == {scene.id for scene in SCENES}
    assert get("marble").label == "大理石"


def test_composite_puts_subject_on_scene():
    output = composite(_subject(), "oak", 320, 400, fill_ratio=0.7)
    image = as_rgba(output)
    assert image.size == (320, 400)
    # 原木场景不是白底，中心仍是偏蓝的商品
    center = image.getpixel((160, 200))
    assert center[2] > center[0]


def test_listing_pack_emits_four_assets():
    items = build_pack(_subject(), caption="锁水")
    assert [item["kind"] for item in items] == ["white", "scene", "selling", "cover"]
    assert items[0]["width"] == 1200
    assert items[1]["height"] == 1350
    assert items[3]["height"] == 1920


def test_brand_overlay_pastes_logo_inside_margin():
    kit = BrandKit(safe_margin=0.1, show_logo=True)
    logo = _png(Image.new("RGBA", (40, 20), (255, 0, 0, 255)))
    canvas = _png(Image.new("RGBA", (200, 200), (255, 255, 255, 255)))
    branded = as_rgba(overlay(canvas, kit, logo))
    pixel = branded.getpixel((166, 27))
    assert pixel[0] > 200 and pixel[1] < 40

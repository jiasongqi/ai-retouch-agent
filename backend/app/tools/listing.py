import asyncio

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app import storage
from app.edits.split import already_split
from app.edits.studio import EmptySubject, apply_studio_finish
from app.layers import BACKGROUND_LAYER_ID, LayerKind
from app.listing.brand import overlay
from app.listing.fit import png
from app.listing.pack import build_pack
from app.listing.platforms import PlatformId, fit_platform
from app.listing.scenes import UnknownScene, composite, get as get_scene, render
from app.models.asset import AssetKind
from app.models.tool_run import ToolRun
from app.schemas.brand import BrandKit
from app.services import assets, auth, runs
from app.tools.base import LayerRef, ToolSpec
from app.tools.context import ToolError, document_of, flatten_session, require_session
from app.tools.marketing import _store
from app.tools.target import layer_image, resolve_target, write_layer_image

_LAYER = "layer_id"


class ApplyStudioFinishIn(LayerRef):
    shadow: bool = True
    reflection: bool = True
    intensity: float = Field(default=0.55, ge=0, le=1)


class ApplySceneIn(LayerRef):
    scene_id: str = Field(min_length=1, max_length=32, description="场景库 id，如 marble、oak")


class PreparePlatformExportIn(BaseModel):
    platforms: list[PlatformId] = Field(
        default_factory=lambda: list(PlatformId),
        min_length=1,
        max_length=len(PlatformId),
        description="taobao_main / amazon_main / douyin_cover，默认三个都出。",
    )
    studio: bool = Field(default=True, description="导出前是否补接触阴影与倒影")
    apply_brand: bool = True


class ExportListingPackIn(BaseModel):
    scene_id: str | None = Field(default=None, description="场景图用哪张底，默认 Brand Kit")
    caption: str = Field(default="核心卖点", max_length=24)
    apply_brand: bool = True


async def _kit_of(session: AsyncSession, user_id) -> tuple[BrandKit, bytes | None]:
    user = await auth.get_by_id(session, user_id)
    kit = BrandKit.model_validate((user.brand_kit if user else None) or {})
    logo = None
    if kit.show_logo and kit.logo_asset_id:
        asset = await assets.get_for_user(session, user_id, kit.logo_asset_id)
        if asset is not None:
            logo = await storage.get(asset.storage_key)
    return kit, logo


def _unique(platforms: list[PlatformId]) -> list[PlatformId]:
    seen: list[PlatformId] = []
    for item in platforms:
        if item not in seen:
            seen.append(item)
    return seen


async def apply_studio_finish_exec(session: AsyncSession, run: ToolRun) -> dict:
    record = await require_session(session, run)
    layer = resolve_target(document_of(record), run.params.get(_LAYER))
    await runs.report(session, run, 20, "读取图层")
    data = await layer_image(session, record, layer)
    await runs.report(session, run, 55, "补阴影与倒影")
    try:
        output = await asyncio.to_thread(
            lambda: apply_studio_finish(
                data,
                shadow=run.params.get("shadow", True),
                reflection=run.params.get("reflection", True),
                intensity=run.params.get("intensity", 0.55),
            )
        )
    except EmptySubject as exc:
        raise ToolError("没有可精修的主体，先去背景或换一张图") from exc
    return await write_layer_image(session, run, record, layer.id, output, AssetKind.GENERATED)


async def apply_scene_exec(session: AsyncSession, run: ToolRun) -> dict:
    record = await require_session(session, run)
    scene_id = run.params["scene_id"]
    try:
        get_scene(scene_id)
    except UnknownScene as exc:
        raise ToolError(str(exc)) from exc

    document = document_of(record)
    kit, _logo = await _kit_of(session, run.user_id)
    await runs.report(session, run, 20, "铺场景")

    if already_split(document):
        background = next(
            (
                layer
                for layer in document.layers
                if layer.id == BACKGROUND_LAYER_ID and layer.kind is LayerKind.IMAGE
            ),
            None,
        )
        if background is not None:
            backdrop = await asyncio.to_thread(
                lambda: png(render(scene_id, background.width, background.height))
            )
            return await write_layer_image(
                session, run, record, background.id, backdrop, AssetKind.BACKGROUND
            )

    layer = resolve_target(document, run.params.get(_LAYER))
    data = await layer_image(session, record, layer)
    output = await asyncio.to_thread(
        lambda: composite(
            data,
            scene_id,
            layer.width,
            layer.height,
            safe_margin=kit.safe_margin,
        )
    )
    return await write_layer_image(session, run, record, layer.id, output, AssetKind.GENERATED)


async def prepare_platform_export_exec(session: AsyncSession, run: ToolRun) -> dict:
    record = await require_session(session, run)
    platforms = _unique([PlatformId(value) for value in run.params["platforms"]])
    kit, logo = await _kit_of(session, run.user_id)
    await runs.report(session, run, 20, "读取画布")
    source = await flatten_session(session, record)
    images: list[bytes] = []
    variants: list[dict] = []
    total = len(platforms)
    for index, platform in enumerate(platforms):
        await runs.report(session, run, 30 + int(60 * index / total), f"适配 {platform.value}")
        try:
            fitted = await asyncio.to_thread(
                lambda p=platform: fit_platform(
                    source,
                    p,
                    studio=run.params.get("studio", True),
                    safe_margin=kit.safe_margin,
                )
            )
        except EmptySubject as exc:
            raise ToolError("没有可导出的主体，先去背景或换一张图") from exc
        data = fitted.data
        if run.params.get("apply_brand", True):
            data = overlay(data, kit, logo)
        images.append(data)
        variants.append(
            {
                "kind": "platform",
                "platform": platform.value,
                "width": fitted.width,
                "height": fitted.height,
                "fill_ratio": round(fitted.fill_ratio, 3),
                "issues": list(fitted.issues),
            }
        )
    await runs.report(session, run, 95, "平台画幅已加入图片墙")
    return await _store(session, run, images, kind=AssetKind.EXPORT, variants=variants)


async def export_listing_pack_exec(session: AsyncSession, run: ToolRun) -> dict:
    record = await require_session(session, run)
    kit, logo = await _kit_of(session, run.user_id)
    await runs.report(session, run, 15, "读取画布")
    source = await flatten_session(session, record)
    await runs.report(session, run, 35, "生成套图")
    try:
        items = await asyncio.to_thread(
            lambda: build_pack(
                source,
                kit=kit,
                scene_id=run.params.get("scene_id"),
                caption=run.params.get("caption") or "核心卖点",
                logo=logo if run.params.get("apply_brand", True) else None,
            )
        )
    except (EmptySubject, UnknownScene) as exc:
        raise ToolError(str(exc) if str(exc) else "套图失败，检查主体或场景") from exc
    images = [item["data"] for item in items]
    variants = [
        {
            "kind": item["kind"],
            "width": item["width"],
            "height": item["height"],
            "fill_ratio": round(item["fill_ratio"], 3),
            "issues": item["issues"],
            "scene_id": item["scene_id"],
        }
        for item in items
    ]
    await runs.report(session, run, 95, "套图已加入图片墙")
    return await _store(session, run, images, kind=AssetKind.EXPORT, variants=variants)


APPLY_STUDIO_FINISH = ToolSpec(
    name="apply_studio_finish",
    label="影棚精修",
    description="给主体补接触阴影和倒影，写成影棚商品照。默认最上层图像。不改画幅尺寸。",
    params=ApplyStudioFinishIn,
    handler=apply_studio_finish_exec,
    queued=True,
    session_required=True,
)

APPLY_SCENE = ToolSpec(
    name="apply_scene",
    label="铺场景",
    description=(
        "把商品放到场景库里的固定背景上，如 marble 大理石、oak 原木、linen 亚麻。"
        "已拆层时只换背景层；未拆层则合成到当前图像层。不要用它来自由描述换背景。"
    ),
    params=ApplySceneIn,
    handler=apply_scene_exec,
    queued=True,
    session_required=True,
)

PREPARE_PLATFORM_EXPORT = ToolSpec(
    name="prepare_platform_export",
    label="平台导出",
    description=(
        "按淘宝主图、亚马逊主图、抖音封面的画幅和主体占比导出，只进图片墙。"
        "默认一次出三个平台。用户说上架尺寸、平台主图时用这个，不要用 crop_canvas。"
    ),
    params=PreparePlatformExportIn,
    handler=prepare_platform_export_exec,
    queued=False,
    session_required=True,
)

EXPORT_LISTING_PACK = ToolSpec(
    name="export_listing_pack",
    label="一键套图",
    description=(
        "一次出白底主图、场景图、卖点图和 9:16 竖版，只进图片墙。"
        "caption 是卖点条文案。scene_id 可指定场景库背景。"
    ),
    params=ExportListingPackIn,
    handler=export_listing_pack_exec,
    queued=True,
    session_required=True,
)

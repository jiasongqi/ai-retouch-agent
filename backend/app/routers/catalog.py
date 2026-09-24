from fastapi import APIRouter, HTTPException, status

from app.db import SessionDep
from app.deps import CurrentUser
from app.listing.platforms import platform_catalog
from app.listing.scenes import UnknownScene, catalog as scene_catalog, get as get_scene
from app.schemas.brand import BrandKit, PlatformOut, SceneOut
from app.services import assets as asset_service

router = APIRouter(tags=["catalog"])


@router.get("/scenes", response_model=list[SceneOut])
async def list_scenes(_: CurrentUser) -> list[dict]:
    return scene_catalog()


@router.get("/platforms", response_model=list[PlatformOut])
async def list_platforms(_: CurrentUser) -> list[dict]:
    return platform_catalog()


@router.get("/brand-kit", response_model=BrandKit)
async def get_brand_kit(user: CurrentUser) -> BrandKit:
    return BrandKit.model_validate(user.brand_kit or {})


@router.put("/brand-kit", response_model=BrandKit)
async def put_brand_kit(payload: BrandKit, user: CurrentUser, session: SessionDep) -> BrandKit:
    if payload.default_scene_id:
        try:
            get_scene(payload.default_scene_id)
        except UnknownScene as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    if payload.logo_asset_id is not None:
        logo = await asset_service.get_for_user(session, user.id, payload.logo_asset_id)
        if logo is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Logo 素材不存在")
    user.brand_kit = payload.model_dump(mode="json")
    await session.commit()
    await session.refresh(user)
    return BrandKit.model_validate(user.brand_kit)

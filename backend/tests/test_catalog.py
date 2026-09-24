import httpx
import pytest

from tests.canvas import apply
from tests.test_sessions import open_session


@pytest.fixture
async def signed_in(client: httpx.AsyncClient, credentials):
    await client.post("/api/auth/register", json=credentials)
    return client


async def test_scenes_and_platforms_catalog(signed_in: httpx.AsyncClient):
    scenes = (await signed_in.get("/api/scenes")).json()
    platforms = (await signed_in.get("/api/platforms")).json()
    assert len(scenes) == 12
    assert {item["id"] for item in platforms} == {"taobao_main", "amazon_main", "douyin_cover"}


async def test_brand_kit_roundtrip(signed_in: httpx.AsyncClient):
    original = (await signed_in.get("/api/brand-kit")).json()
    assert original["primary_color"] == "#171917"

    saved = await signed_in.put(
        "/api/brand-kit",
        json={**original, "primary_color": "#112233", "safe_margin": 0.1},
    )
    assert saved.status_code == 200, saved.text
    assert saved.json()["primary_color"] == "#112233"
    assert (await signed_in.get("/api/brand-kit")).json()["safe_margin"] == 0.1


async def test_brand_kit_rejects_unknown_scene(signed_in: httpx.AsyncClient):
    current = (await signed_in.get("/api/brand-kit")).json()
    response = await signed_in.put(
        "/api/brand-kit",
        json={**current, "default_scene_id": "not-a-scene"},
    )
    assert response.status_code == 422


async def test_apply_scene_and_listing_pack(signed_in: httpx.AsyncClient):
    session = await open_session(signed_in)
    updated = await apply(signed_in, session["id"], "apply_scene", {"scene_id": "marble"})
    assert updated["revision"] == 2

    packed = await apply(signed_in, session["id"], "export_listing_pack", {"caption": "锁水"})
    exported = [asset for asset in packed["assets"] if asset["kind"] == "export"]
    assert len(exported) == 4
    assert packed["current_asset_id"] == updated["current_asset_id"]

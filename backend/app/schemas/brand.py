import uuid

from pydantic import BaseModel, Field, field_validator


class BrandKit(BaseModel):
    primary_color: str = Field(default="#171917", description="主色，用于卖点条和点缀")
    accent_color: str = Field(default="#C4B5A0", description="辅助色")
    logo_asset_id: uuid.UUID | None = None
    safe_margin: float = Field(default=0.08, ge=0.04, le=0.18)
    default_scene_id: str | None = Field(default="marble")
    show_logo: bool = True

    @field_validator("primary_color", "accent_color")
    @classmethod
    def _hex_color(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) != 7 or not normalized.startswith("#"):
            raise ValueError("颜色须为 #RRGGBB")
        try:
            int(normalized[1:], 16)
        except ValueError as exc:
            raise ValueError("颜色须为 #RRGGBB") from exc
        return "#" + normalized[1:].upper()


class SceneOut(BaseModel):
    id: str
    label: str
    hint: str
    swatch: str
    prompt: str


class PlatformOut(BaseModel):
    id: str
    label: str
    hint: str
    width: int
    height: int
    fill_ratio: float

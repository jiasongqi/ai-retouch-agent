from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / "public" / "landing"
FRAMES = [
    ("product-before.png", "1  修前原图"),
    ("product-after.png", "2  白底主图"),
    ("product-scene.png", "3  场景氛围"),
    ("product-story.png", "4  9:16 竖版"),
    ("product-poster.png", "5  促销海报"),
]
WIDTH, HEIGHT = 480, 600


def pick_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
    ):
        if path.exists():
            return ImageFont.truetype(str(path), 22)
    return ImageFont.load_default()


FONT = pick_font()


def main() -> None:
    frames: list[Image.Image] = []
    for name, caption in FRAMES:
        source = Image.open(ROOT / name).convert("RGB")
        source.thumbnail((WIDTH, HEIGHT - 56), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (WIDTH, HEIGHT), (239, 241, 238))
        canvas.paste(source, ((WIDTH - source.width) // 2, (HEIGHT - 56 - source.height) // 2))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, HEIGHT - 52, WIDTH, HEIGHT), fill=(23, 25, 23))
        draw.text((16, HEIGHT - 38), caption, font=FONT, fill=(217, 255, 110))
        frames.append(canvas.convert("P", palette=Image.Palette.ADAPTIVE, colors=64))

    dest = ROOT / "demo.gif"
    frames[0].save(dest, save_all=True, append_images=frames[1:], duration=1400, loop=0, optimize=True)
    print(f"wrote {dest} ({dest.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

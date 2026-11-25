"""Turn raw overlay captures (from tools/capture.mjs) into images to share.

    python tools/make_screenshots.py

Reads share/screenshots/raw/{ingame,pregame}_after.png (captures of the Arenan style)
and writes share/screenshots/1-ingame.png, 2-scoreboard.png and 3-champselect.png.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent / "share" / "screenshots"
RAW = ROOT / "raw"
GOLD = (240, 215, 140)
BRONZE = (201, 162, 74)
MARBLE = (237, 230, 214)


def font(size, bold=True):
    name = "georgiab.ttf" if bold else "georgia.ttf"
    try:
        return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)
    except OSError:
        return ImageFont.load_default()


def backdrop(w, h):
    """Dark arena-night gradient so the transparent overlay has something to sit on."""
    top, bottom = (34, 46, 66), (10, 15, 26)
    bg = Image.new("RGBA", (w, h))
    px = bg.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)) + (255,)
        for x in range(w):
            px[x, y] = c
    return bg


def on_backdrop(im):
    bg = backdrop(*im.size)
    bg.alpha_composite(im)
    return bg


def titled(img, title, subtitle=None):
    """Add a header band with the tournament name above an image."""
    band = 90 if subtitle else 70
    out = Image.new("RGBA", (img.width, img.height + band), (11, 18, 32, 255))
    out.alpha_composite(img, (0, band))
    d = ImageDraw.Draw(out)
    d.line([(0, band - 2), (img.width, band - 2)], fill=BRONZE, width=3)
    d.text((30, 14), title, font=font(36), fill=GOLD)
    if subtitle:
        d.text((32, 56), subtitle, font=font(22, bold=False), fill=MARBLE)
    return out


def save(img, name):
    path = ROOT / name
    img.convert("RGB").save(path, optimize=True)
    print("wrote", path)


def main():
    ingame = Image.open(RAW / "ingame_after.png").convert("RGBA")
    pregame = Image.open(RAW / "pregame_after.png").convert("RGBA")

    # 1. Whole in-game overlay.
    save(titled(on_backdrop(ingame), "ARENAN", "Under matchen – scoreboard, champion-flikar och gladiatorloggan"),
         "1-ingame.png")

    # 2. Scoreboard close-up, enlarged 1.25x so the details read on Discord.
    box = (180, 0, 1740, 100)
    close = ingame.crop(box).resize((round((box[2] - box[0]) * 1.25), round((box[3] - box[1]) * 1.25)),
                                    Image.LANCZOS)
    pad = 30
    framed = backdrop(close.width + 2 * pad, close.height + 2 * pad)
    framed.alpha_composite(close, (pad, pad))
    save(titled(framed, "ARENAN", "Scoreboarden"), "2-scoreboard.png")

    # 3. Champ select bar.
    save(titled(on_backdrop(pregame.crop((0, 745, 1920, 1080))), "ARENAN", "Champ select"), "3-champselect.png")


if __name__ == "__main__":
    main()

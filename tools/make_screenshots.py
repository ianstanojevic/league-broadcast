"""Turn raw overlay captures (from tools/capture.mjs) into images to share.

    python tools/make_screenshots.py

Reads share/screenshots/raw/{ingame,pregame}_{before,after}.png and writes
share/screenshots/1-ingame.png, 2-scoreboard-fore-efter.png, 3-champselect.png,
4-champselect-fore-efter.png.
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


def label(img, text, xy, size=34, fill=GOLD):
    d = ImageDraw.Draw(img)
    d.text(xy, text, font=font(size), fill=fill, stroke_width=3, stroke_fill=(8, 12, 20))


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


def stacked(before, after, gap=24, gutter=170):
    """Before above after, with the labels in their own left margin so they never cover the overlay."""
    w = max(before.width, after.width) + gutter
    out = backdrop(w, before.height + after.height + gap)
    out.alpha_composite(before, (gutter, 0))
    out.alpha_composite(after, (gutter, before.height + gap))
    label(out, "FÖRE", (24, before.height // 2 - 20))
    label(out, "EFTER", (24, before.height + gap + after.height // 2 - 20))
    return out


def save(img, name):
    path = ROOT / name
    img.convert("RGB").save(path, optimize=True)
    print("wrote", path)


def main():
    ig_after = Image.open(RAW / "ingame_after.png").convert("RGBA")
    ig_before = Image.open(RAW / "ingame_before.png").convert("RGBA")
    pg_after = Image.open(RAW / "pregame_after.png").convert("RGBA")
    pg_before = Image.open(RAW / "pregame_before.png").convert("RGBA")

    # 1. Whole in-game overlay.
    save(titled(on_backdrop(ig_after), "ARENAN", "Under matchen – scoreboard, champion-flikar och gladiatorloggan"),
         "1-ingame.png")

    # 2. Scoreboard close-up, before vs after, enlarged 1.25x so details read on Discord.
    box = (180, 0, 1740, 100)
    sc = lambda im: im.crop(box).resize((round((box[2] - box[0]) * 1.25), round((box[3] - box[1]) * 1.25)),
                                        Image.LANCZOS)
    save(titled(stacked(sc(ig_before), sc(ig_after), gap=40), "ARENAN", "Scoreboarden – före och efter"),
         "2-scoreboard-fore-efter.png")

    # 3. Champ select bar.
    pg_box = (0, 745, 1920, 1080)
    save(titled(on_backdrop(pg_after.crop(pg_box)), "ARENAN", "Champ select"), "3-champselect.png")

    # 4. Champ select before vs after.
    save(titled(stacked(pg_before.crop(pg_box), pg_after.crop(pg_box), gap=40), "ARENAN",
                "Champ select – före och efter"), "4-champselect-fore-efter.png")


if __name__ == "__main__":
    main()

"""Turn raw overlay captures (from underhall/tools/capture.mjs) into images to share.

    python underhall/tools/make_screenshots.py

Reads underhall/raw/{ingame,pregame}_after.png (captures of the Arenan style)
and writes bilder/1-ingame.png … 7-champselect-mitten.png (overview + close-ups).
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2] / "bilder"      # repo root / bilder
RAW = Path(__file__).resolve().parents[1] / "raw"          # underhall/raw (not in git)
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

    # Close-ups. Boxes are the element edges in the 1920x1080 captures.
    def closeup(im, box, scale, title, name, pad=30):
        part = im.crop(box)
        part = part.resize((round(part.width * scale), round(part.height * scale)), Image.LANCZOS)
        canvas = backdrop(part.width + 2 * pad, part.height + 2 * pad)
        canvas.alpha_composite(part, (pad, pad))
        save(titled(canvas, "ARENAN", title), name)

    # 4. Champion tabs: blue side and red side next to each other.
    left, right = (0, 128, 82, 602), (1838, 128, 1920, 602)
    gap = 120
    both = Image.new("RGBA", (82 * 2 + gap, 474), (0, 0, 0, 0))
    both.alpha_composite(ingame.crop(left), (0, 0))
    both.alpha_composite(ingame.crop(right), (82 + gap, 0))
    closeup(both, (0, 0, both.width, both.height), 2.0, "Champion-flikar", "4-champion-flikar.png", pad=50)

    # 5. Player statistics table at the bottom.
    closeup(ingame, (518, 796, 1403, 1080), 1.6, "Spelarstatistik", "5-spelarstatistik.png")

    # 6. Objective timers (bottom left).
    closeup(ingame, (0, 829, 306, 961), 2.5, "Objective-timers", "6-objective-timers.png")

    # 7. Centre of champ select: tournament logo and team names.
    closeup(pregame, (700, 798, 1220, 1080), 1.8, "Champ select – mitten", "7-champselect-mitten.png")


if __name__ == "__main__":
    main()

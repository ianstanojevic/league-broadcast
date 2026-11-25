"""Make the 1280x640 Arenan banner (GitHub social preview, shown when the repo link is shared).

    python underhall/tools/make_banner.py

Builds an HTML page (real Cinzel / Barlow Condensed from Google Fonts), renders it with
headless Edge via capture.mjs and crops it to underhall/arenan/logo/banner.png.
Upload it under the repo's Settings -> Social preview; it is not shown in the README.
Needs underhall/raw/ingame_after.png (from capture.mjs) for the scoreboard strip.
"""
import subprocess
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
UNDERHALL = HERE.parent
WORK = UNDERHALL / "raw" / "banner"          # scratch, not in git
OUT = UNDERHALL / "arenan" / "logo" / "banner.png"
W, H = 1280, 640


def main():
    WORK.mkdir(parents=True, exist_ok=True)

    # Scoreboard strip from the real in-game capture (transparent background).
    ingame = Image.open(UNDERHALL / "raw" / "ingame_after.png").convert("RGBA")
    ingame.crop((180, 0, 1740, 100)).save(WORK / "scoreboard.png")
    gladiator = (UNDERHALL / "arenan" / "logo" / "gladiator.png").as_uri()

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Barlow+Condensed:wght@500;600&display=block" rel="stylesheet">
<style>
  html, body {{ margin: 0; background: transparent; }}
  .b {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; overflow: hidden;
        background: radial-gradient(ellipse at 30% 40%, #22314d 0%, #0e1628 55%, #070c17 100%); }}
  .rule {{ position: absolute; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, transparent, #C9A24A 15%, #F0D78C 50%, #C9A24A 85%, transparent); }}
  .logo {{ position: absolute; left: 84px; top: 96px; width: 300px; height: 300px;
           border: 3px solid #C9A24A; box-shadow: 0 0 0 8px #0B1220, 0 0 0 10px #C9A24A66, 0 18px 40px #000a; }}
  .logo img {{ width: 100%; height: 100%; display: block; }}
  .text {{ position: absolute; left: 450px; top: 112px; right: 60px; }}
  .title {{ font-family: Cinzel, serif; font-weight: 700; font-size: 132px; line-height: 1; letter-spacing: 14px;
            color: #F0D78C; text-shadow: 0 4px 0 #6b5320, 0 10px 30px #000c; }}
  .line {{ margin: 26px 0 22px; height: 2px; width: 560px; background: linear-gradient(90deg, #C9A24A, transparent); }}
  .sub {{ font-family: "Barlow Condensed", sans-serif; font-weight: 600; font-size: 40px; color: #EDE6D6; letter-spacing: 1px; }}
  .tags {{ margin-top: 14px; font-family: "Barlow Condensed", sans-serif; font-weight: 500; font-size: 28px;
           color: #C9A24A; letter-spacing: 3px; text-transform: uppercase; }}
  .board {{ position: absolute; left: 50%; bottom: 46px; transform: translateX(-50%); width: 1120px; }}
  .board img {{ width: 100%; display: block; filter: drop-shadow(0 8px 18px #000c); }}
</style></head><body>
<div class="b" id="ready">
  <div class="rule" style="top:0"></div>
  <div class="rule" style="bottom:0"></div>
  <div class="logo"><img src="{gladiator}"></div>
  <div class="text">
    <div class="title">ARENAN</div>
    <div class="line"></div>
    <div class="sub">League Broadcast-stil för våra 5v5-customkvällar</div>
    <div class="tags">Champ select · In-game · OBS</div>
  </div>
  <div class="board"><img src="scoreboard.png"></div>
</div></body></html>"""
    page = WORK / "banner.html"
    page.write_text(html, encoding="utf-8")

    shot = WORK / "banner_full.png"
    subprocess.run(["node", str(HERE / "capture.mjs"), page.as_uri(), str(shot), "4"], check=True)
    Image.open(shot).convert("RGB").crop((0, 0, W, H)).save(OUT, optimize=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()

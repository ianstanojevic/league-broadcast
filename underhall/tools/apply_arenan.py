"""Apply the "Arenan" tournament look to League Broadcast's style files.

Edits only the user-owned copies the app made when we duplicated them:
  data/style/set/ingame/Arenan.json, data/style/set/pregame/Arenan.json
  data/style/variant/ingame/GlobalScoreboardV2/Arenan.json
  data/style/variant/ingame/ChampionTabsV2/Arenan.json
  data/style/variant/pregame/BottomRowV2/Arenan.json
The look only shows on the V2 browser sources: /ingame/v2 and /pregame/v2.
Close League Broadcast before running. Safe to run again.

    python underhall/tools/apply_arenan.py            # apply
    python underhall/tools/apply_arenan.py --dry-run  # only print what would change
"""
import json
import math
import os
import shutil
import sys
from pathlib import Path

LB = Path(os.environ["APPDATA"]) / "BlueBottle" / "LeagueBroadcast" / "data" / "style"
SNAPSHOT = Path(__file__).resolve().parent.parent / "arenan" / "style"

NIGHT = "#0B1220"
BRONZE = "#C9A24A"
GOLD = "#F0D78C"
BLUE = "#2F8CFF"
RED = "#D7372B"   # brighter than the mockup's #B3261E so kill and gold numbers stay readable
MARBLE = "#EDE6D6"

DISPLAY_FONT = "Cinzel"            # team names, titles
NUMERIC_FONT = "Barlow Condensed"  # kills, gold, timers, everything else

# Overrides for League Broadcast's own theme variables. customCss is injected as a
# page-wide stylesheet, so this block rethemes every in-game element.
ROOT_CSS = f""":root {{
  --lb-overlay-surface-base: {NIGHT}F0;
  --lb-overlay-surface-glass: {NIGHT}DB;
  --lb-overlay-surface-strong: #070C17F7;
  --lb-overlay-surface-opaque: #070C17;
  --lb-overlay-surface-raised: #16203AF0;
  --lb-overlay-surface-muted: #1E2A44E6;
  --lb-overlay-surface-scrim: #070C17B8;
  --lb-overlay-border-subtle: {BRONZE}66;
  --lb-overlay-border-strong: {BRONZE}B3;
  --lb-overlay-border-width: 1.5px;
  --lb-overlay-divider: {BRONZE}33;
  --lb-overlay-highlight: {GOLD};
  --lb-overlay-highlight-soft: {BRONZE};
  --lb-overlay-warning: {GOLD};
  --lb-overlay-brand-primary: {BRONZE};
  --lb-overlay-brand-secondary: {GOLD};
  --lb-overlay-info: {BLUE};
  --lb-overlay-text-primary: {MARBLE};
  --lb-overlay-text-secondary: #CFC4AA;
  --lb-overlay-text-muted: #8FA3C4;
  --lb-overlay-team-neutral: {BRONZE};
  --lb-overlay-team-blue: {BLUE};
  --lb-overlay-team-blue-soft: {BLUE}38;
  --lb-overlay-team-red: {RED};
  --lb-overlay-team-red-soft: {RED}38;
  --lb-font-display: "{DISPLAY_FONT}", Georgia, serif;
  --lb-font-numeric: "{NUMERIC_FONT}", "Roboto Condensed", sans-serif;
  --lb-font-body: "{NUMERIC_FONT}", "Roboto Condensed", sans-serif;
}}"""

CHAMPION_TAB_COLORS = {
    "#bf0000": "var(--lb-side-red)",
    "#1d4ed8": "var(--lb-side-blue)",
    "#d6db29": GOLD,
    "#A9A9A9": "#8FA3C4",
}

BOTTOM_ROW_COLORS = {
    "#1F1F1F": NIGHT,
    "#000000": "#070C17",
    "#FFFFFF": MARBLE,
    "#6B7280": BRONZE + "59",   # score pips not yet won
}
# Champ select nodes (by editor label) that get the display font; other text gets NUMERIC_FONT.
BOTTOM_ROW_DISPLAY_NODES = {"Team Name Text", "Match Name Text"}
# Champ select boxes (by editor label) that get a bronze frame.
BOTTOM_ROW_FRAMED_NODES = {"Team Identity", "Tournament Details", "Phase Timer"}
BRONZE_BORDER = {"width": "1.5px", "style": "solid", "color": {"color": BRONZE}, "radius": ""}


def hex_to_oklch(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = lin(r), lin(g), lin(b)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return {"lightness": round(L, 6), "chroma": round(math.hypot(A, B), 6),
            "hueDegrees": round(math.degrees(math.atan2(B, A)) % 360, 3), "alpha": 1}


def frame_stops():
    return [{"offset": o, "color": hex_to_oklch(c)}
            for o, c in ((0, BRONZE), (0.25, NIGHT), (0.75, NIGHT), (1, GOLD))]


def walk(node, fn):
    """Call fn(dict) for every dict in the tree."""
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def edit_set(d):
    g = d["Global"]
    g["color"] = {"blueSideColor": BLUE + "FF", "redSideColor": RED + "FF", "neutralColor": BRONZE + "FF"}
    g["fontFamily"] = NUMERIC_FONT
    for frame in ("pipFrame", "splitDivider"):
        g["cameraFrames"][frame]["stops"] = frame_stops()


def edit_scoreboard(d):
    d["container"]["customCss"] = ROOT_CSS

    def fonts(n):
        if n.get("fontFamily") == "var(--lb-font-display)":
            n["fontFamily"] = DISPLAY_FONT
        elif n.get("fontFamily") in ("var(--lb-font-numeric)", "var(--lb-font-body)"):
            n["fontFamily"] = NUMERIC_FONT
    walk(d, fonts)

    # Bronze frame around the tournament emblem in the middle.
    icon = d["topContent"]["tournamentIcon"]["container"]
    icon["border"] = {"width": "1.5px", "style": "solid", "color": {"color": BRONZE}, "radius": "var(--lb-radius-xs)"}


def edit_champion_tabs(d):
    def colors(n):
        c = n.get("color")
        if isinstance(c, str) and c in CHAMPION_TAB_COLORS:
            n["color"] = CHAMPION_TAB_COLORS[c]
    walk(d, colors)


def walk_nodes(node, fn):
    """Call fn(label, node) for every styled node (a dict with a _node header)."""
    if isinstance(node, dict):
        if "_node" in node:
            fn(node["_node"].get("label", ""), node)
        for v in node.values():
            walk_nodes(v, fn)


def edit_bottom_row(d):
    d["customCss"] = ROOT_CSS
    d["showTournament"] = True   # tournament icon in the middle of champ select
    # Give the tournament icon room: the centre column is 5vw by default and the icon
    # shrank to ~29 px at 1080p.
    d["center"]["container"]["container"]["sizing"]["width"] = "8vw"   # "Tournament Details"
    d["center"]["logo"]["container"]["sizing"]["width"] = "6.5vw"

    def colors(n):
        c = n.get("color")
        if isinstance(c, str) and c.upper() in BOTTOM_ROW_COLORS:
            n["color"] = BOTTOM_ROW_COLORS[c.upper()]
    walk(d, colors)

    def per_node(label, node):
        font = DISPLAY_FONT if label in BOTTOM_ROW_DISPLAY_NODES else NUMERIC_FONT
        if "fontFamily" in node:
            node["fontFamily"] = font
        for key, section in node.items():
            if key == "_node" or not isinstance(section, dict) or "_node" in section:
                continue
            walk(section, lambda n: n.__setitem__("fontFamily", font) if "fontFamily" in n else None)
        if label in BOTTOM_ROW_FRAMED_NODES and isinstance(node.get("container"), dict):
            radius = (node["container"].get("border") or {}).get("radius", "")
            node["container"]["border"] = dict(BRONZE_BORDER, radius=radius)
    walk_nodes(d, per_node)


TARGETS = [
    ("set/ingame/Arenan.json", edit_set),
    ("variant/ingame/GlobalScoreboardV2/Arenan.json", edit_scoreboard),
    ("variant/ingame/ChampionTabsV2/Arenan.json", edit_champion_tabs),
    ("set/pregame/Arenan.json", edit_set),
    ("variant/pregame/BottomRowV2/Arenan.json", edit_bottom_row),
]


def main():
    dry = "--dry-run" in sys.argv
    for rel, fn in TARGETS:
        path = LB / rel
        before = path.read_text(encoding="utf-8")
        data = json.loads(before)
        fn(data)
        after = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        changed = after != before
        print(f"{'would change' if dry and changed else 'changed' if changed else 'unchanged'}: {rel}")
        if not dry and changed:
            path.write_text(after, encoding="utf-8")
        if not dry:
            out = SNAPSHOT / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, out)


if __name__ == "__main__":
    main()

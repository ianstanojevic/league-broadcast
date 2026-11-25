"""Draw the Arenan tournament emblem: a laurel wreath around two crossed swords.

    python tools/make_logo.py

Writes to arenan/logo/:
  arenan-emblem.svg        transparent, for the overlays (they sit on night blue)
  arenan-emblem-badge.svg  on a night-blue disc with a bronze ring, for Discord, thumbnails, etc.
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "arenan" / "logo"

NIGHT = "#0B1220"
BRONZE = "#C9A24A"
BRONZE_DARK = "#9A7A32"
GOLD = "#F0D78C"
MARBLE = "#EDE6D6"
MARBLE_SHADE = "#C9BFA8"
LEATHER = "#5A3E22"

C = 256          # centre of the 512 x 512 canvas
R = 172          # radius of the wreath's stem


def pt(angle_deg, r, cx=C, cy=C):
    a = math.radians(angle_deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def leaf(x, y, angle_deg, length, width, fill):
    """A pointed leaf with its base at (x, y), pointing along angle_deg."""
    h = length
    w = width / 2
    d = (f"M0,0 C{h * 0.25:.1f},{-w:.1f} {h * 0.75:.1f},{-w:.1f} {h:.1f},0 "
         f"C{h * 0.75:.1f},{w:.1f} {h * 0.25:.1f},{w:.1f} 0,0 Z")
    return (f'<path d="{d}" fill="{fill}" '
            f'transform="translate({x:.1f},{y:.1f}) rotate({angle_deg:.1f})"/>')


def branch(start, end):
    """One laurel branch along the circle from angle start to angle end (degrees)."""
    parts = []
    sx, sy = pt(start, R)
    ex, ey = pt(end, R)
    sweep = 1 if end > start else 0
    parts.append(f'<path d="M{sx:.1f},{sy:.1f} A{R},{R} 0 0 {sweep} {ex:.1f},{ey:.1f}" '
                 f'fill="none" stroke="{BRONZE_DARK}" stroke-width="5" stroke-linecap="round"/>')
    steps = 9
    direction = 1 if end > start else -1
    for i in range(steps):
        t = i / (steps - 1)
        a = start + (end - start) * (0.04 + 0.9 * t)
        x, y = pt(a, R)
        tangent = a + 90 * direction          # direction the branch grows
        size = 1.0 - 0.45 * t                 # leaves shrink toward the tip
        length, width = 58 * size, 22 * size
        parts.append(leaf(x, y, tangent - 38 * direction, length, width, BRONZE))   # outer leaf
        parts.append(leaf(x, y, tangent + 42 * direction, length * 0.9, width * 0.9, GOLD))  # inner leaf
    # a berry-like bud at the tip
    tx, ty = pt(end, R)
    parts.append(leaf(tx, ty, end + 90 * direction, 34, 14, GOLD))
    return "\n".join(parts)


def sword(rotation):
    """A gladius, tip up, drawn around the centre and rotated."""
    blade = (f'<path d="M{C - 15},{C + 40} L{C - 15},{C - 120} L{C},{C - 170} '
             f'L{C + 15},{C - 120} L{C + 15},{C + 40} Z" fill="{MARBLE}"/>'
             f'<path d="M{C},{C - 160} L{C},{C + 38}" stroke="{MARBLE_SHADE}" stroke-width="4"/>')
    guard = (f'<rect x="{C - 46}" y="{C + 40}" width="92" height="16" rx="6" fill="{BRONZE}"/>'
             f'<rect x="{C - 46}" y="{C + 40}" width="92" height="5" rx="2" fill="{GOLD}"/>')
    grip = f'<rect x="{C - 10}" y="{C + 56}" width="20" height="58" rx="5" fill="{LEATHER}"/>'
    grip_bands = "".join(
        f'<rect x="{C - 11}" y="{C + 64 + 14 * i}" width="22" height="4" rx="2" fill="{BRONZE_DARK}"/>'
        for i in range(3))
    pommel = (f'<circle cx="{C}" cy="{C + 126}" r="16" fill="{BRONZE}"/>'
              f'<circle cx="{C - 4}" cy="{C + 122}" r="5" fill="{GOLD}"/>')
    return (f'<g transform="rotate({rotation} {C} {C})">'
            f'{blade}{guard}{grip}{grip_bands}{pommel}</g>')


def emblem():
    return "\n".join([
        branch(118, 252),   # left branch, bottom-left up to the top-left
        branch(62, -72),    # right branch, mirrored
        sword(-38),
        sword(38),
    ])


def svg(body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">\n'
            f'<title>{title}</title>\n{body}\n</svg>\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "arenan-emblem.svg").write_text(svg(emblem(), "Arenan"), encoding="utf-8")
    badge = (f'<circle cx="{C}" cy="{C}" r="250" fill="{NIGHT}"/>'
             f'<circle cx="{C}" cy="{C}" r="238" fill="none" stroke="{BRONZE}" stroke-width="6"/>'
             f'<g transform="translate({C},{C}) scale(0.86) translate({-C},{-C})">{emblem()}</g>')
    (OUT / "arenan-emblem-badge.svg").write_text(svg(badge, "Arenan"), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()

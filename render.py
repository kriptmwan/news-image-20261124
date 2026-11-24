#!/usr/bin/env python3
"""Render the news-image-20261124 front page: 1024x1024 newspaper, PIL only.

Layout (locked from the 20261123 Gate 1 review, same geometry):
  1024x1024, margins 36, masthead band ~110px, 2x3 grid of 464x232 panels,
  60px icon left slot, kicker 18px, headline 36px bold max 2 lines,
  subline 26px one line full panel width, footer hairline + ALSO 26px.
Palette: paper #FAF7F0, ink #141414, accent #1B4F8A (rules/kickers only).
Deterministic: no randomness, no timestamps, fixed layout; the width check
raises loudly on any overflow instead of silently clipping.
"""
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 36
PAPER = (250, 247, 240)
INK = (20, 20, 20)
ACCENT = (27, 79, 138)
RULE = (120, 120, 120)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
REG = FONT_DIR + "DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def check(draw, s, f, limit, what):
    w = text_w(draw, s, f)
    if w > limit:
        raise SystemExit(f"WIDTH FAIL {what}: {w:.0f}px > {limit}px :: {s!r}")
    return w


def letterspaced(draw, xy, s, f, fill, spacing=3):
    """Draw text with manual letter spacing; returns total width."""
    x, y = xy
    total = 0
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill)
        w = draw.textlength(ch, font=f)
        x += w + spacing
        total += w + spacing
    return total - spacing if s else 0


# ---------------- icons (PIL primitives, 60x60 box) ----------------

def icon_chart(d, x, y, c):
    # three ascending bars + arrow
    d.rectangle([x + 6, y + 34, x + 16, y + 54], fill=c)
    d.rectangle([x + 24, y + 24, x + 34, y + 54], fill=c)
    d.rectangle([x + 42, y + 12, x + 52, y + 54], fill=c)
    d.line([x + 4, y + 30, x + 30, y + 14, x + 54, y + 4], fill=c, width=4)
    d.polygon([(x + 54, y + 4), (x + 44, y + 2), (x + 54, y + 14)], fill=c)


def icon_halt(d, x, y, c):
    # ascending bars + a halt bar across
    d.rectangle([x + 6, y + 36, x + 16, y + 54], fill=c)
    d.rectangle([x + 24, y + 26, x + 34, y + 54], fill=c)
    d.rectangle([x + 42, y + 16, x + 52, y + 54], fill=c)
    d.rectangle([x + 2, y + 8, x + 58, y + 14], fill=c)


def icon_jet(d, x, y, c):
    # simple jet silhouette, nose right
    d.polygon([(x + 4, y + 30), (x + 34, y + 18), (x + 56, y + 28),
               (x + 34, y + 34), (x + 30, y + 44), (x + 22, y + 36),
               (x + 10, y + 40), (x + 6, y + 34)], fill=c)
    d.polygon([(x + 30, y + 22), (x + 38, y + 6), (x + 42, y + 22)], fill=c)


def icon_ballot(d, x, y, c):
    # ballot box + paper
    d.rectangle([x + 8, y + 26, x + 52, y + 54], outline=c, width=4)
    d.line([x + 22, y + 26, x + 38, y + 26], fill=PAPER, width=4)
    d.rectangle([x + 22, y + 6, x + 38, y + 28], fill=c)
    d.line([x + 26, y + 14, x + 34, y + 14], fill=PAPER, width=2)
    d.line([x + 26, y + 20, x + 34, y + 20], fill=PAPER, width=2)
    d.line([x + 16, y + 40, x + 44, y + 40], fill=c, width=3)


def icon_flag(d, x, y, c):
    # flag on a pole
    d.line([x + 12, y + 4, x + 12, y + 56], fill=c, width=4)
    d.polygon([(x + 14, y + 6), (x + 54, y + 14), (x + 14, y + 26)], fill=c)
    d.rectangle([x + 30, y + 34, x + 52, y + 56], outline=c, width=3)


def icon_gavel(d, x, y, c):
    # gavel: head + handle, diagonal
    d.rectangle([x + 8, y + 10, x + 40, y + 24], fill=c)
    d.rectangle([x + 30, y + 22, x + 38, y + 54], fill=c)
    d.rectangle([x + 4, y + 6, x + 44, y + 12], fill=c)


ICONS = {
    "chart": icon_chart,
    "halt": icon_halt,
    "jet": icon_jet,
    "ballot": icon_ballot,
    "flag": icon_flag,
    "gavel": icon_gavel,
}

# ---------------- content: 6 verified 24 Nov 2026 stories ----------------
# headline: 2 lines max, each <= ~14 chars at 36px bold in the 356px text column.
# subline: 1 line, full panel width 432px at 26px.
PANELS = [
    dict(kicker="MARKETS \u00b7 TOKYO", icon="chart",
         head=["TOKYO ROARS", "BACK +3.8%"],
         sub="Tokyo reopens; chips +8%"),
    dict(kicker="MARKETS \u00b7 SEOUL", icon="halt",
         head=["KOSPI SURGE", "HALTS BUYING"],
         sub="Kospi +5.6% trips 5-min sidecar"),
    dict(kicker="SECURITY", icon="jet",
         head=["KOREA", "SCRAMBLES JETS"],
         sub="Russian planes enter air zone"),
    dict(kicker="PACIFIC", icon="ballot",
         head=["PNG VOTES ON", "BOUGAINVILLE"],
         sub="Ratify 2019 vote: 97.7% for split"),
    dict(kicker="DIPLOMACY", icon="flag",
         head=["SWISS OFFICE", "UNDER THREAT"],
         sub="Kim Yo Jong threatens closure"),
    dict(kicker="LAW", icon="gavel",
         head=["VOTE OFFICIAL", "TO BE ARRESTED"],
         sub="Forged count sheet, court says"),
]

FOOTER = [
    "India markets shut for Guru Nanak Jayanti",
    "Taiwan cuts margin threshold to 120% today",
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_title = font(BOLD, 40)
    f_date = font(BOLD, 56)
    f_kicker = font(BOLD, 18)
    f_head = font(BOLD, 36)
    f_sub = font(REG, 26)
    f_also = font(BOLD, 26)
    f_foot = font(REG, 26)

    # ---- masthead ----
    title = "THE WORLD IN ONE DAY"
    check(d, title, f_title, W - 2 * MARGIN, "masthead title")
    d.text(((W - text_w(d, title, f_title)) / 2, 30), title, font=f_title, fill=INK)

    # date: largest size in [56,54,52,50,48] that fits the usable width
    date = "TUESDAY, 24 NOVEMBER 2026"
    date_size = None
    for sz in (56, 54, 52, 50, 48):
        f_try = font(BOLD, sz)
        if text_w(d, date, f_try) <= W - 2 * MARGIN:
            date_size = sz
            f_date = f_try
            break
    if date_size is None:
        raise SystemExit("WIDTH FAIL masthead date: no size fits")
    print(f"date font size: {date_size}px")
    d.text(((W - text_w(d, date, f_date)) / 2, 78), date, font=f_date, fill=INK)
    d.line([(MARGIN, 148), (W - MARGIN, 148)], fill=INK, width=3)

    # ---- grid ----
    px, py = MARGIN, 164
    pw, ph = 464, 232
    gx, gy = 24, 14
    text_x_off = 92          # icon 60 + gaps
    text_w_limit = pw - text_x_off - 16   # 356px beside the icon
    sub_w_limit = pw - 32                 # 432px full panel width
    content_h = 154          # kicker 22 + gap 6 + headline 2x42 + gap 10 + subline 32
    top_off = (ph - content_h) // 2       # 39 — vertically centre the block

    for i, p in enumerate(PANELS):
        col, row = i % 2, i // 2
        x = px + col * (pw + gx)
        y = py + row * (ph + gy)
        # panel hairline frame
        d.rectangle([x, y, x + pw - 1, y + ph - 1], outline=RULE, width=1)
        cy = y + top_off
        # icon, 60x60 at left
        ICONS[p["icon"]](d, x + 16, cy, INK)
        # kicker (letterspaced, accent)
        kw = letterspaced(d, (x + text_x_off, cy + 2), p["kicker"], f_kicker, ACCENT)
        if kw > text_w_limit:
            raise SystemExit(f"WIDTH FAIL kicker {i+1}: {kw:.0f}px > {text_w_limit}px")
        # headline, 2 lines, 36px bold
        hy = cy + 28
        for li, line in enumerate(p["head"]):
            check(d, line, f_head, text_w_limit, f"headline {i+1} line {li+1}")
            d.text((x + text_x_off, hy + li * 42), line, font=f_head, fill=INK)
        # subline, one line, full panel width
        check(d, p["sub"], f_sub, sub_w_limit, f"subline {i+1}")
        d.text((x + 16, cy + 122), p["sub"], font=f_sub, fill=INK)

    grid_bottom = py + 2 * (ph + gy) + ph   # 164 + 2*246 + 232 = 888
    assert grid_bottom == 888, grid_bottom

    # ---- footer ----
    fy = 902
    d.line([(MARGIN, fy), (W - MARGIN, fy)], fill=INK, width=2)
    d.text((MARGIN, fy + 10), "ALSO", font=f_also, fill=ACCENT)
    for j, line in enumerate(FOOTER):
        check(d, line, f_foot, W - 2 * MARGIN, f"footer {j+1}")
        d.text((MARGIN, fy + 40 + j * 28), line, font=f_foot, fill=INK)

    img.save("entry.png")
    print("wrote entry.png 1024x1024")


if __name__ == "__main__":
    main()

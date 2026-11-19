#!/usr/bin/env python3
"""One image that sums up the world news of Thursday 19 November 2026.

The picture is a broadsheet front page called THE DAILY ORBIT: a Vice City
sunset panel beside the lead story (the worldwide GTA VI launch), four
story cards under it, and a wire strip along the bottom. Everything is
drawn pixel by pixel with the Python 3 standard library only -- a small
5x7 bitmap font, Bresenham lines, filled circles and one PNG encoder --
and written to /output/entry.png (PNG, 1024 x 1024). Deterministic: a
fixed-seed generator places the stars and lit windows, so every run
produces the same bytes.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 242, 231)
PAPER_SHADE = (238, 230, 214)
INK = (29, 39, 51)
MUTED = (105, 112, 120)
RED = (179, 35, 42)
NAVY = (24, 42, 66)
TEAL = (15, 118, 110)
GOLD = (217, 119, 6)
CREAM = (250, 246, 236)
SKYLINE = (26, 11, 46)


# ---------------------------------------------------------------- PNG out

def encode_png(width, height, buf):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    stride = width * 3
    raw = b"".join(b"\x00" + bytes(buf[y * stride:(y + 1) * stride])
                   for y in range(height))
    head = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", head) +
            chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.buf = bytearray(bytes(colour) * (width * height))

    def put(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        x0, x1 = max(x, 0), min(x + w, self.w)
        y0, y1 = max(y, 0), min(y + h, self.h)
        if x1 <= x0 or y1 <= y0:
            return
        run = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.buf[base:base + len(run)] = run

    def frame(self, x, y, w, h, colour, thick=2):
        self.rect(x, y, w, thick, colour)
        self.rect(x, y + h - thick, w, thick, colour)
        self.rect(x, y, thick, h, colour)
        self.rect(x + w - thick, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for ox in range(thick):
                for oy in range(thick):
                    self.put(x0 + ox, y0 + oy, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.put(xx, yy, colour)

    def ring(self, cx, cy, r, colour, thick=2):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - thick) ** 2 < d2 <= r ** 2:
                    self.put(xx, yy, colour)


# ---------------------------------------------------------------- font
# A 5x7 bitmap font, one tuple of seven 5-character rows per glyph.

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ",": (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    ":": (".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."),
    ";": (".....", "..#..", "..#..", ".....", "..#..", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "€": (".###.", "#....", "#####", "#....", "#####", "#....", ".###."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "·": (".....", ".....", ".....", "..#..", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, colour):
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, cell in enumerate(row):
                if cell == "#":
                    cv.rect(cx + col_i * scale, y + row_i * scale,
                            scale, scale, colour)
        cx += 6 * scale
    return cx - scale


def draw_centered(cv, cx, y, text, scale, colour):
    return draw_text(cv, cx - text_width(text, scale) // 2, y, text,
                     scale, colour)


def wrap(text, scale, max_width):
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(cv, x, y, text, scale, colour, max_width, line_step):
    for line in wrap(text, scale, max_width):
        draw_text(cv, x, y, line, scale, colour)
        y += line_step
    return y


# ---------------------------------------------------------------- helpers

class Lcg:
    """Tiny deterministic generator for stars and lit windows."""

    def __init__(self, seed):
        self.state = seed

    def next(self, bound):
        self.state = (self.state * 1103515245 + 12345) % (2 ** 31)
        return self.state % bound


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def palm(cv, base_x, base_y, top_x, top_y, colour):
    """A palm silhouette: a leaning trunk and six fronds from its crown."""
    steps = 14
    for i in range(steps + 1):
        t = i / steps
        x = round(base_x + (top_x - base_x) * t)
        y = round(base_y + (top_y - base_y) * t)
        cv.rect(x - 3, y - 3, 7, 7, colour)
    for dx, dy in ((-78, -18), (-54, -40), (-20, -52), (20, -52),
                   (54, -38), (78, -14)):
        cv.line(top_x, top_y, top_x + dx, top_y + dy + 34, colour, thick=3)


def sunset_panel(cv, x, y, w, h):
    """The lead picture: a retro Vice City sunset over a skyline."""
    stops = [(43, 16, 69), (110, 32, 92), (196, 52, 106),
             (232, 84, 122), (255, 158, 94), (255, 217, 122)]
    bands = 30
    for i in range(bands):
        t = i / (bands - 1)
        pos = t * (len(stops) - 1)
        lo = int(pos)
        hi = min(lo + 1, len(stops) - 1)
        colour = lerp(stops[lo], stops[hi], pos - lo)
        cv.rect(x, y + i * h // bands, w, h // bands + 1, colour)

    rng = Lcg(20261119)
    for _ in range(46):  # stars in the dark top of the sky
        sx = x + 8 + rng.next(w - 16)
        sy = y + 6 + rng.next(h // 4)
        cv.put(sx, sy, CREAM)
        cv.put(sx + 1, sy, CREAM)

    sun_cx, sun_cy, sun_r = x + w // 2, y + int(h * 0.58), 52
    cv.disc(sun_cx, sun_cy, sun_r, (255, 226, 150))
    for i, gap_y in enumerate((0.62, 0.74, 0.86)):  # retro sun stripes
        gy = y + int(h * gap_y)
        cv.rect(x, gy, w, 3 + i * 2, lerp(stops[3], stops[4], 0.4))

    horizon = y + h - 58
    rng = Lcg(6119)
    bx = x + 6
    while bx < x + w - 20:  # skyline
        bw = 22 + rng.next(26)
        bh = 26 + rng.next(64)
        cv.rect(bx, horizon - bh, bw, bh + 58, SKYLINE)
        for _ in range(bh // 9):
            wx = bx + 3 + rng.next(max(bw - 6, 1))
            wy = horizon - bh + 4 + rng.next(max(bh - 8, 1))
            cv.rect(wx, wy, 3, 4, (255, 205, 92))
        bx += bw + 4 + rng.next(8)
    cv.rect(x, horizon + 40, w, h - (horizon - y) - 40 + 58, SKYLINE)

    palm(cv, x + 40, y + h, x + 86, y + h - 196, SKYLINE)
    palm(cv, x + w - 36, y + h, x + w - 88, y + h - 176, SKYLINE)
    cv.frame(x, y, w, h, INK, thick=3)


# ---------------------------------------------------------------- page

def story_card(cv, x, y, w, h, label, colour, headline, body):
    cv.rect(x, y, w, h, PAPER_SHADE)
    cv.rect(x, y, w, 6, colour)
    draw_text(cv, x + 18, y + 16, label, 2, colour)
    hy = draw_wrapped(cv, x + 18, y + 40, headline, 3, INK, w - 36, 27)
    draw_wrapped(cv, x + 18, hy + 6, body, 2, INK, w - 36, 19)


def build():
    cv = Canvas(W, H, PAPER)

    # Masthead
    cv.rect(0, 0, W, 118, RED)
    draw_centered(cv, W // 2, 16, "THE DAILY ORBIT", 7, CREAM)
    draw_centered(cv, W // 2, 84,
                  "THURSDAY 19 NOVEMBER 2026 - THE WORLD IN ONE PICTURE",
                  2, CREAM)
    cv.rect(0, 118, W, 4, INK)

    # Lead story: text left, sunset panel right
    draw_text(cv, 40, 142, "THE LEAD - LAUNCH DAY", 2, RED)
    ly = 168
    for line in ("GTA VI", "LAUNCHES", "WORLDWIDE"):
        draw_text(cv, 40, ly, line, 6, INK)
        ly += 52
    body = ("AFTER A 13-YEAR WAIT, THE MOST ANTICIPATED GAME ON EARTH "
            "UNLOCKS AT MIDNIGHT, TIME ZONE BY TIME ZONE. NEW ZEALAND "
            "PLAYED FIRST; THE AMERICAS WAKE UP INSIDE VICE CITY, "
            "ROCKSTAR'S SUN-SOAKED LEONIDA, WITH LUCIA AND JASON AT "
            "THE WHEEL.")
    by = draw_wrapped(cv, 40, ly + 8, body, 2, INK, 556, 19)
    chips = ("METACRITIC 99", "PS5 + XBOX", "$79.99")
    cx = 40
    for chip in chips:
        cw = text_width(chip, 2) + 20
        if cx + cw > 612:
            cx = 40
            by += 34
        cv.frame(cx, by, cw, 26, TEAL, thick=2)
        draw_text(cv, cx + 10, by + 6, chip, 2, TEAL)
        cx += cw + 12
    sunset_panel(cv, 636, 142, 348, 322)
    cv.rect(40, 478, W - 80, 3, INK)

    # Four story cards, two by two
    cards = [
        ("WORLD", TEAL, "TRUMP, XI + PUTIN MEET IN SHENZHEN",
         "TRILATERAL TALKS AT THE APEC SUMMIT, PLUS A FIRST "
         "TRUMP-PUTIN ONE-ON-ONE SINCE ALASKA."),
        ("CONFLICT", RED, "US + IRAN TRADE FIRE IN THE GULF",
         "IRAN WIDENS STRIKES TO BAHRAIN + KUWAIT AFTER A US HIT "
         "ON QESHM. TANKERS HIT IN HORMUZ."),
        ("SPACE", NAVY, "VOYAGER 1 REACHES ONE LIGHT-DAY",
         "LAUNCHED IN 1977, THE FARTHEST HUMAN-MADE OBJECT CROSSES "
         "A NEW FRONTIER TODAY."),
        ("US POLITICS", GOLD, "JEFFRIES SET TO LEAD THE HOUSE",
         "DEMOCRATS NOMINATE HIM AS THE FIRST AFRICAN-AMERICAN "
         "SPEAKER OF THE HOUSE."),
    ]
    cw, chh, gap = 462, 168, 16
    for i, (label, colour, head, body) in enumerate(cards):
        x = 40 + (i % 2) * (cw + gap)
        y = 492 + (i // 2) * (chh + gap)
        story_card(cv, x, y, cw, chh, label, colour, head, body)

    # Wire strip
    wy = 860
    cv.rect(0, wy, W, 108, NAVY)
    draw_text(cv, 40, wy + 14, "AROUND THE WORLD", 2, GOLD)
    wire = [
        "THE HAGUE: WORLD COURT RULES IN THE GAMBIA V. MYANMAR GENOCIDE CASE",
        "BRUSSELS: EU PROPOSES €45BN UKRAINE LOAN TIED TO RUSSIAN REPARATIONS",
        "INDIA: CYCLONE AKVAN NEARS THE EAST COAST UNDER A RED WARNING",
    ]
    iy = wy + 42
    for item in wire:
        cv.rect(40, iy + 3, 8, 8, GOLD)
        draw_text(cv, 58, iy, item, 2, CREAM)
        iy += 24

    draw_centered(cv, W // 2, 982,
                  "ONE DAY - ONE PICTURE - DRAWN BY A STDLIB-ONLY PYTHON PROGRAM",
                  2, MUTED)
    return encode_png(W, H, cv.buf)


def main():
    data = build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()

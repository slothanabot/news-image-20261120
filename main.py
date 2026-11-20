#!/usr/bin/env python3
"""news-image-20261120 (account B / keen-panda-72): draw one 1024x1024 PNG
summing up the world news of Friday 20 November 2026.

Design (deliberately unlike a newspaper grid): a paper "atlas" page with a
masthead, two lead panels, a large world map across the middle carrying
numbered markers for all 36 stories, and a region-grouped ledger below it.

Pure standard library (zlib/struct/os/math). No network, no randomness, no
clock: two runs write byte-identical PNGs. Output goes to $MAKEFUN_OUTPUT_DIR
when set, else /output/entry.png (the grader sandbox has a read-only CWD).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER   = (242, 236, 221)   # warm cream page
INK     = (20, 38, 63)      # deep navy ink
INK_SOFT = (58, 74, 96)
RED     = (179, 52, 42)     # lead red
TEAL    = (22, 66, 79)      # map ocean
TEAL_DK = (16, 52, 63)
LAND    = (232, 217, 168)   # sand continents
LAND_LN = (190, 168, 110)
GOLD    = (200, 155, 60)
WHITE   = (255, 255, 255)
PANEL   = (247, 243, 232)
RULE    = (120, 110, 88)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 rows of 5 pixels, '#' on, '.' off. Written out by hand for
# this entry (uppercase, lowercase, digits, punctuation).
FONT = {
' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
'C': (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
'D': ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
'0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
'1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
'2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
'3': ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
'4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
'5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
'6': ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
'7': ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
'8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
'9': (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
}

FONT.update({
'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
'c': (".....", ".....", ".###.", "#....", "#....", "#...#", ".###."),
'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
'g': (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
'j': ("...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."),
'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
't': ("..#..", "..#..", ".###.", "..#..", "..#..", "..#..", "...#."),
'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
'y': (".....", "#...#", "#...#", ".#.#.", "..#..", "..#..", ".##.."),
'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
'!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
'"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
'#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
'$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
'%': ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#.##."),
'&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
"'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
'(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
'*': (".....", "..#..", "#.#.#", ".###.", "#.#.#", "..#..", "....."),
'+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
'-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
'.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
'/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
';': (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
'?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
'@': (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."),
'=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
'~': (".....", ".....", ".#..#", "##.#.", ".....", ".....", "....."),
'_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
'<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
'>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
'[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
'|': ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
})

def text_w(s, scale):
    """Pixel width of string s rendered at font scale."""
    return len(s) * 6 * scale - scale

# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        for i in range(w * h):
            self.buf[i * 3:i * 3 + 3] = bytes(bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(c)

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + (x1 - x0) * 3] = row

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r:
                        self.set(xx, yy, c)

    def polyfill(self, pts, c):
        """Scanline fill of a polygon given as [(x, y), ...]."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa, xb = int(math.ceil(xs[k])), int(math.floor(xs[k + 1]))
                if xb >= xa:
                    self.fill_rect(xa, y, xb - xa + 1, 1, c)

    def polyline(self, pts, c, close=True):
        n = len(pts)
        rng = range(n) if close else range(n - 1)
        for i in rng:
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n] if close else pts[i + 1]
            self.line(x0, y0, x1, y1, c)

    def text(self, x, y, s, c, scale=1):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT['?'])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '#':
                        self.fill_rect(cx + col * scale, y + r * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx

    def text_c(self, cx, y, s, c, scale=1):
        """Centred text."""
        self.text(cx - text_w(s, scale) // 2, y, s, c, scale)

    def wrap(self, x, y, s, c, scale, maxw, lh):
        """Word-wrap text; returns y after the last line."""
        words, line, yy = s.split(' '), '', y
        for wd in words:
            trial = (line + ' ' + wd).strip()
            if text_w(trial, scale) <= maxw or not line:
                line = trial
            else:
                self.text(x, yy, line, c, scale)
                yy += lh
                line = wd
        if line:
            self.text(x, yy, line, c, scale)
            yy += lh
        return yy

def png_bytes(cv):
    def chunk(typ, data):
        out = struct.pack('>I', len(data)) + typ + data
        return out + struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))

# ------------------------------------------------------------- story data
# (number, lon, lat, pixel offset for crowded spots, group, ledger label)
# Labels are the verified 20 Nov 2026 facts, kept short and hype-free.
STORIES = [
 (1,   86, 20.0, (0, 0),   "ASIA", "Cyclone Akvan: 300,000 flee Odisha"),
 (2, -122, 37.0, (0, 0),   "TECH & BUSINESS", "Anthropic debuts at ~$1.5T valuation"),
 (3,  116, 40.0, (0, 0),   "WORLD", "First Trump-Xi-Putin three-way summit"),
 (4,   96, 21.0, (0, 0),   "WORLD", "ICJ rules Myanmar committed genocide"),
 (5,   51, 35.0, (0, 0),   "MIDDLE EAST", "Trump delays Iran war decision to 2027"),
 (6, -120,-52.0, (0, 0),   "TECH & BUSINESS", "NASA confirms Voyager 1 light-day mark"),
 (7,  140, 36.0, (0, 0),   "ASIA", "Hayabusa2 engine fault scraps landing"),
 (8, -100, 40.0, (0, 0),   "AMERICAS", "GTA 6 sales pass The Odyssey's $1.80B"),
 (9,   37, 55.0, (0, 0),   "EUROPE", "Europe ready for talks with Russia"),
 (10,  36, 45.0, (0, 0),   "EUROPE", "Crimea Bridge struck; rail disrupted"),
 (11, -17, 14.0, (0, 0),   "AFRICA", "Boat sinks off Senegal; dozens missing"),
 (12,  34, 31.0, (0, 0),   "MIDDLE EAST", "Israel ends Gaza op; strikes Hezbollah"),
 (13,  56, 26.0, (0, 0),   "MIDDLE EAST", "Tanker ablaze after Hormuz mine strike"),
 (14,  29, 41.0, (0, 0),   "WORLD", "COP31 draft drops fossil-fuel mention"),
 (15,  46, 24.0, (0, 0),   "MIDDLE EAST", "Houthis hit Riyadh; PIF tower damaged"),
 (16, -84, 39.0, (0, 0),   "AMERICAS", "Fiona the hippo dies after eating a hat"),
 (17, -77, 39.0, (0, 0),   "AMERICAS", "Trump pardons baseball legend Pete Rose"),
 (18,  77, 28.0, (0, 0),   "ASIA", "Modi hosts Prince, Princess of Wales"),
 (19, 174,-41.0, (-12, 0), "SPORT & CULTURE", "NZ 243/5, Nicholls ton on day 1 v India"),
 (20,  72, 19.0, (0, 0),   "ASIA", "Sensex +1.21%, Nifty +1.14% in rally"),
 (21, 127, 37.5, (0, 0),   "ASIA", "S. Korea clears ex-PM Han Duck-soo"),
 (22, 178,-17.0, (-16, 0), "ASIA", "Fiji declares disaster over drought"),
 (23, -66, 10.0, (0, 0),   "AMERICAS", "US, Venezuela restore military ties"),
 (24, 125.8, 39.8, (16, -8), "ASIA", "N. Korea expands uranium enrichment"),
 (25, -115, 32.0, (0, 0),   "AMERICAS", "California probes Nvidia over China"),
 (26, -75, 45.0, (0, 0),   "AMERICAS", "Canada backs AI data centres; US balks"),
 (27,   2, 49.0, (0, 0),   "TECH & BUSINESS", "Data-centre power may double by 2030"),
 (28, -30,  5.0, (0, 0),   "WORLD", "Islam largest religion by 2035: study"),
 (29,  91, 24.0, (0, 0),   "ASIA", "Fire at Yunus's ancestral home"),
 (30,  44, 41.0, (0, 0),   "ASIA", "Tbilisi blast: boy, 3, rescued alive"),
 (31,   3, 43.5, (0, 0),   "EUROPE", "One dead, 15 hurt in France tower fire"),
 (32,  35, 38.0, (0, 0),   "EUROPE", "Baykar delivers first Kizilelma jets"),
 (33,   8, 46.0, (0, 0),   "EUROPE", "Swiss drills to guard infrastructure"),
 (34,  93, 14.0, (0, 0),   "ASIA", "80,000 evacuated as Storm Dana nears"),
 (35,  30, 50.0, (0, 0),   "TECH & BUSINESS", "Musk: no Starlink, no Ukraine front"),
 (36, -0.2, 51.5, (-14, -6), "EUROPE", "England beat Croatia"),
]

GROUPS = ["ASIA", "EUROPE", "MIDDLE EAST", "AMERICAS",
          "AFRICA", "TECH & BUSINESS", "WORLD", "SPORT & CULTURE"]
GROUP_COLORS = {
    "ASIA": (179, 52, 42), "EUROPE": (31, 93, 140),
    "MIDDLE EAST": (146, 94, 20), "AMERICAS": (31, 120, 90),
    "AFRICA": (120, 70, 130), "TECH & BUSINESS": (60, 60, 130),
    "WORLD": (20, 38, 63), "SPORT & CULTURE": (150, 60, 90),
}

# ------------------------------------------------------- simplified continents
# Rough equirectangular outlines (lon, lat); stylised, not surveyed.
N_AMERICA = [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 68),
             (-100, 69), (-90, 68), (-82, 66), (-76, 62), (-68, 58),
             (-60, 55), (-55, 47), (-60, 44), (-68, 44), (-74, 39),
             (-76, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 21),
             (-94, 18), (-97, 16), (-92, 14), (-87, 13), (-83, 9),
             (-79, 8), (-82, 10), (-86, 13), (-91, 14), (-96, 16),
             (-102, 18), (-106, 22), (-110, 24), (-114, 29), (-120, 34),
             (-124, 40), (-124, 48), (-128, 52), (-134, 56), (-142, 60),
             (-152, 58), (-158, 56), (-162, 60), (-166, 62)]
GREENLAND = [(-44, 60), (-40, 64), (-32, 68), (-24, 70), (-20, 74),
             (-28, 78), (-40, 80), (-52, 78), (-58, 74), (-56, 70),
             (-52, 65), (-48, 61)]
S_AMERICA = [(-79, 9), (-74, 11), (-68, 11), (-62, 10), (-55, 6),
             (-51, 4), (-50, 0), (-44, -3), (-38, -5), (-35, -8),
             (-37, -12), (-39, -16), (-41, -22), (-46, -25), (-50, -29),
             (-55, -34), (-58, -38), (-63, -40), (-66, -45), (-68, -50),
             (-69, -53), (-72, -50), (-73, -44), (-73, -36), (-72, -28),
             (-70, -20), (-75, -15), (-78, -10), (-80, -5), (-81, -1),
             (-80, 4)]
AFRICA = [(-17, 15), (-16, 21), (-12, 27), (-8, 32), (-5, 35), (0, 36),
          (10, 37), (15, 32), (20, 32), (25, 32), (30, 31), (33, 28),
          (36, 22), (38, 18), (41, 13), (44, 11), (48, 11), (51, 10),
          (48, 5), (44, 0), (41, -5), (39, -10), (36, -16), (34, -22),
          (32, -27), (28, -32), (24, -34), (19, -35), (16, -30),
          (14, -24), (12, -18), (11, -10), (9, -2), (9, 4), (2, 6),
          (-6, 5), (-12, 8), (-15, 11)]
EUROPE = [(-10, 36), (-9, 40), (-9, 43), (-4, 44), (-2, 47), (-4, 49),
          (-1, 50), (2, 51), (4, 53), (7, 55), (8, 57), (10, 59),
          (12, 57), (16, 56), (19, 55), (21, 55), (24, 58), (26, 59),
          (30, 60), (28, 63), (24, 66), (21, 69), (18, 70), (14, 67),
          (12, 64), (8, 62), (5, 60), (5, 58), (1, 58), (-3, 57),
          (-5, 53), (-6, 50), (-9, 47), (-10, 42)]
UK = [(-5, 50), (-4, 53), (-5, 56), (-3, 58), (-1, 57), (0, 54),
      (1, 51), (-2, 50)]
ASIA = [(28, 62), (32, 66), (40, 68), (50, 69), (60, 69), (70, 72),
        (80, 73), (90, 75), (100, 76), (110, 74), (120, 73), (130, 72),
        (140, 72), (150, 70), (160, 69), (170, 66), (178, 65),
        (170, 62), (162, 60), (158, 55), (156, 51), (150, 59),
        (142, 54), (140, 48), (138, 44), (135, 43), (132, 40),
        (129, 37), (126, 35), (122, 32), (121, 28), (118, 25),
        (113, 22), (110, 20), (108, 16), (106, 11), (104, 9),
        (101, 8), (99, 10), (97, 14), (94, 17), (92, 21), (89, 22),
        (86, 20), (82, 17), (80, 14), (77, 8), (75, 12), (73, 19),
        (70, 22), (67, 25), (63, 25), (59, 26), (56, 27), (53, 27),
        (50, 29), (48, 30), (45, 29), (42, 29), (39, 31), (36, 36),
        (33, 36), (30, 36), (27, 37), (26, 39), (27, 41), (28, 45),
        (29, 48), (30, 52), (29, 56), (28, 59), (28, 62)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 36),
         (140, 38), (141, 40), (141, 43), (143, 44), (141, 45),
         (140, 41), (139, 38), (137, 36), (135, 35), (132, 34),
         (130, 33)]
SUMATRA = [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6),
           (103, -5), (100, -1), (97, 2)]
BORNEO = [(109, 1), (111, 3), (115, 5), (118, 6), (119, 2),
          (118, -1), (115, -3), (111, -3), (109, 0)]
NEW_GUINEA = [(131, -1), (135, -2), (138, -3), (141, -3), (144, -4),
              (147, -6), (150, -8), (147, -9), (143, -8), (139, -7),
              (135, -5), (132, -3)]
AUSTRALIA = [(113, -22), (114, -29), (115, -34), (118, -35), (122, -34),
             (126, -32), (130, -32), (134, -33), (137, -35), (140, -38),
             (144, -38), (148, -39), (150, -37), (153, -33), (153, -28),
             (152, -24), (150, -22), (147, -19), (144, -16), (142, -11),
             (140, -14), (137, -12), (134, -12), (131, -12), (128, -14),
             (125, -15), (122, -17), (119, -19), (116, -20)]
CONTINENTS = [N_AMERICA, GREENLAND, S_AMERICA, AFRICA, EUROPE, UK,
              ASIA, JAPAN, SUMATRA, BORNEO, NEW_GUINEA, AUSTRALIA]

# Map panel geometry (equirectangular lon -180..180, lat 78..-58).
MAP_X0, MAP_X1, MAP_Y0, MAP_Y1 = 14, 1010, 246, 600

def lon_x(lon):
    return int(MAP_X0 + (lon + 180.0) * (MAP_X1 - MAP_X0) / 360.0)

def lat_y(lat):
    return int(MAP_Y0 + (78.0 - lat) * (MAP_Y1 - MAP_Y0) / 136.0)

def map_pt(lon, lat):
    return (lon_x(lon), lat_y(lat))

# ---------------------------------------------------------------- drawing
def draw_spiral(cv, cx, cy, c):
    """Little cyclone swirl: three arms of dots curling inward."""
    for arm in range(3):
        a0 = arm * 2.094
        for i in range(26):
            t = i / 25.0
            a = a0 + t * 4.4
            r = 15 - t * 12
            x = int(cx + r * math.cos(a))
            y = int(cy + r * math.sin(a))
            cv.set(x, y, c)
            cv.set(x + 1, y, c)
    cv.circle(cx, cy, 2, c)

def draw_bars(cv, x, y, c):
    """Little rising bar chart with a trend line."""
    heights = [7, 12, 17, 23]
    for i, h in enumerate(heights):
        cv.fill_rect(x + i * 9, y + 24 - h, 6, h, c)
    cv.line(x - 2, y + 24 - 7, x + 34, y + 24 - 25, RED)

def draw_marker(cv, num, lon, lat, off):
    tx, ty = map_pt(lon, lat)
    dx, dy = off
    cx, cy = tx + dx, ty + dy
    if (dx, dy) != (0, 0):
        cv.line(tx, ty, cx, cy, WHITE)
        cv.circle(tx, ty, 2, WHITE)
    cv.circle(cx, cy, 8, RED)
    cv.circle(cx, cy, 8, WHITE, fill=False)
    s = str(num)
    cv.text(cx - text_w(s, 1) // 2, cy - 3, s, WHITE, 1)
    return cx, cy

def draw_masthead(cv):
    cv.text(24, 16, "MAKE.FUN NEWS ATLAS", INK_SOFT, 1)
    d = "FRIDAY 20 NOVEMBER 2026"
    cv.text(1024 - 24 - text_w(d, 1), 16, d, RED, 1)
    cv.text_c(512, 34, "THE WORLD IN ONE DAY", INK, 5)
    cv.text_c(512, 76, "36 STORIES FROM EVERY REGION - ONE MAP, ONE DAY",
              INK_SOFT, 2)
    cv.hline(24, 104, 976, RED, 3)
    cv.hline(24, 110, 976, INK, 1)

def draw_lead(cv, x, w, tag, headline, body, icon):
    y0, y1 = 120, 238
    cv.fill_rect(x, y0, w, y1 - y0, PANEL)
    cv.rect(x, y0, w, y1 - y0, INK, 1)
    cv.fill_rect(x, y0, w, 3, RED)
    cv.text(x + 14, y0 + 12, tag, RED, 1)
    if icon == "spiral":
        draw_spiral(cv, x + w - 26, y0 + 20, RED)
    else:
        draw_bars(cv, x + w - 52, y0 + 8, INK)
    yy = cv.wrap(x + 14, y0 + 30, headline, INK, 2, w - 28, 17)
    cv.wrap(x + 14, yy + 4, body, INK_SOFT, 1, w - 28, 10)

def draw_map(cv):
    cv.fill_rect(MAP_X0, MAP_Y0, MAP_X1 - MAP_X0, MAP_Y1 - MAP_Y0, TEAL)
    cv.rect(MAP_X0, MAP_Y0, MAP_X1 - MAP_X0, MAP_Y1 - MAP_Y0, INK, 2)
    # graticule
    for lon in range(-150, 181, 30):
        xx = lon_x(lon)
        cv.vline(xx, MAP_Y0, MAP_Y1 - MAP_Y0, TEAL_DK, 1)
    for lat in range(-30, 79, 30):
        yy = lat_y(lat)
        cv.hline(MAP_X0, yy, MAP_X1 - MAP_X0, TEAL_DK, 1)
    for poly in CONTINENTS:
        pts = [map_pt(lo, la) for lo, la in poly]
        cv.polyfill(pts, LAND)
        cv.polyline(pts, LAND_LN, close=True)
    # compass rose, lower-left ocean
    ccx, ccy = 76, 576
    cv.circle(ccx, ccy, 13, WHITE, fill=False)
    cv.line(ccx, ccy - 13, ccx, ccy + 13, WHITE)
    cv.line(ccx - 13, ccy, ccx + 13, ccy, WHITE)
    cv.text(ccx - 2, ccy - 24, "N", WHITE, 1)
    # Voyager marker note: it is in deep space, shown in the South Pacific
    cv.text(700, 576, "6 = VOYAGER 1, IN DEEP SPACE", (200, 220, 220), 1)
    for num, lon, lat, off, _grp, _lbl in STORIES:
        draw_marker(cv, num, lon, lat, off)

def draw_ledger(cv):
    y0 = 606
    cv.text(24, y0, "THE DAY IN BRIEF - 36 STORIES BY REGION", INK, 2)
    note = "MAP: EVERY NUMBER MATCHES A STORY BELOW"
    cv.text(1024 - 24 - text_w(note, 1), y0 + 4, note, INK_SOFT, 1)
    cv.hline(24, y0 + 18, 976, INK, 1)
    cols = [
        (24, ["ASIA", "EUROPE", "MIDDLE EAST"]),
        (516, ["AMERICAS", "AFRICA", "TECH & BUSINESS", "WORLD",
               "SPORT & CULTURE"]),
    ]
    for cx, groups in cols:
        yy = y0 + 26
        for grp in groups:
            cv.text(cx, yy, grp, GROUP_COLORS[grp], 1)
            cv.hline(cx, yy + 9, 452, GROUP_COLORS[grp], 1)
            yy += 13
            for num, _lo, _la, _off, g, lbl in STORIES:
                if g != grp:
                    continue
                s = str(num)
                cv.fill_rect(cx, yy - 1, 15, 11, GROUP_COLORS[grp])
                cv.text(cx + (15 - text_w(s, 1)) // 2, yy + 1, s, WHITE, 1)
                cv.text(cx + 20, yy, lbl, INK, 2)
                yy += 15
            yy += 2

def draw_footer(cv):
    cv.hline(24, 984, 976, INK, 1)
    cv.text_c(512, 994,
              "ALL 36 STORIES FIRST REPORTED ON FRIDAY 20 NOVEMBER 2026",
              INK_SOFT, 1)

def build():
    cv = Canvas(W, H, PAPER)
    cv.rect(4, 4, W - 8, H - 8, INK, 2)
    draw_masthead(cv)
    draw_lead(cv, 14, 489, "LEAD 1 - ASIA",
              "CYCLONE AKVAN BEARS DOWN ON ODISHA",
              "~300,000 evacuated and 423 rescue teams deployed as the "
              "storm nears India's east coast.", "spiral")
    draw_lead(cv, 521, 489, "LEAD 2 - TECH & BUSINESS",
              "ANTHROPIC'S BLOCKBUSTER MARKET DEBUT",
              "Shares surge on debut as the AI firm becomes one of the "
              "world's most valuable public companies, at a reported "
              "~$1.5T valuation.", "bars")
    draw_map(cv)
    draw_ledger(cv)
    draw_footer(cv)
    return cv

def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)

if __name__ == "__main__":
    main()

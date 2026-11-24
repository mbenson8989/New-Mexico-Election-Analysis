#!/usr/bin/env python3
"""New Mexico Guarantee Clause graphic (1080x1350 and 1600x900) + X post variants (post.txt).

All quoted text is verified (see post.txt):
  - U.S. Const. art. IV, sec. 4 (National Archives transcription).
  - EO 14399, "Ensuring Citizenship Verification and Integrity in Federal Elections",
    signed March 31, 2026, 91 FR 17125 (Apr. 3, 2026), FR Doc. 2026-06601, Sec. 1 text.
Rendered at 2x and downsampled for crisp type. Local only; posts nothing.
"""
import random, math, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'wiki' / 'resources' / 'guarantee-clause'; OUT.mkdir(parents=True, exist_ok=True)
G = '/usr/share/fonts/truetype/sand-box/google/'
CINZEL = G + 'Cinzel/Cinzel-VariableFont_wght.ttf'
EBG = G + 'EB Garamond/EBGaramond-VariableFont_wght.ttf'
EBGI = G + 'EB Garamond/EBGaramond-Italic-VariableFont_wght.ttf'

PARCH = (238, 226, 198); INK = (52, 34, 24); ADOBE = (178, 98, 62); ADOBE_D = (120, 60, 38)
TURQ = (24, 138, 138); TURQ_D = (14, 88, 94); TURQ_L = (120, 186, 180); SAND = (214, 184, 140)

OPEN = "Did you know? It's NOT your job to prove our elections are free and fair. The Guarantee Clause puts that on the government."
CLAUSE = ("The United States shall guarantee to every State in this Union a Republican Form of Government, "
          "and shall protect each of them against Invasion\u2026")
EOQ = ("The Federal Government has an unavoidable duty under Article II of the Constitution "
       "of the United States to enforce Federal law\u2026")
SRC = "Sources: U.S. Const. art. IV, \u00a7 4  \u00b7  Exec. Order 14399 (Mar. 31, 2026), 91 FR 17125, Sec. 1"
FR_URL = "https://www.federalregister.gov/documents/2026/04/03/2026-06601/ensuring-citizenship-verification-and-integrity-in-federal-elections"
WH_URL = "https://www.whitehouse.gov/presidential-actions/2026/03/ensuring-citizenship-verification-and-integrity-in-federal-elections/"

def font(path, size, wght=None):
    f = ImageFont.truetype(path, size)
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f

def parchment(w, h, seed=7):
    rnd = random.Random(seed)
    base = Image.new('RGB', (w, h), PARCH)
    noise = Image.effect_noise((w // 4, h // 4), 22).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3))
    tint = Image.merge('RGB', [noise.point(lambda v: v * 0.9), noise.point(lambda v: v * 0.8), noise.point(lambda v: v * 0.6)])
    base = Image.blend(base, tint, 0.10)
    d = ImageDraw.Draw(base, 'RGBA')
    for _ in range(int(w * h / 9000)):   # faint fibres
        x, y = rnd.uniform(0, w), rnd.uniform(0, h); a = rnd.uniform(0, math.pi); L = rnd.uniform(10, 60)
        d.line([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], fill=(140, 110, 70, 14), width=2)
    # vignette (burnt edges)
    vig = Image.new('L', (w, h), 0); vd = ImageDraw.Draw(vig)
    vd.rectangle([w * 0.04, h * 0.04, w * 0.96, h * 0.96], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(min(w, h) * 0.08))
    edge = Image.new('RGB', (w, h), (176, 140, 92))
    return Image.composite(base, edge, vig)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur); return lines

def block(d, xy, text, f, fill, maxw, lh, align='center', cx=None):
    x, y = xy
    for ln in wrap(d, text, f, maxw):
        if align == 'center': d.text((cx, y), ln, font=f, fill=fill, anchor='ma')
        else: d.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y

def mountains(d, w, base_y, s, seed=3, ground=None):
    """Layered Sangre de Cristo ridgelines: jagged peaks (midpoint displacement around a few summits),
    highest toward the left/north like the range above Santa Fe; filled down to the ground line."""
    rnd = random.Random(seed)
    ground = ground or base_y
    layers = [(TURQ_L, 1.0, 0.00), (TURQ, 0.78, 0.30), (TURQ_D, 0.52, 0.62)]
    top = base_y
    for li, (col, amp, ph) in enumerate(layers):
        n = 257
        peaks = [(rnd.uniform(0, 1), rnd.uniform(0.45, 1.0) * amp, rnd.uniform(0.10, 0.22)) for _ in range(6)]
        def hgt(t):
            v = max(max(0.0, pk * (1 - abs(t - px) / wd)) for px, pk, wd in peaks)
            return max(v, 0.18 * amp) * (1.12 - 0.35 * t)
        ys = [hgt(i / (n - 1)) for i in range(n)]
        step = 64; r = 0.10 * amp
        while step >= 1:      # midpoint jitter for rocky ridges
            for i in range(step, n - 1, step * 2):
                ys[i] = (ys[i - step] + ys[i + step]) / 2 * 0.5 + ys[i] * 0.5 + rnd.uniform(-r, r)
            step //= 2; r *= 0.55
        pts = [(0, ground)] + [(w * i / (n - 1), base_y - max(0.05, y) * s) for i, y in enumerate(ys)] + [(w, ground)]
        d.polygon(pts, fill=col); top = min([top] + [p_[1] for p_ in pts])
    d.rectangle([0, base_y, w, ground], fill=TURQ_D)
    return top

def roundhouse(d, cx, base_y, s):
    """New Mexico State Capitol (Roundhouse) silhouette: round two-tier drum, central entrance block
    with Territorial brick coping and square columns, flat roofline."""
    col = ADOBE_D
    W1, H1 = 620 * s, 120 * s      # lower drum (seen as wide band with rounded ends)
    d.rectangle([cx - W1 / 2 + 60 * s, base_y - H1, cx + W1 / 2 - 60 * s, base_y], fill=col)
    d.ellipse([cx - W1 / 2, base_y - H1, cx - W1 / 2 + 120 * s, base_y], fill=col); d.ellipse([cx + W1 / 2 - 120 * s, base_y - H1, cx + W1 / 2, base_y], fill=col)
    W2, H2 = 430 * s, 70 * s       # upper drum
    d.rounded_rectangle([cx - W2 / 2, base_y - H1 - H2 + 8 * s, cx + W2 / 2, base_y - H1 + 20 * s], radius=34 * s, fill=col)
    # brick coping dentils on both tiers
    for (wid, top) in ((W1, base_y - H1), (W2, base_y - H1 - H2 + 8 * s)):
        x = cx - wid / 2 + 60 * s
        while x < cx + wid / 2 - 60 * s:
            d.rectangle([x, top - 9 * s, x + 12 * s, top], fill=col); x += 22 * s
    # entrance portico
    PW, PH = 170 * s, 190 * s
    d.rectangle([cx - PW / 2, base_y - PH, cx + PW / 2, base_y], fill=col)
    d.rectangle([cx - PW / 2 - 14 * s, base_y - PH - 14 * s, cx + PW / 2 + 14 * s, base_y - PH + 4 * s], fill=col)
    # columns as parchment-coloured gaps
    gap = PARCH
    for i in range(4):
        x0 = cx - PW / 2 + 20 * s + i * 38 * s
        d.rectangle([x0 + 12 * s, base_y - PH + 34 * s, x0 + 26 * s, base_y], fill=(206, 178, 140))
    # window bands on lower drum
    for side in (-1, 1):
        for i in range(5):
            x = cx + side * (PW / 2 + 30 * s + i * 42 * s)
            d.rectangle([x - 8 * s, base_y - H1 + 34 * s, x + 8 * s, base_y - H1 + 66 * s], fill=(206, 178, 140))
            d.rectangle([x - 8 * s, base_y - H1 + 80 * s, x + 8 * s, base_y - H1 + 106 * s], fill=(206, 178, 140))
    

def rule(d, cx, y, half, col, s):
    d.line([(cx - half, y), (cx + half, y)], fill=col, width=max(2, int(3 * s)))
    d.polygon([(cx, y - 9 * s), (cx + 9 * s, y), (cx, y + 9 * s), (cx - 9 * s, y)], fill=col)

def portrait():
    S = 2; w, h = 1080 * S, 1350 * S
    im = parchment(w, h); d = ImageDraw.Draw(im)
    d.rectangle([28 * S, 28 * S, w - 28 * S, h - 28 * S], outline=ADOBE_D, width=3 * S)
    d.rectangle([40 * S, 40 * S, w - 40 * S, h - 40 * S], outline=TURQ_D, width=1 * S)
    cx = w // 2; M = 110 * S
    d.text((cx, 78 * S), 'NEW MEXICO  \u00b7  ARTICLE IV, SECTION 4', font=font(CINZEL, 30 * S, 600), fill=TURQ_D, anchor='ma')
    d.text((cx, 124 * S), 'The Guarantee Clause', font=font(CINZEL, 74 * S, 700), fill=INK, anchor='ma')
    rule(d, cx, 230 * S, 260 * S, ADOBE, S)
    y = block(d, (0, 270 * S), '\u201c' + CLAUSE + '\u201d', font(EBGI, 35 * S, 500), INK, w - 2 * M, 48 * S, cx=cx)
    y += 34 * S
    lines = ["Did you know? It\u2019s NOT your job", "to prove our elections are free and fair.", "The Guarantee Clause puts that", "on the government."]
    fb = font(EBG, 54 * S, 700)
    for i, ln in enumerate(lines):
        d.text((cx, y), ln, font=fb, fill=ADOBE_D if i < 2 else TURQ_D, anchor='ma'); y += 70 * S
    y += 30 * S
    # EO box
    bx0, bx1 = M - 20 * S, w - M + 20 * S; by0 = y
    eo_f = font(EBGI, 33 * S, 500); eo_lines = wrap(d, '\u201c' + EOQ + '\u201d', eo_f, bx1 - bx0 - 170 * S)
    by1 = by0 + 76 * S + len(eo_lines) * 44 * S + 22 * S
    d.rectangle([bx0, by0, bx1, by1], outline=TURQ, width=2 * S, fill=(232, 216, 184))
    d.text((cx, by0 + 18 * S), 'EXECUTIVE ORDER 14399  \u00b7  MARCH 31, 2026  \u00b7  91 FR 17125', font=font(CINZEL, 24 * S, 700), fill=TURQ_D, anchor='ma')
    yy = by0 + 70 * S
    for ln in eo_lines:
        d.text((cx, yy), ln, font=eo_f, fill=INK, anchor='ma'); yy += 44 * S
    # landscape
    base = h - 120 * S
    MTOP = mountains(d, w, base - 40 * S, 150 * S, ground=base)
    assert MTOP > by1 + 10 * S, f'mountains ({MTOP / S:.0f}) overlap EO box ({by1 / S:.0f})'
    d.rectangle([0, base - 40 * S, w, base], fill=SAND)
    roundhouse(d, cx, base - 6 * S, 0.66 * S)
    d.rectangle([0, base, w, h], fill=ADOBE)
    d.rectangle([28 * S, 28 * S, w - 28 * S, h - 28 * S], outline=ADOBE_D, width=3 * S)
    d.text((cx, base + 32 * S), SRC, font=font(EBG, 24 * S, 500), fill=PARCH, anchor='ma')
    return im.resize((1080, 1350), Image.LANCZOS), by1 / S, MTOP / S

def landscape():
    S = 2; w, h = 1600 * S, 900 * S
    im = parchment(w, h, seed=11); d = ImageDraw.Draw(im)
    d.rectangle([24 * S, 24 * S, w - 24 * S, h - 24 * S], outline=ADOBE_D, width=3 * S)
    d.rectangle([36 * S, 36 * S, w - 36 * S, h - 36 * S], outline=TURQ_D, width=1 * S)
    L = 90 * S; colw = 860 * S
    d.text((L, 70 * S), 'NEW MEXICO  \u00b7  ARTICLE IV, SECTION 4', font=font(CINZEL, 26 * S, 600), fill=TURQ_D)
    d.text((L, 108 * S), 'The Guarantee Clause', font=font(CINZEL, 64 * S, 700), fill=INK)
    d.line([(L, 202 * S), (L + 420 * S, 202 * S)], fill=ADOBE, width=3 * S)
    y = 226 * S
    fb = font(EBG, 46 * S, 700)
    for i, ln in enumerate(["Did you know? It\u2019s NOT your job to prove", "our elections are free and fair.", "The Guarantee Clause puts that", "on the government."]):
        d.text((L, y), ln, font=fb, fill=ADOBE_D if i < 2 else TURQ_D); y += 58 * S
    y += 14 * S
    y = block(d, (L, y), '\u201c' + CLAUSE + '\u201d', font(EBGI, 28 * S, 500), INK, colw, 37 * S, align='left') + 8 * S
    # right: EO panel
    px0, px1, py0 = 1010 * S, w - 80 * S, 90 * S
    eo_f = font(EBGI, 30 * S, 500); eo_lines = wrap(d, '\u201c' + EOQ + '\u201d', eo_f, px1 - px0 - 60 * S)
    py1 = py0 + 150 * S + len(eo_lines) * 40 * S + 20 * S
    d.rectangle([px0, py0, px1, py1], outline=TURQ, width=2 * S, fill=(232, 216, 184))
    pcx = (px0 + px1) // 2
    d.text((pcx, py0 + 22 * S), 'EXECUTIVE ORDER 14399', font=font(CINZEL, 30 * S, 700), fill=TURQ_D, anchor='ma')
    d.text((pcx, py0 + 66 * S), 'Signed March 31, 2026  \u00b7  91 FR 17125', font=font(EBG, 26 * S, 600), fill=INK, anchor='ma')
    rule(d, pcx, py0 + 118 * S, 150 * S, ADOBE, S)
    yy = py0 + 142 * S
    for ln in eo_lines:
        d.text((pcx, yy), ln, font=eo_f, fill=INK, anchor='ma'); yy += 40 * S
    base = h - 84 * S
    MT = mountains(d, w, base - 34 * S, 240 * S, seed=5, ground=base)
    assert MT > max(y, py1) + 10 * S, 'landscape mountains overlap text'
    d.rectangle([0, base - 34 * S, w, base], fill=SAND)
    roundhouse(d, 1270 * S, base - 4 * S, 0.56 * S)
    d.rectangle([0, base, w, h], fill=ADOBE)
    d.rectangle([24 * S, 24 * S, w - 24 * S, h - 24 * S], outline=ADOBE_D, width=3 * S)
    d.text((w // 2, base + 22 * S), SRC, font=font(EBG, 22 * S, 500), fill=PARCH, anchor='ma')
    return im.resize((1600, 900), Image.LANCZOS), y / S, py1 / S

# ---------------- X post variants (weighted length as X counts: URL = 23, CJK/emoji = 2)
URL = re.compile(r'https?://\S+')
def xlen(s):
    n = 0
    for ch in URL.sub('\x00', s):
        o = ord(ch)
        n += 23 if ch == '\x00' else (1 if (o <= 4351 or 8192 <= o <= 8205 or 8208 <= o <= 8223 or 8242 <= o <= 8247) else 2)
    return n

VARIANTS = [
    ('A (recommended: verified quote + source link)',
     OPEN + '\n\nEO 14399 (March 31, 2026) cites it and says Washington has an "unavoidable duty" to enforce federal law. Hold them to it.\n\n' + FR_URL),
    ('B (no link; full Federal Register citation)',
     OPEN + '\n\nEO 14399, signed March 31, 2026 (91 FR 17125), cites Art. IV, Sec. 4 and an "unavoidable duty" to enforce federal law. Their duty. Not yours.'),
    ('C (New Mexico framing + link)',
     OPEN + '\n\nNew Mexico: EO 14399 (3/31/26) cites the Clause and names an "unavoidable duty" to enforce federal law. Expect them to meet it.\n\n' + FR_URL),
]

def main():
    p, eo_bottom, mtn_top = portrait(); p.save(OUT / 'nm-guarantee-clause.png')
    l, ly, lpy = landscape(); l.save(OUT / 'nm-guarantee-clause-landscape.png')
    print(f'portrait: EO box bottom y={eo_bottom:.0f}, mountain top approx y={mtn_top:.0f}; landscape: left text bottom {ly:.0f}, EO panel bottom {lpy:.0f}')
    out = ["NEW MEXICO GUARANTEE CLAUSE X POST (draft, NOT posted; local only)",
           "Built by scripts/build_guarantee_clause.py. Character counts use X's weighting (every URL = 23).", ""]
    for name, txt in VARIANTS:
        n = xlen(txt); assert n <= 280, (name, n); assert txt.startswith(OPEN)
        out += [f"=== Variant {name}: {n}/280 characters ===", txt, ""]
    out += ["=== Verification notes (checked Nov 23, 2026) ===",
        "CONFIRMED on federalregister.gov (API + full text):",
        "  - Executive Order 14399, \"Ensuring Citizenship Verification and Integrity in Federal Elections\".",
        "  - Signed March 31, 2026 (API signing_date 2026-03-31; text: \"Executive Order 14399 of March 31, 2026\"; \"THE WHITE HOUSE, March 31, 2026.\").",
        "  - Citation 91 FR 17125 (pages 17125-17128), published Friday April 3, 2026 (Vol. 91, No. 64), FR Doc. 2026-06601. President: Donald Trump.",
        "  - Exact quote, Sec. 1: \"The Federal Government has an unavoidable duty under Article II of the Constitution of the United States to enforce Federal law, which includes preventing violations of Federal criminal law and maintaining public confidence in election outcomes.\"",
        "  - Guarantee Clause tie-in, preamble: the order is issued under, among other authorities, \"the Federal Government's constitutional obligation to guarantee a republican form of Government to every State in the Union, U.S. Const. Art. IV, Sec. 4\".",
        "CONFIRMED on whitehouse.gov (presidential-actions page, same date, same Sec. 1 sentence).",
        "CONFIRMED on archives.gov: Art. IV, Sec. 4 text \"The United States shall guarantee to every State in this Union a Republican Form of Government, and shall protect each of them against Invasion; ...\"",
        "CAUTION / NOT CONFIRMED - do not claim:",
        "  - The EO ties the words \"unavoidable duty\" to ARTICLE II (enforcing federal law), not to the Guarantee Clause itself. The Guarantee Clause appears in the order's authority preamble as a \"constitutional obligation\". The variants keep these separate (\"cites it\" + \"unavoidable duty to enforce federal law\"); do not write \"the Guarantee Clause is an unavoidable duty\" as a quote.",
        "  - /workspace/AG_Hilgers_EO14399_Letter_Prompt.txt says EO 14399 was signed March 31, 2025. That year is wrong; the Federal Register and White House both say March 31, 2026.",
        "  - Parts of the EO's implementation (USPS ballot-mail rule) have been in litigation; not mentioned in the post.",
        "Sources:",
        "  " + FR_URL,
        "  https://www.federalregister.gov/documents/full_text/text/2026/04/03/2026-06601.txt",
        "  https://www.federalregister.gov/api/v1/documents/2026-06601.json",
        "  https://www.govinfo.gov/content/pkg/FR-2026-04-03/pdf/2026-06601.pdf",
        "  " + WH_URL,
        "  https://www.whitehouse.gov/wp-content/uploads/2026/03/eo-14399.pdf",
        "  https://www.archives.gov/founding-docs/constitution-transcript",
        "Graphics: nm-guarantee-clause.png (1080x1350), nm-guarantee-clause-landscape.png (1600x900)."]
    (OUT / 'post.txt').write_text('\n'.join(out) + '\n')
    for name, txt in VARIANTS: print(f'{name}: {xlen(txt)}')

if __name__ == '__main__':
    main()

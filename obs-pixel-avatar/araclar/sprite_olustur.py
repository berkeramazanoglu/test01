"""Yüksek çözünürlüklü portreden animasyonlu pixel sprite üretir → sprite.js

Kullanım:  python3 -I araclar/sprite_olustur.py PORTRE.webp [çıktı/sprite.js]

Bütün düzenlemeler (göz kırpma, ağız açılması, çatık kaş) önce büyük
görselde yapılır, sonra hepsi aynı paletle 128 piksele küçültülür. Böylece
kareler birbirine piksel piksel uyar. Koordinatlar bu projedeki portreye göre
ölçülmüştür; farklı bir görsel kullanılırsa LANDMARK değerleri güncellenmeli.
"""
import json
import math
import sys

from PIL import Image, ImageDraw

SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else 'sprite.js'
W = 128            # sprite genişliği (piksel)
NCOL = 40          # palet büyüklüğü

im = Image.open(SRC).convert('RGBA')
F = W / im.width
H = round(im.height * F)

# ---------------------------------------------------------------- ölçülen noktalar (orijinal görsel)
LIP_L, LIP_R = (555, 699), (725, 720)          # dudak çizgisi köşeleri
EYES = [((577, 472), 50, 19, 0), ((789, 511), 46, 16, 499)]  # merkez, yarıçaplar, üst sınır
BROWS = [  # x aralığı, segment üst/alt, kaş merkez çizgisi (dış, iç), kayma (dış, iç)
    dict(x0=500, x1=692, top=372, bot=446, c0=(515, 400), c1=(680, 428), s0=-7, s1=26),
    dict(x0=733, x1=878, top=404, bot=482, c0=(745, 437), c1=(860, 432), s0=26, s1=-7),
]


def lip_y(x):
    return LIP_L[1] + (x - LIP_L[0]) * (LIP_R[1] - LIP_L[1]) / (LIP_R[0] - LIP_L[0])


def mouth(img, amp):
    """Alt dudak + çeneyi sütun sütun aşağı kaydırarak ağzı açar."""
    src = img.copy(); px = img.load(); sp = src.load()
    cx = (LIP_L[0] + LIP_R[0]) / 2; hw = (LIP_R[0] - LIP_L[0]) / 2
    for x in range(LIP_L[0], LIP_R[0] + 1):
        t = (x - cx) / hw
        o = round(amp * max(0.0, 1 - t * t) ** 0.7)
        if o <= 0:
            continue
        y0 = round(lip_y(x)) + 2
        for y in range(y0 + 95 + o, y0 - 1, -1):          # aşağı kaydır
            if y - o >= y0:
                px[x, y] = sp[x, y - o]
        teeth = max(0, min(9, round(o * 0.33))) if amp >= 25 else 0
        for k in range(o):                                   # boşluğu doldur
            y = y0 + k
            depth = k / max(1, o - 1)
            if k < teeth:
                col = (238, 230, 222, 255)
            elif amp >= 25 and depth > 0.6 and abs(t) < 0.45:
                col = (196, 92, 104, 255)                     # dil
            else:
                col = (74, 24, 34, 255) if 0.15 < abs(t) or depth > 0.2 else (92, 30, 42, 255)
            px[x, y] = col
    return img


def blink(img):
    px = img.load()
    for (cx, cy), rx, ry, ymin in EYES:
        # gözün hemen altındaki tenin ortalama rengi
        samp = [px[x, cy + ry + 6] for x in range(cx - rx // 2, cx + rx // 2)]
        skin = tuple(sum(c[i] for c in samp) // len(samp) for i in range(3)) + (255,)
        for y in range(cy - ry - 2, cy + ry + 3):
            for x in range(cx - rx - 2, cx + rx + 3):
                if y < ymin:
                    continue
                if ((x - cx) / (rx + 2)) ** 2 + ((y - cy) / (ry + 2)) ** 2 <= 1:
                    px[x, y] = skin
        d = ImageDraw.Draw(img)
        pts = [(cx + rx * math.cos(a), cy + ry * 0.35 + ry * 0.45 * math.sin(a)) for a in [i * math.pi / 20 for i in range(21)]]
        d.line(pts, fill=(38, 26, 24, 255), width=7)
    return img


def angry(img):
    src = img.copy(); px = img.load(); sp = src.load()
    for b in BROWS:
        for x in range(b['x0'], b['x1'] + 1):
            t = (x - b['c0'][0]) / (b['c1'][0] - b['c0'][0]); t = min(1, max(0, t))
            c = b['c0'][1] + t * (b['c1'][1] - b['c0'][1])
            s = b['s0'] + t * (b['s1'] - b['s0'])
            fade = min(1, (x - b['x0']) / 12, (b['x1'] - x) / 12)  # kenarlarda yumuşat
            s *= fade
            top, bot = b['top'], b['bot']
            for y in range(top, bot + 1):
                if y <= c + s:
                    sy = top + (y - top) * (c - top) / max(1, c + s - top)
                else:
                    sy = c + (y - c - s) * (bot - c) / max(1, bot - c - s)
                px[x, y] = sp[x, min(bot, max(top, round(sy)))]
    return img


variants = {
    'base': im.copy(),
    'blink': blink(im.copy()),
    'half': mouth(im.copy(), 16),
    'open': mouth(im.copy(), 32),
    'shout': mouth(im.copy(), 50),
    'angry': angry(im.copy()),
}

small = {k: v.resize((W, H), Image.BOX) for k, v in variants.items()}
alpha = small['base'].getchannel('A').point(lambda v: 255 if v > 128 else 0)

# ortak palet: bütün karelerden
mosaic = Image.new('RGB', (W * len(small), H))
for i, v in enumerate(small.values()):
    mosaic.paste(v.convert('RGB'), (i * W, 0))
palimg = mosaic.quantize(colors=NCOL, method=Image.MEDIANCUT, dither=Image.NONE)
pal = palimg.getpalette()[:NCOL * 3]
hexpal = ['#%02x%02x%02x' % tuple(pal[i * 3:i * 3 + 3]) for i in range(NCOL)]
ALPH = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

idx = {k: list(v.convert('RGB').quantize(palette=palimg, dither=Image.NONE).get_flattened_data()) for k, v in small.items()}
A = list(alpha.get_flattened_data())
base = ''.join(ALPH[i] if A[j] else '.' for j, i in enumerate(idx['base']))
patches = {}
for k in variants:
    if k == 'base':
        continue
    patches[k] = ''.join(ALPH[i] if (A[j] and i != idx['base'][j]) else '.' for j, i in enumerate(idx[k]))

# saç tepesi (her sütundaki ilk opak satır) → boynuz/hale yerleşimi
top = [next((y for y in range(H) if A[y * W + x]), H) for x in range(W)]

# gözlük camı maskesi (parlama efekti için): ölçülen cam köşeleri içindeki açık renkli pikseller
LENSES = [[(50, 49), (66, 50), (66, 57), (52, 58)], [(76, 53), (90, 56), (89, 62), (78, 61)]]  # sprite koordinatı


def inside(poly, x, y):
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


rgb = small['base'].convert('RGB').load()
lens = [y * W + x for poly in LENSES for y in range(H) for x in range(W)
        if inside(poly, x + 0.5, y + 0.5) and 0.3 * rgb[x, y][0] + 0.59 * rgb[x, y][1] + 0.11 * rgb[x, y][2] > 140]

data = dict(w=W, h=H, pal=hexpal, base=base, patches=patches, top=top, lens=sorted(lens),
            cheeks=[[round(470 * F), round(640 * F), round(58 * F), round(30 * F)], [round(832 * F), round(668 * F), round(40 * F), round(24 * F)]],
            ears=[[round(370 * F), round(530 * F)], [round(925 * F), round(560 * F)]],
            split=round(800 * F))
with open(OUT, 'w') as f:
    f.write('// Otomatik üretildi: araclar/sprite_olustur.py — elle düzenlemeyin\n')
    f.write('window.SPRITE = ' + json.dumps(data, separators=(',', ':')) + ';\n')
print('sprite', W, H, 'renk', NCOL, 'cam pikseli', len(lens), {k: sum(c != '.' for c in p) for k, p in patches.items()})

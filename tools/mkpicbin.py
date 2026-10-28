"""Encodeur d'atlas `pic.bin` pour le moteur MCU des montres OnePlus/OPPO (monaco).

Inverse de `picbin.py`. Prend des images PNG (8 bits, RGB ou RGBA, non entrelacées) et
produit un atlas `pic.bin` au format observé par rétro-ingénierie :

  en-tête : u32 taille_totale, u32 N
  table   : N × (u32 offset, u16 w, u16 h, u16 format, u16 flag, u32 size)
  données : pixels non compressés + 4 octets de pied par image

Formats pixel :
  - argb4444 (format=4, 2 o/px, défaut)   : v = (a4<<12)|(r4<<8)|(g4<<4)|b4, little-endian
  - bgra8888 (format=1, 4 o/px)           : octets B,G,R,A

RÉSERVE IMPORTANTE : le rôle des 4 octets de pied de chaque image n'est pas identifié
(ni CRC32 standard ni longueur — testé). On écrit 0x00000000 par défaut. Si le MCU rejette
l'atlas, c'est le premier suspect : voir --tail pour essayer d'autres valeurs. À valider
seulement après root, sur la vraie montre. Usage personnel / interopérabilité.

Usage :
  python -I mkpicbin.py --out pic.bin img0.png img1.png ...            # argb4444
  python -I mkpicbin.py --fmt bgra8888 --out pic.bin fond.png
  # relire/vérifier avec picbin.py :
  python -I picbin.py pic.bin /tmp/verif
"""
import struct, sys, zlib, argparse

# ------- lecteur PNG minimal (8 bits, colortype 2=RGB / 6=RGBA, non entrelacé) -------
def read_png_rgba(path):
    d = open(path, 'rb').read()
    if d[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'{path}: pas un PNG')
    pos, w, h, ct, idat = 8, 0, 0, 0, b''
    while pos < len(d):
        ln = struct.unpack_from('>I', d, pos)[0]; typ = d[pos+4:pos+8]
        body = d[pos+8:pos+8+ln]
        if typ == b'IHDR':
            w, h, bd, ct = struct.unpack_from('>IIBB', body, 0)
            if bd != 8 or ct not in (2, 6):
                raise ValueError(f'{path}: seul PNG 8 bits RGB/RGBA non entrelacé est géré (bd={bd}, ct={ct})')
        elif typ == b'IDAT':
            idat += body
        elif typ == b'IEND':
            break
        pos += 12 + ln
    raw = zlib.decompress(idat)
    ch = 4 if ct == 6 else 3
    stride = w * ch
    out = bytearray(w * h * 4)
    prev = bytearray(stride)
    p = 0
    def paeth(a, b, c):
        pp = a + b - c; pa, pb, pc = abs(pp-a), abs(pp-b), abs(pp-c)
        return a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
    for y in range(h):
        f = raw[p]; line = bytearray(raw[p+1:p+1+stride]); p += 1 + stride
        for i in range(stride):
            a = line[i-ch] if i >= ch else 0
            b = prev[i]
            c = prev[i-ch] if i >= ch else 0
            if f == 1: line[i] = (line[i] + a) & 255
            elif f == 2: line[i] = (line[i] + b) & 255
            elif f == 3: line[i] = (line[i] + ((a + b) >> 1)) & 255
            elif f == 4: line[i] = (line[i] + paeth(a, b, c)) & 255
        for x in range(w):
            r, g, b_ = line[x*ch], line[x*ch+1], line[x*ch+2]
            al = line[x*ch+3] if ch == 4 else 255
            o = (y*w + x) * 4
            out[o:o+4] = bytes((r, g, b_, al))
        prev = line
    return w, h, bytes(out)

# ------------------------------- encodage -------------------------------
def enc_argb4444(rgba, n):
    out = bytearray(n * 2)
    for k in range(n):
        r, g, b, a = rgba[4*k:4*k+4]
        v = ((a >> 4) << 12) | ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4)
        out[2*k] = v & 0xFF; out[2*k+1] = (v >> 8) & 0xFF
    return bytes(out)

def enc_bgra8888(rgba, n):
    out = bytearray(n * 4)
    for k in range(n):
        r, g, b, a = rgba[4*k:4*k+4]
        out[4*k:4*k+4] = bytes((b, g, r, a))
    return bytes(out)

def build(images, fmt, tail):
    code = 4 if fmt == 'argb4444' else 1
    enc = enc_argb4444 if fmt == 'argb4444' else enc_bgra8888
    header = 8
    table = 16 * len(images)
    off = header + table
    index, blob = [], bytearray()
    for (w, h, rgba) in images:
        px = enc(rgba, w * h) + tail
        index.append((off, w, h, code, 1, len(px)))
        blob += px
        off += len(px)
    total = header + table + len(blob)
    out = bytearray()
    out += struct.pack('<II', total, len(images))
    for (o, w, h, c, fl, sz) in index:
        out += struct.pack('<IHHHHI', o, w, h, c, fl, sz)
    out += blob
    return bytes(out)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('pngs', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--fmt', choices=['argb4444', 'bgra8888'], default='argb4444')
    ap.add_argument('--tail', default='00000000', help='4 octets de pied en hex (rôle inconnu)')
    a = ap.parse_args()
    tail = bytes.fromhex(a.tail)
    if len(tail) != 4:
        sys.exit('--tail doit faire 4 octets (8 hex)')
    imgs = [read_png_rgba(p) for p in a.pngs]
    data = build(imgs, a.fmt, tail)
    open(a.out, 'wb').write(data)
    print(f'{a.out}: {len(imgs)} images, {len(data)} octets, fmt={a.fmt}')
    for i, (w, h, _) in enumerate(imgs):
        print(f'  #{i} {w}x{h}')

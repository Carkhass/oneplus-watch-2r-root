"""Lecteur de pic.bin (atlas d'images MCU des cadrans OnePlus/OPPO).

Usage : python -I picbin.py <pic.bin> [dossier_png]
Sans dossier : liste la table d'index. Avec : exporte chaque image en PNG
(selon le format déduit) pour vérification visuelle. Usage personnel.
"""
import struct, sys, zlib, os

def entries(buf):
    total, count = struct.unpack_from('<II', buf, 0)
    out = []
    for i in range(count):
        off, w, h, fmt, flag, size = struct.unpack_from('<IHHHHI', buf, 8 + 16 * i)
        out.append(dict(i=i, off=off, w=w, h=h, fmt=fmt, flag=flag, size=size))
    return total, out

def write_png(path, w, h, rgba):
    raw = b''.join(b'\x00' + rgba[y * w * 4:(y + 1) * w * 4] for y in range(h))
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b'')
    open(path, 'wb').write(png)

def decode(buf, e, mode):
    n = e['w'] * e['h']
    d = buf[e['off']:e['off'] + e['size']]
    px = bytearray()
    if e['fmt'] == 1:                       # 4 octets/px
        for k in range(n):
            b, g, r, a = d[4 * k:4 * k + 4]
            px += bytes((r, g, b, a))
    else:                                   # 2 octets/px
        for k in range(n):
            v = d[2 * k] | d[2 * k + 1] << 8
            if mode == 'rgb565':
                r, g, b = (v >> 11) << 3, ((v >> 5) & 63) << 2, (v & 31) << 3
                a = 255
            elif mode == 'rgb565be':
                v = d[2 * k] << 8 | d[2 * k + 1]
                r, g, b = (v >> 11) << 3, ((v >> 5) & 63) << 2, (v & 31) << 3
                a = 255
            else:                           # argb4444
                a, r, g, b = (v >> 12) * 17, ((v >> 8) & 15) * 17, ((v >> 4) & 15) * 17, (v & 15) * 17
            px += bytes((r, g, b, a))
    return px

if __name__ == '__main__':
    buf = open(sys.argv[1], 'rb').read()
    total, es = entries(buf)
    print(f'taille déclarée={total} réelle={len(buf)} images={len(es)}')
    for e in es:
        bpp = (e['size'] - 4) / (e['w'] * e['h'])
        print(f"#{e['i']:2} off=0x{e['off']:06x} {e['w']}x{e['h']} fmt={e['fmt']} flag={e['flag']} size={e['size']} -> {bpp:.3f} o/px, 4 derniers octets={buf[e['off']+e['size']-4:e['off']+e['size']].hex()}")
    if len(sys.argv) > 2:
        os.makedirs(sys.argv[2], exist_ok=True)
        for e in es:
            if e['off'] + e['size'] > len(buf) or (e['i'] + 1 < len(es) and es[e['i'] + 1]['off'] == e['off']):
                continue                    # image sans données propres (aperçu stocké dans preview.bin)
            modes = ['argb'] if e['fmt'] == 1 else ['rgb565', 'rgb565be', 'argb4444']
            for m in modes:
                write_png(os.path.join(sys.argv[2], f"{e['i']:02}_{m}.png"), e['w'], e['h'], decode(buf, e, m))

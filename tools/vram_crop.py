"""Recorta e amplia uma região de um dump de VRAM (tools/vram_dump.py).

Uso:
    python tools/vram_crop.py DUMP.bin X Y W H MODO SAIDA.png [ESCALA] [CLUT_X CLUT_Y]

    X, Y, W, H em unidades de VRAM (halfwords); MODO = 4, 8 ou 15.
    Em 4/8 bits, sem CLUT a imagem sai em tons de cinza; com CLUT_X/CLUT_Y
    usa a paleta real que fica naquele ponto da VRAM.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vram_dump import W, write_png  # noqa: E402


def c15(c):
    return bytes(((c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31))


def main():
    a = sys.argv[1:]
    if len(a) < 7:
        raise SystemExit(__doc__)
    path, x, y, w, h, mode, out = a[0], *map(int, a[1:6]), a[6]
    scale = int(a[7]) if len(a) > 7 else 3
    clut = (int(a[8]), int(a[9])) if len(a) > 9 else None
    data = open(path, "rb").read()
    hw = struct.unpack("<%dH" % (len(data) // 2), data)
    pal = None
    if clut:
        n = 16 if mode == 4 else 256
        pal = [hw[clut[1] * W + clut[0] + i] for i in range(n)]
    rows = []
    for yy in range(y, y + h):
        row = bytearray()
        for xx in range(x, x + w):
            c = hw[yy * W + xx]
            if mode == 15:
                px = [c15(c)]
            else:
                bits = 4 if mode == 4 else 8
                idx = [(c >> (bits * i)) & ((1 << bits) - 1) for i in range(16 // bits)]
                if pal:
                    px = [c15(pal[i]) for i in idx]
                else:
                    k = 255 // ((1 << bits) - 1)
                    px = [bytes((i * k,) * 3) for i in idx]
            for p in px:
                row += p * scale
        for _ in range(scale):
            rows.append(bytes(row))
    pw = w * (4 if mode == 4 else 2 if mode == 8 else 1) * scale
    write_png(out, pw, h * scale, rows)
    print("ok", out, pw, h * scale)


if __name__ == "__main__":
    main()

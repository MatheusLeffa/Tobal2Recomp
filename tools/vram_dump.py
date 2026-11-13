"""Despeja a VRAM do PS1 (1024x512, 16 bits) do jogo rodando e gera imagens.

Uso:
    python tools/vram_dump.py analysis/vram/titulo

Gera:
    <prefixo>.bin       VRAM crua (1024*512 halfwords little-endian)
    <prefixo>_15bpp.png  leitura como cor direta 15 bits
    <prefixo>_4bpp.png   cada halfword vira 4 pixels (nibbles) em tons de cinza;
                         textos/fontes de 4 bits ficam legíveis aqui
    <prefixo>_8bpp.png   cada halfword vira 2 pixels (bytes) em tons de cinza

Precisa do jogo aberto com PSX_DEBUG_SERVER=1. Os arquivos ficam em analysis/
(ignorada pelo Git: é conteúdo do disco).
"""
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nav  # noqa: E402

W, H, TILE = 1024, 512, 128


def read_vram():
    out = bytearray(W * H * 2)
    for ty in range(0, H, TILE):
        for tx in range(0, W, TILE):
            r = nav.cmd({"cmd": "vram_peek", "x": tx, "y": ty, "w": TILE, "h": TILE}, timeout=30)
            if not r.get("ok"):
                raise SystemExit(f"vram_peek falhou em {tx},{ty}: {r}")
            data = bytes.fromhex(r["hex"])
            for row in range(TILE):
                src = data[row * TILE * 2:(row + 1) * TILE * 2]
                dst = ((ty + row) * W + tx) * 2
                out[dst:dst + TILE * 2] = src
    return bytes(out)


def write_png(path, width, height, rows_rgb):
    raw = b"".join(b"\x00" + row for row in rows_rgb)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    prefix = sys.argv[1]
    os.makedirs(os.path.dirname(prefix) or ".", exist_ok=True)
    vram = read_vram()
    with open(prefix + ".bin", "wb") as f:
        f.write(vram)
    hw = struct.unpack("<%dH" % (W * H), vram)

    rows15 = []
    for y in range(H):
        row = bytearray()
        for x in range(W):
            c = hw[y * W + x]
            r, g, b = c & 31, (c >> 5) & 31, (c >> 10) & 31
            row += bytes((r * 255 // 31, g * 255 // 31, b * 255 // 31))
        rows15.append(bytes(row))
    write_png(prefix + "_15bpp.png", W, H, rows15)

    rows4 = []
    for y in range(H):
        row = bytearray()
        for x in range(W):
            c = hw[y * W + x]
            for i in range(4):
                v = ((c >> (4 * i)) & 15) * 17
                row += bytes((v, v, v))
        rows4.append(bytes(row))
    write_png(prefix + "_4bpp.png", W * 4, H, rows4)

    rows8 = []
    for y in range(H):
        row = bytearray()
        for x in range(W):
            c = hw[y * W + x]
            for i in range(2):
                v = (c >> (8 * i)) & 255
                row += bytes((v, v, v))
        rows8.append(bytes(row))
    write_png(prefix + "_8bpp.png", W * 2, H, rows8)
    print("ok", prefix)


if __name__ == "__main__":
    main()

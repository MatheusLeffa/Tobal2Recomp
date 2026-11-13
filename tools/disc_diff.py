"""Compara duas imagens BIN (MODE2/2352, uma trilha) arquivo por arquivo.

Uso:
    python tools/disc_diff.py ORIGINAL.bin MODIFICADO.bin [--out analysis/disc_diff.json]

Lê o sistema de arquivos ISO9660 do disco original, compara setor a setor e
mostra, para cada arquivo, quantos setores e bytes mudaram. Setores alterados
fora de qualquer arquivo também são listados. Não grava nada do disco, só
estatísticas (o JSON opcional tem offsets, não conteúdo).
"""
import json
import struct
import sys

SECTOR = 2352
USER = 2048


def read_sector(f, lba):
    f.seek(lba * SECTOR)
    return f.read(SECTOR)


def user_data(raw):
    """Form 1 (2048 bytes em +24) ou Form 2 (2324 bytes em +24)."""
    mode = raw[15]
    if mode == 2:
        form2 = raw[18] & 0x20
        return raw[24:24 + (2324 if form2 else USER)], bool(form2)
    return raw[16:16 + USER], False


def parse_dir(f, lba, size, path, out):
    data = b""
    for i in range((size + USER - 1) // USER):
        data += user_data(read_sector(f, lba + i))[0][:USER]
    pos = 0
    while pos < len(data):
        rec_len = data[pos]
        if rec_len == 0:
            pos = (pos // USER + 1) * USER
            continue
        ext = struct.unpack_from("<I", data, pos + 2)[0]
        length = struct.unpack_from("<I", data, pos + 10)[0]
        flags = data[pos + 25]
        nlen = data[pos + 32]
        name = data[pos + 33:pos + 33 + nlen]
        pos += rec_len
        if name in (b"\x00", b"\x01"):
            continue
        name = name.decode("ascii", "replace").split(";")[0]
        full = f"{path}/{name}"
        if flags & 2:
            parse_dir(f, ext, length, full, out)
        else:
            out.append({"path": full, "lba": ext, "size": length})


def list_files(f):
    pvd = user_data(read_sector(f, 16))[0]
    assert pvd[1:6] == b"CD001", "não é ISO9660"
    root = pvd[156:156 + 34]
    lba = struct.unpack_from("<I", root, 2)[0]
    size = struct.unpack_from("<I", root, 10)[0]
    files = []
    parse_dir(f, lba, size, "", files)
    return files


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    a_path, b_path = sys.argv[1], sys.argv[2]
    out_json = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    with open(a_path, "rb") as fa, open(b_path, "rb") as fb:
        files = list_files(fa)
        files_b = {x["path"]: x for x in list_files(fb)}
        fa.seek(0, 2)
        total = fa.tell() // SECTOR
        owner = {}
        for i, fi in enumerate(files):
            n = (fi["size"] + USER - 1) // USER
            # arquivos XA (Form 2) ocupam size/2048 setores de qualquer forma
            for s in range(fi["lba"], fi["lba"] + max(n, 1)):
                owner[s] = i
        per_file = {}
        orphan = []
        for lba in range(total):
            ra, rb = read_sector(fa, lba), read_sector(fb, lba)
            if ra == rb:
                continue
            ua, form2 = user_data(ra)
            ub, _ = user_data(rb)
            nbytes = sum(1 for x, y in zip(ua, ub) if x != y)
            i = owner.get(lba)
            if i is None:
                orphan.append(lba)
                continue
            st = per_file.setdefault(i, {"sectors": 0, "bytes": 0, "first": lba, "last": lba})
            st["sectors"] += 1
            st["bytes"] += nbytes
            st["last"] = lba
    rows = []
    for i, st in sorted(per_file.items(), key=lambda kv: -kv[1]["bytes"]):
        fi = files[i]
        fb_ = files_b.get(fi["path"])
        rows.append({**fi, **st, "size_b": fb_["size"] if fb_ else None})
    print(f"{len(files)} arquivos no disco original; {len(rows)} mudaram; "
          f"{len(orphan)} setores alterados fora de arquivos")
    print(f"{'arquivo':40} {'tamanho':>10} {'setores':>8} {'bytes':>9}  tamanho no modificado")
    for r in rows:
        print(f"{r['path']:40} {r['size']:>10} {r['sectors']:>8} {r['bytes']:>9}  {r['size_b']}")
    new = sorted(set(files_b) - {x["path"] for x in files})
    if new:
        print("arquivos só no modificado:", new)
    if out_json:
        with open(out_json, "w") as f:
            json.dump({"files": rows, "orphan_sectors": orphan, "new_files": new}, f, indent=1)


if __name__ == "__main__":
    main()

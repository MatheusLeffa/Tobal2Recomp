"""Gera o mod de idioma do Tobal 2 (tobal2.language) a partir de discos traduzidos.

Uso:
    python tools/make_lang_mod.py ORIGINAL.bin SAIDA_DIR \
        --variant en English "caminho/disco_em_ingles.bin" \
        [--variant pt Português "caminho/disco_em_portugues.bin"] \
        [--version 0.1.0]

Compara cada disco traduzido com o original (MODE2/2352, uma trilha) e grava
SAIDA_DIR/tobal2.language/<versão>/:
    manifest.toml   um [[overlay]] disc_user por trecho alterado, ativo só
                    quando a opção "lang" do mod é aquela variante
    <lang>/*.dat    SOMENTE os bytes que a tradução mudou (texto e letras da
                    fonte); nada do conteúdo original do jogo vai junto. Cada
                    trecho é guardado pelo SHA-256 do trecho original.

Mod desligado = jogo em japonês, idêntico ao disco original.
Para publicar, use SAIDA_DIR = mods/preloaded/packages.
"""
import argparse
import hashlib
import os
import shutil

SECTOR = 2352
USER = 2048
MAX_GAP = 4  # bytes iguais tolerados dentro de um trecho alterado


def user_data(raw):
    if raw[15] == 2:  # MODE2
        if raw[18] & 0x20:  # Form 2 (XA): não suportado por disc_user
            return None
        return raw[24:24 + USER]
    return raw[16:16 + USER]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def changed_runs(orig_path, mod_path):
    """Lista de (offset_disc_user, bytes_originais, bytes_novos)."""
    if os.path.getsize(orig_path) != os.path.getsize(mod_path):
        raise SystemExit(f"{mod_path}: tamanho diferente do original; o gerador "
                         "só faz trocas do mesmo tamanho")
    runs = []
    with open(orig_path, "rb") as fo, open(mod_path, "rb") as fm:
        lba = 0
        while True:
            so, sm = fo.read(SECTOR), fm.read(SECTOR)
            if not so:
                break
            if so != sm:
                uo, um = user_data(so), user_data(sm)
                if uo is None or um is None:
                    raise SystemExit(f"setor {lba} alterado é XA (Form 2); não suportado")
                base = lba * USER
                i = 0
                while i < USER:
                    if uo[i] == um[i]:
                        i += 1
                        continue
                    j = i
                    last = i
                    while j < USER and j - last <= MAX_GAP:
                        if uo[j] != um[j]:
                            last = j
                        j += 1
                    end = last + 1
                    runs.append([base + i, bytes(uo[i:end]), bytes(um[i:end])])
                    i = end
            lba += 1
    # junta trechos vizinhos (inclusive atravessando a fronteira de setor)
    merged = []
    for off, o, m in runs:
        if merged:
            p = merged[-1]
            gap = off - (p[0] + len(p[1]))
            if 0 <= gap <= MAX_GAP:
                # bytes do vão são iguais nos dois discos; recupera do original
                filler = b""
                if gap:
                    with open(orig_path, "rb") as fo:
                        for k in range(gap):
                            pos = p[0] + len(p[1]) + k
                            fo.seek((pos // USER) * SECTOR)
                            filler += bytes([user_data(fo.read(SECTOR))[pos % USER]])
                p[1] += filler + o
                p[2] += filler + m
                continue
        merged.append([off, bytearray(o), bytearray(m)])
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("original")
    ap.add_argument("out")
    ap.add_argument("--variant", nargs=3, action="append", required=True,
                    metavar=("CODIGO", "NOME", "DISCO"))
    ap.add_argument("--extra", nargs=2, action="append", default=[],
                    metavar=("CODIGO", "TOML"),
                    help="anexa [[patch]]/[[overlay]] extras de um idioma "
                         "(ex.: mods/lang_extra/en.toml)")
    ap.add_argument("--version", default="0.1.0")
    ap.add_argument("--game-id", default="SLPM-86033")
    ap.add_argument("--default", dest="default_lang", default=None,
                    help="idioma ligado por padrão numa instalação nova "
                         "(omitido = mod desligado = japonês)")
    a = ap.parse_args()
    codes = {v[0] for v in a.variant}
    for code, _ in a.extra:
        if code not in codes:
            raise SystemExit(f"--extra {code}: idioma não está entre os --variant")
    if a.default_lang and a.default_lang not in codes:
        raise SystemExit(f"--default {a.default_lang}: idioma não está entre os --variant")

    pkg = "tobal2.language"
    root = os.path.join(a.out, pkg, a.version)
    if os.path.isdir(root):
        shutil.rmtree(root)
    os.makedirs(root)
    disc_sha = sha256_file(a.original)

    lines = [
        "format_version = 5",
        f'id = "{pkg}"',
        f'version = "{a.version}"',
        'name = "Tobal 2 - Language / Idioma"',
        'author = "Tobal2Recomp"',
        'description = "Changes the game text and font. Off = original Japanese."',
        'resolver = "declarative"',
        'save_compatibility = "shared"',
        "",
        "[[target]]",
        f'game_id = "{a.game_id}"',
        f'disc_sha256 = "{disc_sha}"',
        "",
        "[[feature]]",
        'id = "language"',
        'name = "Language / Idioma"',
        'description = "Game language. Disabled = original Japanese."',
        'group = "Localization"',
        f"default_enabled = {'true' if a.default_lang else 'false'}",
        "",
        "[[option]]",
        'feature = "language"',
        'id = "lang"',
        'label = "Language / Idioma"',
        'description = "Text language used in menus, Quest mode and dialogue."',
        'group = "Localization"',
        'type = "choice"',
        f'default = "{a.default_lang or a.variant[0][0]}"',
    ]
    for code, label, _ in a.variant:
        lines += ["", "[[option.choice]]", f'value = "{code}"', f'label = "{label}"']

    total = 0
    for code, label, path in a.variant:
        runs = changed_runs(a.original, path)
        os.makedirs(os.path.join(root, code))
        nbytes = 0
        for off, orig, new in runs:
            name = f"{code}/{off:09d}.dat"
            with open(os.path.join(root, name), "wb") as f:
                f.write(new)
            nbytes += len(new)
            lines += [
                "",
                "[[overlay]]",
                'feature = "language"',
                'target = "disc_user"',
                f"offset = {off}",
                f'file = "{name}"',
                f'sha256 = "{hashlib.sha256(new).hexdigest()}"',
                f'expected_sha256 = "{hashlib.sha256(orig).hexdigest()}"',
                f'when = {{ lang = "{code}" }}',
            ]
        total += len(runs)
        print(f"{code} ({label}): {len(runs)} trechos, {nbytes} bytes")
    for code, path in a.extra:
        with open(path, encoding="utf-8") as f:
            lines += ["", f"# --- extras de '{code}' ({os.path.basename(path)}) ---", f.read().rstrip()]
        print(f"{code}: extras anexados de {path}")
    with open(os.path.join(root, "manifest.toml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{pkg} {a.version}: {total} overlays -> {root}")


if __name__ == "__main__":
    main()

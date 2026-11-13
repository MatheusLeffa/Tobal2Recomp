"""Gera um pacote de mod de idioma a partir de duas imagens do Tobal 2.

Uso:
    python tools/make_lang_mod.py ORIGINAL.bin TRADUZIDO.bin SAIDA_DIR \
        --lang en --label English [--version 0.1.0]

Compara as duas imagens setor a setor (MODE2/2352) e escreve
SAIDA_DIR/<id>/<versão>/manifest.toml com um [[overlay]] disc_raw por setor
alterado (o setor traduzido inteiro, com EDC/ECC), guardado pelo SHA-256 do
setor original e pelo SHA-256 do disco original.

O pacote gerado contém dados do disco traduzido (trabalho dos tradutores):
NÃO coloque a saída no Git. Use uma pasta ignorada, como analysis/.
"""
import argparse
import hashlib
import os

SECTOR = 2352


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("original")
    ap.add_argument("translated")
    ap.add_argument("out")
    ap.add_argument("--lang", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--version", default="0.1.0")
    ap.add_argument("--game-id", default="SLPM-86033")
    a = ap.parse_args()

    if os.path.getsize(a.original) != os.path.getsize(a.translated):
        raise SystemExit("as imagens têm tamanhos diferentes; este gerador só "
                         "faz trocas de setor do mesmo tamanho")
    pkg_id = f"tobal2.language.{a.lang}"
    root = os.path.join(a.out, pkg_id, a.version)
    sec_dir = os.path.join(root, "sectors")
    os.makedirs(sec_dir, exist_ok=True)

    changed = []
    with open(a.original, "rb") as fo, open(a.translated, "rb") as ft:
        lba = 0
        while True:
            so, st = fo.read(SECTOR), ft.read(SECTOR)
            if not so:
                break
            if so != st:
                name = f"sectors/{lba:06d}.bin"
                with open(os.path.join(root, name), "wb") as f:
                    f.write(st)
                changed.append((lba, name, hashlib.sha256(st).hexdigest(),
                                hashlib.sha256(so).hexdigest()))
            lba += 1

    disc_sha = sha256_file(a.original)
    lines = [
        "format_version = 5",
        f'id = "{pkg_id}"',
        f'version = "{a.version}"',
        f'name = "Tobal 2 - {a.label}"',
        'author = "Tobal2Recomp (gerado por tools/make_lang_mod.py)"',
        f'description = "Troca os textos e a fonte do jogo para {a.label}. '
        f'{len(changed)} setores do disco original, sem mexer no código."',
        'resolver = "declarative"',
        'save_compatibility = "shared"',
        "",
        "[[target]]",
        f'game_id = "{a.game_id}"',
        f'disc_sha256 = "{disc_sha}"',
        "",
        "[[feature]]",
        'id = "language"',
        f'name = "Idioma: {a.label}"',
        f'description = "Jogo em {a.label}. Desligado = japonês original."',
        'group = "Localization"',
        "default_enabled = false",
    ]
    for lba, name, sha, sha_stock in changed:
        lines += [
            "",
            "[[overlay]]",
            'feature = "language"',
            'target = "disc_raw"',
            f"offset = {lba * SECTOR}",
            f'file = "{name}"',
            f'sha256 = "{sha}"',
            f'expected_sha256 = "{sha_stock}"',
        ]
    with open(os.path.join(root, "manifest.toml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{pkg_id} {a.version}: {len(changed)} setores -> {root}")


if __name__ == "__main__":
    main()

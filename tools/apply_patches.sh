#!/usr/bin/env bash
# Aplica os patches de patches/<submódulo>/*.patch nos submódulos psxrecomp/ e
# recomp-ui/ (veja patches/README.md). Rode na raiz do repositório, depois de
# `git submodule update --init --recursive`.
#
#   bash tools/apply_patches.sh           aplica (sem commit) o que falta
#   bash tools/apply_patches.sh --check   só confere; sai com erro se faltar
#
# Idempotente: um patch já aplicado é reconhecido e pulado.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHECK=0
[[ "${1:-}" == "--check" ]] && CHECK=1

status=0
for sub in psxrecomp recomp-ui; do
  shopt -s nullglob
  patches=("$ROOT/patches/$sub"/*.patch)
  shopt -u nullglob
  [[ ${#patches[@]} -eq 0 ]] && continue
  if [[ ! -d "$ROOT/$sub/.git" && ! -f "$ROOT/$sub/.git" ]]; then
    echo "erro: $sub/ não é um submódulo inicializado (rode git submodule update --init --recursive)" >&2
    exit 1
  fi
  for p in "${patches[@]}"; do
    name="$sub/$(basename "$p")"
    if git -C "$ROOT/$sub" apply --reverse --check "$p" >/dev/null 2>&1; then
      echo "já aplicado: $name"
    elif [[ $CHECK -eq 1 ]]; then
      echo "FALTA aplicar: $name"
      status=1
    elif git -C "$ROOT/$sub" apply --check "$p" >/dev/null 2>&1; then
      git -C "$ROOT/$sub" apply "$p"
      echo "aplicado: $name"
    else
      echo "erro: $name não aplica limpo nesta versão do submódulo" >&2
      exit 1
    fi
  done
done
exit $status

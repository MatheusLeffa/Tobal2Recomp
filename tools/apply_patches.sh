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
  # Os patches de um submódulo formam uma pilha: um pode mexer no que o
  # anterior mudou, então o primeiro deixa de "desfazer" sozinho quando o
  # seguinte está aplicado. Por isso a pilha conta como aplicada quando o
  # ÚLTIMO patch desfaz limpo, e a aplicação vai um por um, na ordem.
  last="${patches[${#patches[@]}-1]}"
  if git -C "$ROOT/$sub" apply --reverse --check "$last" >/dev/null 2>&1; then
    for p in "${patches[@]}"; do echo "já aplicado: $sub/$(basename "$p")"; done
    continue
  fi
  if [[ $CHECK -eq 1 ]]; then
    echo "FALTA aplicar: patches de $sub"
    status=1
    continue
  fi
  for p in "${patches[@]}"; do
    name="$sub/$(basename "$p")"
    if git -C "$ROOT/$sub" apply --check "$p" >/dev/null 2>&1; then
      git -C "$ROOT/$sub" apply "$p"
      echo "aplicado: $name"
    elif git -C "$ROOT/$sub" apply --reverse --check "$p" >/dev/null 2>&1; then
      echo "já aplicado: $name"
    else
      echo "erro: $name não aplica limpo nesta versão do submódulo" >&2
      exit 1
    fi
  done
done
exit $status

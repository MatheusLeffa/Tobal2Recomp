# Ambiente de desenvolvimento (Windows)

## Ferramentas desta máquina (verificadas em 12/11/2026)

| Ferramenta | Versão | Para quê |
| --- | --- | --- |
| Git | 2.52 | controle de versão e submódulos |
| GitHub CLI (`gh`) | 2.96 | publicar no GitHub |
| Python | 3.14 | scripts do PSXRecomp |
| Toolchain RetroPorting `cmake-clang-v1` | CMake 3.31, Ninja, Clang (llvm-mingw) | compilar o recompilador e o jogo |

O toolchain fica em
`%USERPROFILE%\.local\share\retcomm\toolchains\cmake-clang-v1\latest`
(no Linux/macOS: `~/.local/share/retcomm/toolchains/cmake-clang-v1/latest`)
e o setup do PSXRecomp o coloca no PATH.

## Clonar com os submódulos

```bash
git clone --recurse-submodules <url>
# ou, num clone que já existe:
git submodule update --init --recursive
```

## Compilar o recompilador (uma vez por máquina)

Gera `build-recompiler/psxrecomp-game.exe` e `psxrecomp-bios.exe`:

```bash
PSXRECOMP_TOOLCHAIN_DIR="$HOME/.local/share/retcomm/toolchains/cmake-clang-v1/latest" \
  bash psxrecomp/tools/ci/build_emitters.sh --framework psxrecomp --build-dir build-recompiler
```

## Compilar o runtime de teste (sem jogo)

Roda só a BIOS (OpenBIOS) recompilada. Serve para provar que o ambiente funciona:

```bash
cmake -S psxrecomp/runtime -B build-runtime -G Ninja -DCMAKE_BUILD_TYPE=Release -DPSX_RECOMP_UI=OFF
cmake --build build-runtime --target psx-runtime
```

## Gerar e compilar o jogo (precisa do disco)

Ver a Fase 1 em `ROADMAP.md`.

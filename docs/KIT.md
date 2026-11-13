# Kit de instalação (setup host)

O kit é o que a comunidade baixa: um launcher **sem nenhum código do jogo**.
Cada pessoa escolhe o próprio BIN/CUE, e o launcher gera e compila o Tobal 2 no
PC dela. Nada do jogo é distribuído.

## Fluxo do jogador

1. Baixa o kit e extrai.
2. Abre `Tobal_2_Recompiled.exe` (precisa de Python 3 instalado).
3. Escolhe o disco (`.cue`) e clica em **Generate & rebuild**.
4. O launcher gera o C (~1 min) e compila (~2–3 min), com barra de progresso.
   Se for preciso, ele baixa o compilador (`cmake-clang-v1`) sozinho.
5. O jogo pronto fica em `build-release/`; reabrir o exe da raiz encaminha
   direto para ele.

## Montar o kit (Windows)

Pré-requisitos: recompilador compilado (`build-recompiler/`, ver `AMBIENTE.md`)
e os patches de `patches/` aplicados nos submódulos (`psxrecomp/` e `recomp-ui/`).

```bash
# 1. Launcher sem código do jogo
cmake -S . -B build-setuphost -G Ninja -DCMAKE_BUILD_TYPE=Release -DPSXRECOMP_FORCE_SETUP_HOST=ON
cmake --build build-setuphost --target psx-runtime

# 2. Empacotar (gera dist/stage-setup-windows-x64/)
bash psxrecomp/tools/package_setup_host.sh --build-dir build-setuphost \
  --artifact windows-x64 --zip-prefix tobal2 --exe-name Tobal_2_Recompiled \
  --display-name "Tobal 2 Recompiled" --recompiler-build build-recompiler \
  --disc-hint "your own Tobal 2 (Japan) disc, SLPM-86033" \
  --project-file game.toml --project-file game_options.toml \
  --project-file CMakeLists.txt --project-file codegen_setup.c \
  --project-file codegen_setup.h --project-file symbols.toml \
  --project-file psx_symbols.h --project-file VERSION \
  --project-file catalog_identity.json \
  --project-dir seeds --project-dir assets --project-dir mods
```

O último passo do script (`zip`) falha no Windows sem o comando `zip`; a pasta
`dist/stage-setup-windows-x64/` já é o kit completo. Nos releases do GitHub
(Linux) o `zip` existe.

## Testado (12/11/2026)

- Kit de 158 MB, sem disco, BIOS ou código gerado.
- Usuário novo em pasta limpa: gerar 51 s + compilar 116 s → jogo até a tela de
  título.
- Pelo launcher, com cliques: compila na própria janela, sem CMD, e abre o jogo.

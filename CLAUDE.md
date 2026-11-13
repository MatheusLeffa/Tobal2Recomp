# Tobal2Recomp: instruções para o Claude

## Contexto

- Port nativo de Tobal 2 (PS1, SLPM-86033) via recompilação estática com o
  PSXRecomp. O dono do projeto **não programa**: o Claude faz o trabalho
  técnico e explica em português, de forma simples.
- Antes de agir, leia `docs/ROADMAP.md` para saber em que fase estamos.
  Atualize a lista de tarefas de lá quando uma etapa terminar.

## Regras

1. **Nada de dados do jogo no Git.** Disco (`iso/`), arquivos extraídos (`disc/`),
   BIOS, saves e o C gerado (`generated/`) ficam fora do repositório.
   Confira `git status` antes de cada commit.
2. **Não edite `psxrecomp/` nem `recomp-ui/`.** São submódulos fixados em um
   commit. Correções no framework viram issue ou PR no repositório
   upstream; atualizar o submódulo é uma decisão explícita.
3. **Não edite código gerado.** Se o C gerado estiver errado, corrija a entrada
   (`game.toml`, `seeds/`, `symbols.toml`) e gere de novo.
4. Mudanças específicas do Tobal 2 (widescreen, mods, tradução) vão em
   `src/mods/`, `mods/preloaded/` ou `game.toml`, seguindo os docs do framework
   (`psxrecomp/docs/`). Use o BattleArenaToshindenRecomp como exemplo de jogo de luta.
5. Meta de cada fase = algo visível na tela, comparado com um emulador.

## Comandos (depois que o disco existir)

```bash
python psxrecomp/psxrecomp_cli.py generate --config game.toml --project-root . --disc "iso/Tobal 2 (Japan) (v1.1).cue"
python psxrecomp/psxrecomp_cli.py rebuild --config game.toml --project-root . --build-dir build-release --no-pgo
```

Toolchain: `%USERPROFILE%\.local\share\retcomm\toolchains\cmake-clang-v1\latest`
(definir `PSXRECOMP_TOOLCHAIN_DIR` com esse caminho).

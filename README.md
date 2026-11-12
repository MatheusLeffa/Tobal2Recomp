# Tobal 2 Recompiled

Port nativo para PC de **Tobal 2** (PlayStation, Square / DreamFactory, 1997),
feito por **recompilação estática**: o código MIPS do jogo original é traduzido
para C e compilado como um programa Windows de verdade, sem emulador.

Construído em cima do framework [PSXRecomp](https://github.com/RetroPortingToolKit/psxrecomp)
e da interface [recomp-ui](https://github.com/RetroPortingToolKit/recomp-ui),
que já rodam jogos de luta 3D parecidos (Battle Arena Toshinden,
Dragon Ball GT: Final Bout).

> **Status: preparação.** O repositório, o framework e as ferramentas estão
> prontos. Falta o dump do disco para gerar o código do jogo — ver
> [docs/DUMP_DO_DISCO.md](docs/DUMP_DO_DISCO.md).

## Objetivos

1. Rodar Tobal 2 nativamente no PC, do boot até a luta e o modo Quest.
2. Melhorias opcionais: resolução interna alta, sem tremedeira de polígonos
   (PGXP), widescreen, controles modernos.
3. Base para mods: tradução para inglês/português, alterações de jogabilidade,
   personagens, netplay.

## Versões do disco suportadas

| Versão | Serial | Situação |
| --- | --- | --- |
| Tobal 2 (Japão), original de 1997 | SLPM-86033 | alvo principal |
| Tobal 2 [Legendary Hits] (Japão) | SLPM-87406 | talvez no futuro |

## Aviso legal

Este repositório **não contém** nenhum dado do jogo, BIOS da Sony nem código
gerado a partir do jogo. Para usar, você precisa do **seu próprio disco
original** e fazer o dump dele. Tobal 2 é marca da Square Enix; este é um
projeto de fã, sem fins comerciais.

## Estrutura

```text
Tobal2Recomp/
├── psxrecomp/      submódulo: recompilador + runtime de hardware do PS1
├── recomp-ui/      submódulo: launcher (escolha do disco, opções, mods)
├── docs/           pesquisa, roadmap, guias
├── iso/            (local, ignorado) seu dump .bin/.cue
└── generated/      (local, ignorado) C gerado a partir do seu disco
```

## Clonar

```bash
git clone --recurse-submodules <url-deste-repositório>
```

## Documentação

- [docs/PESQUISA.md](docs/PESQUISA.md): o que foi pesquisado e por que
  escolhemos o PSXRecomp.
- [docs/ROADMAP.md](docs/ROADMAP.md): fases do projeto.
- [docs/DUMP_DO_DISCO.md](docs/DUMP_DO_DISCO.md): como fazer o dump do disco.
- [docs/AMBIENTE.md](docs/AMBIENTE.md): ferramentas necessárias e como compilar.

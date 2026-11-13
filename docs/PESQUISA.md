# Pesquisa (novembro de 2026)

## Pergunta

Qual a melhor forma de transformar Tobal 2 (PS1) em um programa nativo de PC,
que possa ser modificado depois?

## Caminhos possíveis

| Caminho | Como funciona | Prós | Contras |
| --- | --- | --- | --- |
| **Recompilação estática** | Uma ferramenta traduz cada instrução MIPS do executável para C; um runtime substitui o hardware do PS1 | Roda rápido; não exige entender o jogo inteiro; mods podem ser feitos aos poucos | Código gerado é ilegível; overlays carregados do CD dão trabalho |
| **Decompilação (matching)** | Reescrever cada função à mão em C até gerar bytes idênticos (ex.: sotn-decomp, com splat + maspsx) | Código limpo e totalmente modificável | Anos de trabalho manual |
| **Recompilador próprio do zero** | Escrever nosso próprio tradutor MIPS→C e runtime | Controle total | Reinventar o que já existe e funciona |

**Decisão:** recompilação estática usando o **PSXRecomp**. Partes do jogo que
quisermos modificar a fundo podem ser decompiladas à mão depois, por cima.

## Ferramentas encontradas

### PSXRecomp, a escolhida
<https://github.com/RetroPortingToolKit/psxrecomp>

- Framework beta e ativo (atualizado em nov/2026), cerca de 400 estrelas, mantido pela
  comunidade RetroPortingToolkit (Discord R.A.I.D.).
- Traduz MIPS R3000A → C; runtime completo: GPU (OpenGL, Vulkan, software),
  GTE, SPU, CD-ROM/XA/MDEC, controles, memory card, timers e interrupções.
- BIOS: usa o **OpenBIOS** (livre, MIT), então não precisa de BIOS da Sony.
- **Overlays** (código que o jogo carrega do CD durante a execução): captura → compila →
  cache; um interpretador MIPS pequeno cobre o que ainda não foi compilado.
- Extras prontos: widescreen real (alarga o campo de visão), PGXP (sem
  tremedeira), resolução interna alta, sistema de mods `.psxmod`, tradução
  de texto trocada com o jogo rodando, netplay com rollback.
- Jogos parecidos já portados: **Battle Arena Toshinden** (luta 3D, netplay,
  mod de personagens extras), **Dragon Ball GT: Final Bout** (luta 3D),
  **Tsumu Light** (jogo japonês com tradução).
- Licença: **PolyForm Noncommercial 1.0.0**, que permite uso e modificação sem
  fins comerciais.
- O autor original fez o protótipo sem experiência prévia, usando Claude Code:
  <https://1379.tech/i-built-a-ps1-static-recompiler-with-no-prior-experience-and-claude-code/>

### Alternativas avaliadas

- **PS1Recomp**: <https://github.com/PS1Recomp/ps1-recomp>. Projeto de TCC,
  ainda não é um runtime completo.
- **AlienReRecomp**: <https://github.com/DiegoDeDios/AlienReRecomp> (MIT).
  Recomp de um único jogo (Alien Resurrection), boa referência de arquitetura.
- **MimiPS1**: <https://github.com/wlfrotaneto/MimiPS1>. Feito para
  Apple Silicon.
- **N64Recomp**: <https://github.com/N64Recomp/N64Recomp>. Projeto que
  inspirou essa abordagem (Majora's Mask), para N64.
- **Ferramentas de decompilação de PS1**: splat
  (<https://github.com/ethteck/splat>), maspsx (<https://github.com/mkst/maspsx>),
  PSY-Z (decompilação das bibliotecas PSY-Q), sotn-decomp
  (<https://github.com/Xeeynamo/sotn-decomp>). São úteis se um dia formos
  decompilar partes à mão.

## O que se sabe sobre o Tobal 2

- Desenvolvido pela DreamFactory e publicado pela Square, lançado em 25/04/1997, só no Japão.
- Seriais: **SLPM-86033** (original) e **SLPM-87406** (Legendary Hits)
  (fonte: psxdatacenter.com).
- Conhecido por rodar a 60 fps em alta resolução no PS1. Tem um modo Quest
  (dungeon crawler) e um elenco enorme de personagens desbloqueáveis.
- **Não existe** recomp nem decompilação pública do Tobal 2 (verificado em nov/2026).
- O disco original existe em pelo menos uma revisão **v1.1**; é a que o
  projeto suporta (SLPM-86033 v1.1, confere com o Redump).

## Riscos conhecidos

- **Overlays:** o modo Quest e as lutas provavelmente carregam código diferente
  do CD. O PSXRecomp lida com isso (captura e cache), mas cada overlay
  precisa ser exercitado jogando.
- **60 fps em alta resolução:** o jogo faz uso pesado da GPU e do GTE. Pode
  revelar problemas de timing no runtime.
- **Texto em japonês:** a tradução para inglês ou português vai usar o sistema
  de tradução do PSXRecomp (`docs/STRING_TRANSLATION.md`) ou mods de dados.

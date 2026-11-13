# Roadmap

Cada fase só termina quando o resultado é **visível**: o jogo na tela, não
"deve funcionar".

## Fase 0: Preparação (quase pronta)

- [x] Pesquisa de ferramentas (ver `PESQUISA.md`)
- [x] Repositório Git com PSXRecomp e recomp-ui como submódulos
- [x] Toolchain (CMake, Ninja, Clang) instalado e testado
- [x] Recompilador do PSXRecomp compilado nesta máquina (`build-recompiler/`)
- [x] Runtime de teste rodando: o OpenBIOS recompilado mostra o cubo
      girando, em OpenGL e resolução 4x (12/11/2026)
- [x] Dump do disco original: SLPM-86033 v1.1, SHA-1 `50edccaa…` confere
      com o Redump (disco 10087)

## Fase 1: Primeiro boot ✅ (12/11/2026)

Resultado: logo da DreamFactory → vídeo de abertura (MDEC) → tela de título
→ seleção de personagem → luta do Torneio (Chuji vs Epon, Stage 1) rodando
nativamente, com OpenGL e resolução 4x. Foram geradas cerca de 3.750 funções e 12 milhões de linhas de C.

Como foi feito:

1. Colocar o dump em `iso/` (`.cue` + `.bin`).
2. Rodar o scaffold do PSXRecomp numa pasta temporária. Ele recusa pastas que
   já existem, então copiamos de lá para cá os arquivos de projeto
   (`game.toml`, `CMakeLists.txt`, `codegen_setup.c/.h`, `seeds/`,
   `symbols.toml`, `catalog_identity.json`, `.recomp.json`, `mods/`, `assets/`):

   ```powershell
   powershell -File psxrecomp\tools\new_project_layout\setup_project.ps1 `
     -Disc "<pasta do projeto>\iso\Tobal 2 (Japan) (v1.1).cue" `
     -Dir "<pasta temporária>" -Name Tobal2Recomp `
     -GithubRepo tobal2-scaffold -Players 2 -Yes -EnableRecompUi `
     -NoNetplay -NoFetchBoxart -NoGithub -Generate -EnableBuild
   ```
3. Gerar o C e compilar:

   ```bash
   python psxrecomp/psxrecomp_cli.py generate --config game.toml --project-root . --disc "iso/Tobal 2 (Japan) (v1.1).cue"
   python psxrecomp/psxrecomp_cli.py rebuild --config game.toml --project-root . --build-dir build-release --no-pgo
   ```
4. Rodar sem o launcher:
   `build-release/Tobal_2_Recompiled.exe --game game.toml --disc "iso/Tobal 2 (Japan) (v1.1).cue" --no-launcher`

## Fase 2: Jogável ← fase atual

- [x] Menu → seleção de personagem → luta começa (1P vs CPU)
- [ ] Jogar uma luta inteira com controle/teclado; depois 1P vs 2P.
- [ ] Conferir o som (músicas e efeitos).
- Modo Quest: entrar no primeiro andar da dungeon.
- Ir adicionando seeds e overlays conforme o jogo avança, até a cobertura nativa ficar perto de 100%.
- Sons, músicas (CD-DA/XA) e vídeos funcionando.
- Memory card: salvar e carregar.
- Comparar com um emulador confiável (DuckStation) para achar diferenças.

## Fase 3: Melhorias visuais

- Resolução interna 4x ou mais, PGXP (sem tremedeira, texturas com perspectiva correta).
- Widescreen: **descartado por enquanto** (12/11/2026). A versão por mod
  (squash do GTE + `auto_screen_x`) funcionou no título e nas lutas, mas vários
  objetos ficaram com bugs, e o dono decidiu remover. O que foi feito está no commit
  4fe6589 (revertido), caso um dia valha tentar de novo.
- Launcher com box art e mapeamento de controle.

## Fase 4: Mods

- Mapear o executável: nomear funções em `symbols.toml`, usando o Ghidra e o
  trabalho dos tradutores.
- Tradução: inglês (aproveitando o que já existe) e português.
- Mods de jogabilidade (`.psxmod`).
- Netplay com rollback, como no Toshinden.

## Kit de instalação (caminho A) ← em andamento

- [x] Launcher sem código do jogo (setup host) que gera e compila no PC do
      jogador (`docs/KIT.md`)
- [x] Setup no Windows sem CMD, com barra de progresso (patch no framework,
      `patches/`)
- [x] Idioma como configuração na tela inicial do launcher (cartão
      LANGUAGE): English (padrão) ou Japanese (original), sem gerar código de
      novo (`docs/IDIOMAS.md`, patch no recomp-ui)
- [ ] Português (texto + letras com acento na fonte)
- [x] Releases automáticos Windows / Linux / Mac no GitHub (workflow "Release
      kits", testado nos 4 sistemas; `docs/KIT.md`)
- [ ] Publicar a release v0.1.0 e enviar ao catálogo do Retro Launcher
      (`docs/retro-catalog/`)

## Fase 5: Publicação

- Publicar o repositório no GitHub (sem disco, BIOS nem código gerado).
- Release para Windows: o jogador aponta para o próprio disco e o launcher
  gera e compila o jogo localmente (Generate & Build).

## Decisões em aberto

- **Publicar `generated/` ou não?** O guia do PSXRecomp sugere publicar, para
  que o CI gere releases prontos. Mas esse C é uma tradução do código da
  Square. Por enquanto fica fora do Git (igual ao Toshinden); dá para mudar
  depois.
- **Licença do nosso código:** sugestão é PolyForm Noncommercial, a mesma do
  framework.

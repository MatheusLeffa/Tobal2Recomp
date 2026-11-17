# Patches nos submódulos

Mudanças nossas no PSXRecomp e no recomp-ui que ainda não estão nos
repositórios oficiais. Os submódulos continuam apontando para os commits
oficiais; estes patches são aplicados por cima antes de compilar.

| Patch | O que faz |
| --- | --- |
| `psxrecomp/0001-host-Windows-first-run-setup-builds-in-process-no-co.patch` | No Windows, o primeiro setup compila dentro da janela do launcher, com barra de progresso, sem abrir CMD |
| `psxrecomp/0002-launcher-dashboard-cards-selects-the-cards-home.patch` | Lê `[launcher] dashboard = "cards"` do `game.toml` e avisa o launcher |
| `psxrecomp/0003-generate-accept-a-renamed-bin-beside-a-single-FILE-c.patch` | O Generate aceita `.bin` renomeado: se o `.cue` aponta para um arquivo que não existe, usa o `.bin` com o mesmo nome do `.cue` (igual o jogo já fazia) |
| `psxrecomp/0004-mods-read-a-renamed-bin-beside-a-broken-cue-like-the.patch` | A parte de mods também aceita `.bin` renomeado: antes, com o `.cue` "quebrado", o Play dava "cannot open stock image range" e era preciso escolher o `.bin` na mão |
| `psxrecomp/0005-host-prepare-builds-the-game-without-a-window-for-st.patch` | `Tobal_2_Recompiled --prepare --disc <.cue>`: faz o que a janela de setup faz (ferramentas, Generate, compilar), sem janela, com linhas `progress <0..1> <texto>`. É o passo "Setting it up" do Easy Setup do Recomp Launcher (`recomplauncher.json`, `prepare`) |
| `recomp-ui/0001-dashboard-LANGUAGE-card-for-a-title-s-Language-mod-f.patch` | Cartão LANGUAGE na tela inicial do launcher para a feature de mod do grupo "Language" (o seletor English / Japanese) |
| `recomp-ui/0002-dashboard-settings-cards-for-the-Language-and-Charac.patch` | Generaliza o cartão: features dos grupos "Language" e "Characters" viram cartões na tela inicial (LANGUAGE e CHARACTERS) |
| `recomp-ui/0003-dashboard-cards-layout-cover-disc-controllers-and-se.patch` | Tela inicial "cards": capa à esquerda e quatro cartões (disco, controles, idioma, personagens) |

Nenhum deles foi enviado aos projetos oficiais ainda.

## Aplicar

```bash
git -C psxrecomp am ../patches/psxrecomp/*.patch
git -C recomp-ui am ../patches/recomp-ui/*.patch
```

(Ou `git -C <submódulo> apply ../patches/<submódulo>/*.patch` para aplicar sem
commit.)

Quando um patch for aceito no projeto oficial, atualize o submódulo para a
versão que já tem a mudança e apague o patch daqui.

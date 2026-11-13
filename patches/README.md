# Patches nos submódulos

Mudanças nossas no PSXRecomp e no recomp-ui que ainda não estão nos
repositórios oficiais. Os submódulos continuam apontando para os commits
oficiais; estes patches são aplicados por cima antes de compilar.

| Patch | O que faz |
| --- | --- |
| `psxrecomp/0001-host-Windows-first-run-setup-builds-in-process-no-co.patch` | No Windows, o primeiro setup compila dentro da janela do launcher, com barra de progresso, sem abrir CMD |
| `recomp-ui/0001-dashboard-LANGUAGE-card-for-a-title-s-Language-mod-f.patch` | Cartão LANGUAGE na tela inicial do launcher para a feature de mod do grupo "Language" (o seletor English / Japanese) |

Nenhum dos dois foi enviado aos projetos oficiais ainda.

## Aplicar

```bash
git -C psxrecomp am ../patches/psxrecomp/*.patch
git -C recomp-ui am ../patches/recomp-ui/*.patch
```

(Ou `git -C <submódulo> apply ../patches/<submódulo>/*.patch` para aplicar sem
commit.)

Quando um patch for aceito no projeto oficial, atualize o submódulo para a
versão que já tem a mudança e apague o patch daqui.

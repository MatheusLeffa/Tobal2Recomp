# Patches no framework

Mudanças nossas no PSXRecomp que ainda não estão no repositório oficial.
O submódulo `psxrecomp/` continua apontando para o commit oficial; estes patches
são aplicados por cima antes de compilar o kit.

| Patch | O que faz | Situação |
| --- | --- | --- |
| `psxrecomp/0001-host-Windows-first-run-setup-builds-in-process-no-co.patch` | No Windows, o primeiro setup compila dentro da janela do launcher, com barra de progresso, sem abrir CMD | Ainda não enviado para o upstream |

## Aplicar

```bash
git -C psxrecomp am ../patches/psxrecomp/*.patch
```

(Ou `git -C psxrecomp apply ../patches/psxrecomp/*.patch` para aplicar sem commit.)

Quando um patch for aceito no PSXRecomp oficial, atualize o submódulo para a
versão que já tem a mudança e apague o patch daqui.

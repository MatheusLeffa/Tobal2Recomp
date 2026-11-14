# Retro Launcher (catálogo)

`tobal2-psx.json` é o manifest do Tobal 2 para o
[Retro Catalog](https://github.com/RetroPortingToolKit/Retro-Catalog), no
formato do `SCHEMA.md` de lá.

## Situação

- [x] Repositório público: `MatheusLeffa/Tobal2Recomp`.
- [x] Release **v0.1.0** com um kit por sistema
  (`tobal2-0.1.0-{windows-x64,linux-x64,macos-arm64,macos-x64}.zip`), que
  casam com os `asset_glob` `*windows*` / `*linux*` / `*macos*`. O ZIP
  automático do GitHub não traz os submódulos nem os nossos patches; os kits
  trazem.
- [x] `build.source.ref` = `main` (o Retro usa o kit da release mais recente; o ref só é usado se o kit não trouxer o código); `toolchain.min_version` = `1.0.14`, a versão com que os kits foram testados.
- [x] Enviado pelo formulário em 13/11/2026:
  <https://github.com/RetroPortingToolKit/Retro-Catalog/issues/61>
  (id `tobal2-psx`). O envio saiu com `min_version` 1.0.3 e `build_dir`
  `build`; os dois funcionam (a versão é só o mínimo aceito, e a pasta de
  build é só um nome).
- [ ] Um mantenedor aprova (label `approved`), o título entra no
  `catalog.zip` e aparece no Retro Launcher. Depois disso, testar a
  instalação pelo launcher.

Para mudar o manifest depois de aprovado, envie de novo pelo formulário; o
mantenedor usa o label `approved-update`.

## Como enviar

1. Abrir <https://retroportingtoolkit.github.io/Retro-Catalog/submit/> e
   entrar com a conta do GitHub.
2. Plataforma **PSX**; repositório `MatheusLeffa/Tobal2Recomp`. O formulário
   lê o repositório e preenche hashes e nomes dos kits.
3. Conferir os campos com `tobal2-psx.json` (principalmente `launch` =
   `Tobal_2_Recompiled` / `Tobal_2_Recompiled.exe`, `install_dir_name`, a seção
   `build` e os hashes). O formulário pede que você calcule os hashes do seu
   disco localmente: eles devem bater com os do manifest.
4. Enviar. Ele abre uma issue no Retro-Catalog; um mantenedor aprova (label
   `approved`) e o título entra no próximo `catalog.zip`.

Os hashes vêm do `game.toml` (`[prepare_disc]`) e batem com o Redump do disco
original (SLPM-86033 v1.1). Netplay não está ligado, então o manifest não tem
a seção `netplay`.

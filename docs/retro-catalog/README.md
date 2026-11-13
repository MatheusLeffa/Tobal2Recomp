# Retro Launcher (catálogo)

`tobal-2-psx.json` é o rascunho do manifest do Tobal 2 para o
[Retro Catalog](https://github.com/RetroPortingToolKit/Retro-Catalog), no
formato do `SCHEMA.md` de lá.

## Antes de enviar

1. Conferir o dono do repositório (`MatheusLeffa/Tobal2Recomp`, 3 lugares).
2. Ter uma **release** no GitHub com um kit por sistema, com nomes contendo
   `windows`, `linux` e `macos` (ex.: `tobal2-0.1.0-windows-x64.zip`). O ZIP
   automático do GitHub não traz os submódulos nem os nossos patches, então o
   Retro precisa desses kits.
3. Conferir `build.source.ref` (tag da release) e `toolchain.min_version`.
4. Enviar pelo formulário oficial (login no GitHub):
   <https://retroportingtoolkit.github.io/Retro-Catalog/submit/>. Ele lê o
   repositório, preenche os hashes e abre uma issue para os mantenedores
   aprovarem.

Os hashes vêm do `game.toml` (`[prepare_disc]`) e batem com o Redump do disco
original (SLPM-86033 v1.1). Netplay não está ligado, então o manifest não tem
a seção `netplay`.

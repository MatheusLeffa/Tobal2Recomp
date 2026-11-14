# Tobal 2 Recompiled

A native PC port of **Tobal 2** (PlayStation, Square / DreamFactory, 1997), made
by **static recompilation**: the game's original MIPS code is translated to C
and compiled into a real Windows / Linux / macOS program. It is not an
emulator. Built on [PSXRecomp](https://github.com/RetroPortingToolKit/psxrecomp)
and [recomp-ui](https://github.com/RetroPortingToolKit/recomp-ui).

> **No game data is included.** You need your own copy of the original
> Japanese disc. The game code is generated and compiled on your own computer
> from that disc; this repository contains only tools, configuration and the
> language data.

## Status: playable

- Boots, plays the intro FMV, title screen, Tournament / VS / Training fights
  and Quest mode, all running as native code.
- **Language: English (default) or Japanese (original)**, picked on the
  launcher's home screen. Switching does not require rebuilding.
- The English title menu box is widened so every option fits.
- **Characters: Original or All unlocked**, picked on the launcher's home
  screen (default Original). All unlocked makes every fighter selectable from
  the start, secret ones included; saves are not changed. On Windows it can
  also be switched while playing, from the game window's menu bar (**Options →
  Unlock all characters**; hidden in fullscreen): it applies the next time the
  character select screen opens.
- High internal resolution (4x by default, OpenGL renderer).

Not yet verified end to end: the whole Quest mode, every ending, memory-card
saves in every mode. Reports are welcome in Issues.

## Supported disc

| Game | Serial | Region | Format |
| --- | --- | --- | --- |
| Tobal 2 (v1.1) | SLPM-86033 | Japan (NTSC-J) | BIN/CUE, 1 track |

Data track (`Tobal 2 (Japan) (v1.1).bin`, 669,555,600 bytes):

| Hash | Value |
| --- | --- |
| CRC32 | `479f1388` |
| MD5 | `9d583bcc0ee949f42e07fa8613939d8d` |
| SHA-1 | `50edccaaccf002673a817047905372603e63e208` |
| SHA-256 | `04e79535b4616963e045957b4f9b87126753e94b01d35d32c60214df04bf5a5a` |

This matches the Redump dump of the retail disc. Other revisions and patched
images are rejected. The game ships in Japanese only, so do **not** use a
pre-translated image: the English text is applied by this project on top of
the original disc.

Dump the disc as **BIN/CUE** (for example with ImgBurn, redumper or
DiscImageCreator), not as a 2048-byte `.iso`. The disc is recognized by its
contents, so the file names do not matter, as long as the `.cue` names the
`.bin` next to it.

## Playing

1. Get the setup package for your system from
   [Releases](../../releases) (or install through the
   [Retro Launcher](https://github.com/RetroPortingToolKit/Retro-Launcher)
   once the title is in its catalog).
2. Extract it and run `Tobal_2_Recompiled` (Python 3 is required for the
   first-time setup).
3. Pick your `.cue`, click **Generate & rebuild** and wait a few minutes. The
   launcher downloads the compiler it needs, converts the game code and builds
   it on your computer.
4. Choose the language on the home screen and press **PLAY**.

## Building from source

Requirements: Git, Python 3, and either the
[cmake-clang-v1](https://github.com/RetroPortingToolKit/RetroPorting-Toolchains/releases)
toolchain pack or CMake + Ninja + a C/C++ compiler.

```bash
git clone --recurse-submodules https://github.com/MatheusLeffa/Tobal2Recomp.git
cd Tobal2Recomp
bash tools/apply_patches.sh          # our changes to psxrecomp / recomp-ui
python psxrecomp/psxrecomp_cli.py generate --config game.toml --project-root . --disc "path/to/Tobal 2 (Japan) (v1.1).cue"
python psxrecomp/psxrecomp_cli.py rebuild  --config game.toml --project-root . --build-dir build-release --no-pgo
```

The executable is `build-release/Tobal_2_Recompiled` (`.exe` on Windows).
Never commit the disc, the extracted `disc/` files or `generated/`: they are
ignored by `.gitignore` on purpose.

## Repository layout

| Path | What it is |
| --- | --- |
| `game.toml`, `CMakeLists.txt`, `codegen_setup.*`, `seeds/`, `symbols.toml` | Title configuration for PSXRecomp |
| `mods/preloaded/packages/tobal2.language/` | Language package: only the bytes the English text changes, each guarded by the SHA-256 of the original disc data |
| `mods/preloaded/packages/tobal2.unlock/`, `src/mods/unlock_characters.c` | Characters setting: a plugin swaps five guarded instructions in the character select code, also while the game runs |
| `mods/lang_extra/en.toml` | Layout fixes applied with English (wider title menu box) |
| `patches/` | Our changes to the `psxrecomp` and `recomp-ui` submodules |
| `tools/` | Test automation and analysis tools (`nav.py`, `vram_dump.py`, `disc_diff.py`, `make_lang_mod.py`, `apply_patches.sh`) |
| `psxrecomp/`, `recomp-ui/` | Framework and launcher submodules |

## Legal

Tobal 2 is a trademark of Square Enix. This is a non-commercial fan project,
not affiliated with or endorsed by Square Enix or Sony. The repository and
its releases contain no disc image, no BIOS and no code generated from the
game. Use your own legally obtained disc.

## License

[PolyForm Noncommercial 1.0.0](LICENSE), the same license as PSXRecomp, from
which parts of this repository derive. `recomp-ui` is MIT licensed. Release
packages include OpenBIOS (MIT) from PCSX-Redux.

---

## Português

Port nativo do Tobal 2 para PC por recompilação estática, feito com o
PSXRecomp. Você precisa do **seu disco original japonês** (SLPM-86033 v1.1);
o jogo é gerado e compilado no seu computador. O idioma (**English** por
padrão ou **japonês original**) é escolhido na tela inicial do launcher.

Na tela inicial também dá para liberar todos os personagens (cartão
**CHARACTERS**), inclusive os secretos, sem mexer no save. No Windows, dá para
trocar com o jogo aberto pelo menu **Options** no topo da janela.

Faça o dump do disco em **BIN/CUE** (não `.iso`). O nome dos arquivos não
importa: o disco é reconhecido pelo conteúdo. Para jogar, siga os passos de
**Playing** acima.

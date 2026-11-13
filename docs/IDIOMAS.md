# Idiomas

## Como funciona

O idioma é o mod **`tobal2.language`**
(`mods/preloaded/packages/tobal2.language/`), que vem no catálogo do jogo:

- **Desligado** (padrão): japonês original, idêntico ao disco.
- **Ligado**: opção *Language / Idioma* escolhe o idioma (hoje: English).

O mod troca só os bytes de texto e de fonte que mudam no disco, na hora em
que o jogo lê o CD. O código recompilado é o mesmo para todos os idiomas, então
trocar de idioma não exige gerar nem compilar de novo.

Cada trecho é conferido pelo SHA-256 do disco original e do trecho original
antes de ser aplicado; com outro disco, o mod se recusa a ligar.

## Como o Tobal 2 guarda os textos

- **`SLPM_860.33` (executável):** um bloco de texto Shift-JIS em
  `0x800D7CB0`–`0x800D9A52` (modo Quest: história, itens, partes do corpo).
- **`ALLBIN.BIN`:** tabelas de texto numa codificação própria (menus,
  opções, diálogos dos NPCs) e os gráficos da fonte.
- A fonte japonesa é carregada sob demanda na VRAM (≈ x 960, y 0); a fonte
  latina grande (nomes, "READY") fica em ≈ x 832, y 256.
- Por isso a tradução automática do PSXRecomp (`text_xlate`, do Tsumu Light)
  não enxerga os menus do Tobal 2.

## Inglês

Gerado a partir da tradução de fã v1.00b. Ela muda só dados (32 setores):
7,5 KB de texto no executável, sem tocar em código, e ~25 KB em `ALLBIN.BIN`
(texto + letras latinas desenhadas na fonte). O mod guarda apenas os
**35 KB de bytes alterados** (395 trechos), nada do conteúdo original.

Verificado (12/11/2026): disco original + mod = disco em inglês, byte a byte;
título (TOURNAMENT / VS / QUEST / TRAINING / OPTIONS), Quest (NEW GAME,
Pick Fighter, história do imperador Udan) em inglês; mod desligado = japonês.

## Gerar ou adicionar um idioma

```bash
python tools/make_lang_mod.py "iso/Tobal 2 (Japan) (v1.1).bin" mods/preloaded/packages \
  --variant en English "iso/referencia-en/<disco em inglês>.bin" \
  [--variant pt "Português" "iso/<disco em português>.bin"]
```

Cada `--variant` vira uma escolha da opção *Language / Idioma*. O gerador só
aceita discos do mesmo tamanho do original (trocas no lugar).

(A versão do VincentNL, com letras de meia largura, muda **código**; não serve
para este gerador.)

## Próximo: português

- Partir dos textos em inglês (mesmas posições, mesmos limites de tamanho).
- Desenhar na fonte latina as letras com acento e o ç.
- Gerar um disco em português de trabalho e acrescentar `--variant pt`.

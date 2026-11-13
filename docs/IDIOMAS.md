# Idiomas

## Como o Tobal 2 guarda os textos

- O jogo **não** usa frases Shift-JIS passadas a uma função de desenho para os
  menus, então a tradução automática do PSXRecomp (`text_xlate`, usada no
  Tsumu Light) não enxerga o menu principal.
- Os textos ficam em dois lugares:
  - **`SLPM_860.33` (executável):** um bloco de texto Shift-JIS em
    `0x800D7CB0`–`0x800D9A52` (modo Quest: itens, partes do corpo, história).
  - **`ALLBIN.BIN`:** tabelas de texto numa codificação própria (menus,
    opções, diálogos dos NPCs) e os gráficos da fonte.
- A fonte japonesa é carregada sob demanda na VRAM (≈ x 960, y 0); a fonte
  latina grande (nomes, "READY") fica em ≈ x 832, y 256.

## Tradução em inglês existente

Comparando o disco original com o patch **Infinite Lupine v1.00b**
(`tools/disc_diff.py`):

| Arquivo | Mudança |
| --- | --- |
| `SLPM_860.33` | 7,5 KB, só texto; **nenhuma** faixa de código recompilado |
| `ALLBIN.BIN` | ~25 KB em 36 trechos: tabelas de texto + letras latinas na fonte |

Total: **32 setores** de 669 MB. Tudo é dado, então o idioma pode ser um mod
aplicado sobre o disco original, sem gerar o código de novo.

(A versão do VincentNL, com letras de meia largura, muda **código**; por isso
o alvo é a v1.00b / v1.01b.)

## Protótipo (12/11/2026) — funcionando

`tools/make_lang_mod.py` gera o pacote `tobal2.language.<código>` com um
`[[overlay]]` `disc_raw` por setor alterado, guardado pelo SHA-256 do disco
original e de cada setor:

```bash
python tools/make_lang_mod.py "iso/Tobal 2 (Japan) (v1.1).bin" \
  "iso/referencia-en/Tobal 2 (Japan) (v1.1) [En by Infinite Lupine v1.00b].bin" \
  analysis/mods --lang en --label English
# instalar localmente:
cp -r analysis/mods/tobal2.language.en build-release/mods/installed/
```

Resultado: com o mod ligado o título mostra TOURNAMENT / VS / QUEST /
TRAINING / OPTIONS; desligado, volta ao japonês. O pacote contém o trabalho
dos tradutores e **não vai para o Git** (fica em `analysis/`).

## Pendências

1. **Distribuição do inglês:** pedir permissão aos tradutores (Infinite
   Lupine, r4dius) **ou** fazer o mod ler os bytes de um arquivo que o jogador
   fornece (`[[resource]]` + overlay de recurso, formato 10). Se o patch
   oficial for PPF (bytes crus), os overlays podem apontar direto para ele.
2. **Português:** reaproveitar a fonte latina e as posições de texto da
   versão em inglês; desenhar letras com acento e ç.
3. **Escolha no launcher:** hoje é um mod liga/desliga na página Mods; depois
   juntar os idiomas numa única opção (Japonês / English / Português).

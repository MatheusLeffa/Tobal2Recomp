# Como fazer o dump do disco

O projeto precisa de uma cópia **bit a bit** do seu disco original de Tobal 2,
no formato **BIN/CUE**. Não use ISO "cozida" (2048 bytes por setor): ela perde
áudio XA e dados de setor que o jogo usa.

## 1. O que você precisa

- O disco original japonês de **Tobal 2** (SLPM-86033). Dá para encontrar usado
  em lojas de games retrô, no Mercado Livre ou no eBay.
- Um **leitor de CD/DVD** no PC. Este computador não tem leitor interno. Um
  leitor USB externo (gravador de DVD comum) funciona.

## 2. Programa recomendado

Opções gratuitas que geram BIN/CUE:

- **ImgBurn** (Windows): modo *Create image file from disc*. Em
  *Tools → Settings → Read*, mantenha o formato de saída **BIN**.
- **redumper** ou **DiscImageCreator**: ferramentas de linha de comando
  usadas pelo Redump. Geram o dump mais fiel e permitem comparar com o banco
  do redump.org. Se você quiser, eu te guio passo a passo.

## 3. Onde colocar

Crie a pasta `iso/` na raiz do projeto (ela já é ignorada pelo Git) e coloque
o `.cue` e **todos** os `.bin` que ele cita:

```text
Tobal2Recomp/
└── iso/
    ├── Tobal 2 (Japan) (v1.1).cue
    └── Tobal 2 (Japan) (v1.1).bin        (ou Track 01, Track 02, ...)
```

## 4. Conferir

Depois do dump, me peça para verificar. Vou calcular os hashes, ler o serial
no `SYSTEM.CNF` e conferir a revisão (v1.0 ou v1.1).

> Nunca publique o conteúdo de `iso/`. É material com direitos autorais.

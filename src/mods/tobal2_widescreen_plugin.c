/*
 * Tobal 2 — widescreen (mod "tobal2.enhancement.widescreen").
 *
 * Usa o caminho "squash" do PSXRecomp: a projeção do GTE é comprimida no eixo
 * X e a imagem é esticada na apresentação, o que revela mais cenário dos dois
 * lados. Os cortes de tela que os renderizadores do jogo fazem (compare com
 * 512 / 0x200) são alargados pelo recompilador via [widescreen.cull] no
 * game.toml, e não fazem nada em 4:3.
 *
 * As callbacks de ativação só escolhem o aspecto; com o mod desligado o jogo
 * fica idêntico ao original.
 */
#include "mod_plugins.h"

static void tobal2_widescreen_16_9_activate(void) {
    (void)psx_mod_set_fixed_display_aspect(16u, 9u);
}

static void tobal2_widescreen_adaptive_activate(void) {
    /* Começa em 16:9 e depois segue o tamanho da janela, até 32:9. */
    (void)psx_mod_set_fixed_display_aspect(16u, 9u);
    (void)psx_mod_set_adaptive_display_aspect(32u, 9u);
}

PSX_MOD_CONSTRUCTOR(tobal2_register_widescreen_plugins) {
    (void)psx_mod_register_activation_plugin(
        "tobal2.widescreen.16-9", tobal2_widescreen_16_9_activate);
    (void)psx_mod_register_activation_plugin(
        "tobal2.widescreen.adaptive", tobal2_widescreen_adaptive_activate);
}

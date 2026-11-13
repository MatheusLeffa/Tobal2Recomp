/* Title config for psxrecomp/host/psxrecomp_codegen_host.
 * Wired only when the build opts into -DPSX_SETUP_WIZARD=ON. */

#include "codegen_setup.h"

#include "psxrecomp_codegen_host.h"

static const PsxrecompCodegenHostConfig kCodegenConfig = {
    .display_name = "Tobal 2",
    .project_root_env = "TOBAL2RECOMP_PROJECT_ROOT",
    .build_dir_env = "TOBAL2RECOMP_BUILD_DIR",
    .force_setup_env = "TOBAL2RECOMP_FORCE_SETUP",
    .psxrecomp_cli_relpath = "psxrecomp/psxrecomp_cli.py",
    .seed_cfg_relpath = "game.toml",
    .game_toml_relpath = "game.toml",
    .gen_marker_relpath = "generated/SLPM_860.33_dispatch.c",
    .build_dir_name = "build-release",
    .cmake_target = "psx-runtime",
    /* Must match the OUTPUT_NAME runtime.cmake derives from WINDOW_TITLE
     * ("Tobal 2 Recompiled" -> Tobal_2_Recompiled); the setup host forwards
     * to build-release/<exe_basename> once the game is built. */
    .exe_basename = "Tobal_2_Recompiled",
    .prepare_note =
        "Builds Tobal 2 from your own disc, right on this computer: first "
        "it converts the game code, then it compiles it (about 3 to 5 "
        "minutes the first time). Nothing from your disc leaves this PC. "
        "When it finishes, the game opens here.",
    .prepare_note_windows =
        "Builds Tobal 2 from your own disc, right on this computer: first "
        "it converts the game code, then it compiles it (about 3 to 5 "
        "minutes the first time). Nothing from your disc leaves this PC. "
        "When it finishes, the game opens here.",
    .prepare_note_no_cmake =
        "Uses your legal disc with the local psxrecomp SDK to generate "
        "BIOS + game C. Rebuild into build-release/, then relaunch this "
        "setup exe (it forwards to the product build).",
};

void psx_game_codegen_setup_apply(RecompLauncherCGameInfo* gi) {
    psxrecomp_codegen_host_apply(gi, &kCodegenConfig);
}

void psx_game_codegen_relaunch_or_exit(const char* disc_path) {
    psxrecomp_codegen_host_relaunch_or_exit(disc_path);
}

void psx_game_codegen_forward_if_built(int argc, char** argv) {
    psxrecomp_codegen_host_forward_if_built(&kCodegenConfig, argc, argv);
}


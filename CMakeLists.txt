cmake_minimum_required(VERSION 3.20)
set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp" CACHE PATH
    "Path to psxrecomp")
if(NOT EXISTS "${PSXRECOMP_ROOT}/runtime/runtime.cmake")
    message(FATAL_ERROR
        "PSXRecomp runtime is missing: ${PSXRECOMP_ROOT}/runtime/runtime.cmake\n"
        "This project expects the psxrecomp framework checkout at ${PSXRECOMP_ROOT}.\n"
        "Run: git submodule update --init --recursive\n"
        "If psxrecomp/ is not a submodule, set -DPSXRECOMP_ROOT=<path-to-psxrecomp>.")
endif()

project(Tobal2Recomp LANGUAGES C CXX)

# --- Opt-in product surfaces (OFF by default in the framework) -------------
# Scaffold prompts / flags fill these. Without recomp-ui, PSX_RECOMP_UI is OFF.
# The wizard (WIZARD_CMAKE_BLOCK / ENABLE_SETUP_WIZARD) is the first-run disc
# picker; releases are compiled from the committed generated/ C, so it never
# needs to generate or rebuild anything on a player's machine.
# recomp-ui submodule present (PSX_RECOMP_UI defaults ON).
# Online play is not supported yet. Explicit OFF (the framework default) also
# tells the Retro Catalog submission autofill not to list the title as netplay:
# the [netplay] section in game.toml is only the disc-identity gate.
set(PSX_NETPLAY OFF CACHE BOOL "Tobal 2: no online play yet" FORCE)
set(PSX_SETUP_WIZARD ON CACHE BOOL
    "Advertise first-run setup wizard + Generate & rebuild in recomp-ui" FORCE)
include("${PSXRECOMP_ROOT}/runtime/runtime.cmake")

# This project's own mod catalog. The FRAMEWORK stages it -- together with its
# builtin psx.* packages -- into <exe-dir>/mods/bundled, and refuses to
# configure if a catalog exists here but is not declared. Shared Internal
# Resolution is included even with a builtin allowlist, enabled at 4x on fresh
# profiles, with 1x..32x choices; do not supply a title-local copy of that id.
# Never copy the catalog by hand: five titles did, and framework 4cc04be3's rename of the staged
# directory broke all five silently (bead beads-eio.3.101).
set(PSX_PRELOADED_MODS "${CMAKE_CURRENT_SOURCE_DIR}/mods/preloaded")
if(NOT IS_DIRECTORY "${PSX_PRELOADED_MODS}")
    set(PSX_PRELOADED_MODS "NONE")
endif()

psxrecomp_add_game_runtime(psx-runtime
    PRELOADED_MODS_DIR "${PSX_PRELOADED_MODS}"
    ENABLE_SETUP_WIZARD
    WINDOW_TITLE "Tobal 2 Recompiled"
    DEFAULT_GAME_CONFIG_PATH "game.toml"
    MAX_PLAYERS 2
    APP_ICON "${CMAKE_CURRENT_SOURCE_DIR}/assets/psxrecomp.ico"
    # Committed game C (psxrecomp_cli.py generate; git add generated). Release
    # CI configures with -DPSXRECOMP_REQUIRE_GAME_C=ON so a checkout without
    # it fails instead of building a setup host.
    GEN_MARKER "generated/SLPM_860.33_dispatch.c"
    GEN_FULL_GLOB "generated/SLPM_860.33_full_*.c"
    CODEGEN_SETUP_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/codegen_setup.c"
)

# Title plugins (trusted C mods selected by mods/preloaded manifests). They only
# use the mod API, so they build in the setup host too.
target_sources(psx-runtime PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/src/mods/unlock_characters.c")
if(WIN32)
    target_link_libraries(psx-runtime PRIVATE user32)
endif()

# Launcher cover art. No artwork ships with this project (it belongs to Square
# Enix): when the player's own build has no cover yet, it is downloaded once,
# on the player's computer, from the libretro-thumbnails archive (the same
# source RetroArch uses) into <exe dir>/artwork/SLPM-86033/, where the
# launcher looks for it. Any image already in that folder (the player's own
# cover) is kept and nothing is downloaded. Never in CI or in the setup kit.
# Opt out with -DTOBAL2_NO_COVER_DOWNLOAD=ON. A failed download is ignored.
set(TOBAL2_COVER_URL
    "https://thumbnails.libretro.com/Sony%20-%20PlayStation/Named_Boxarts/Tobal%202%20(Japan,%20Asia).png"
    CACHE STRING "Where the launcher cover is downloaded from")
option(TOBAL2_NO_COVER_DOWNLOAD "Do not download the launcher cover art" OFF)
if(NOT TOBAL2_NO_COVER_DOWNLOAD AND NOT PSXRECOMP_FORCE_SETUP_HOST
   AND NOT DEFINED ENV{CI})
    set(_tobal2_cover_dir "${CMAKE_BINARY_DIR}/artwork/SLPM-86033")
    file(GLOB _tobal2_covers "${_tobal2_cover_dir}/*.png" "${_tobal2_cover_dir}/*.jpg"
                             "${_tobal2_cover_dir}/*.jpeg" "${_tobal2_cover_dir}/*.webp")
    if(NOT _tobal2_covers)
        file(DOWNLOAD "${TOBAL2_COVER_URL}" "${_tobal2_cover_dir}/front.png.part"
             TIMEOUT 20 STATUS _tobal2_cover_status)
        list(GET _tobal2_cover_status 0 _tobal2_cover_code)
        if(_tobal2_cover_code EQUAL 0)
            file(RENAME "${_tobal2_cover_dir}/front.png.part" "${_tobal2_cover_dir}/front.png")
            message(STATUS "Tobal 2: launcher cover downloaded to ${_tobal2_cover_dir}")
        else()
            file(REMOVE "${_tobal2_cover_dir}/front.png.part")
            message(STATUS "Tobal 2: launcher cover not downloaded (${_tobal2_cover_status}); "
                           "the launcher shows a placeholder")
        endif()
    endif()
endif()

# Stage runtime configs next to the exe for direct build/ launches. Only copy
# files that exist — never fail POST_BUILD when game_options.toml is absent.
foreach(_PSX_RUNTIME_CONFIG game.toml game_options.toml)
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${_PSX_RUNTIME_CONFIG}")
        add_custom_command(TARGET psx-runtime POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${CMAKE_CURRENT_SOURCE_DIR}/${_PSX_RUNTIME_CONFIG}"
                "$<TARGET_FILE_DIR:psx-runtime>/${_PSX_RUNTIME_CONFIG}"
            COMMENT "Staging ${_PSX_RUNTIME_CONFIG}"
            VERBATIM)
    endif()
endforeach()

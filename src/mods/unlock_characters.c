/*
 * Tobal 2: "Characters" setting (package tobal2.unlock, feature all_characters).
 *
 * The character select screen (function at 0x80019680 in SLPM_860.33) builds a
 * bitmask with one bit per selectable fighter (ids 0..20):
 *
 *   base  = 0x0403FF  (0-9: the starting ten; 18: load a Quest fighter)
 *           0x1C03FF  (a hidden condition also adds 19 and 20, memory-card
 *                      monsters)
 *   final = base | (saved progress byte at 0x801012D0) << 10   (10-17)
 *               | 0x20000 when a Quest fighter is loaded         (17)
 *
 * "All unlocked" turns the base into 0x1DFFFF in every path (0-16 and 18-20;
 * 17 keeps its Quest rule). That is five instruction words. They are written
 * from the VBlank callback, so the choice can change while the game runs: the
 * mask is rebuilt each time the select screen opens. Every word is checked to
 * hold either its original or its unlocked value before anything is written,
 * so other code or data at those addresses is never touched.
 *
 * On Windows the game window gets a menu bar, Options > Unlock all characters,
 * that switches the option, saves it to mods/state.toml and applies it at
 * once. The bar is hidden in fullscreen.
 */
#include "mod_plugins.h"

#include <stdint.h>
#include <string.h>

#define PKG "tobal2.unlock"
#define FEATURE "all_characters"
#define OPTION "unlock"
#define PLUGIN_ID "tobal2.unlock-characters"

static const struct {
    uint32_t address;
    uint32_t original;
    uint32_t unlocked;
} k_sites[] = {
    {0x800196CCu, 0x3C140004u, 0x3C14001Du}, /* lui $s4, 0x0004 -> 0x001D */
    {0x800196DCu, 0x3C140004u, 0x3C14001Du}, /* lui $s4, 0x0004 -> 0x001D */
    {0x800196E4u, 0x3C14001Cu, 0x3C14001Du}, /* lui $s4, 0x001C -> 0x001D */
    {0x800196F4u, 0x369403FFu, 0x3694FFFFu}, /* ori $s4, $s4, 0x03FF -> 0xFFFF */
    {0x800196F8u, 0x369403FFu, 0x3694FFFFu}, /* ori $s4, $s4, 0x03FF -> 0xFFFF */
};
#define SITE_COUNT (sizeof k_sites / sizeof k_sites[0])

static volatile int g_want_unlocked;

static int option_is_on(const char* value) {
    return value && strcmp(value, "on") == 0;
}

static void read_option(void) {
    char value[16] = {0};
    if (psx_mod_option_value(PKG, FEATURE, OPTION, value, sizeof value))
        g_want_unlocked = option_is_on(value);
    else
        g_want_unlocked = 0;
}

/* Bring the five words to the wanted state. Does nothing until the executable
 * is in RAM (and if anything else ever occupies those addresses). */
static void apply_words(void) {
    const int unlocked = g_want_unlocked;
    uint32_t current[SITE_COUNT];
    for (unsigned i = 0; i < SITE_COUNT; ++i) {
        current[i] = psx_mod_read_word(k_sites[i].address);
        if (current[i] != k_sites[i].original && current[i] != k_sites[i].unlocked)
            return;
    }
    for (unsigned i = 0; i < SITE_COUNT; ++i) {
        const uint32_t want = unlocked ? k_sites[i].unlocked : k_sites[i].original;
        if (current[i] != want)
            psx_mod_write_code_word(k_sites[i].address, want);
    }
}

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#define MENU_UNLOCK_ID 0x7A01u
#define MSG_SYNC_MENU (WM_APP + 0x7A0)
#define WINDOW_TITLE L"Tobal 2 Recompiled"

static HWND g_window;
static WNDPROC g_previous_proc;
static HMENU g_menu_bar;
static unsigned g_vblanks_until_check;

static void toggle_unlock(void) {
    const char* value = g_want_unlocked ? "off" : "on";
    if (!psx_mod_feature_set_option(PKG, FEATURE, OPTION, value)) return;
    if (psx_mod_set_option_live(PKG, FEATURE, OPTION, value) < 0) {
        /* Refused (netplay): keep the running game as it is. */
        (void)psx_mod_feature_set_option(PKG, FEATURE, OPTION,
                                         g_want_unlocked ? "on" : "off");
        return;
    }
    (void)psx_mod_save_selection();
}

/* Window thread only. The bar is shown while the window has a title bar and
 * hidden in fullscreen (no caption), where it would cover the game. Adding it
 * grows the window by the bar's height, so the game area keeps its size. */
static void sync_menu_bar(HWND window) {
    if (!g_menu_bar) {
        HMENU options = CreatePopupMenu();
        g_menu_bar = CreateMenu();
        if (!options || !g_menu_bar) return;
        AppendMenuW(options, MF_STRING, MENU_UNLOCK_ID, L"Unlock all characters");
        AppendMenuW(g_menu_bar, MF_POPUP, (UINT_PTR)options, L"Options");
    }
    CheckMenuItem(g_menu_bar, MENU_UNLOCK_ID,
                  MF_BYCOMMAND | (g_want_unlocked ? MF_CHECKED : MF_UNCHECKED));
    const LONG style = GetWindowLongW(window, GWL_STYLE);
    const int windowed = (style & WS_CAPTION) == WS_CAPTION;
    const int attached = GetMenu(window) == g_menu_bar;
    if (windowed == attached) return;
    RECT before, after;
    GetClientRect(window, &before);
    SetMenu(window, windowed ? g_menu_bar : NULL);
    if (windowed && !IsZoomed(window)) {
        GetClientRect(window, &after);
        const int grow = (before.bottom - before.top) - (after.bottom - after.top);
        RECT outer;
        if (grow > 0 && GetWindowRect(window, &outer))
            SetWindowPos(window, NULL, 0, 0, outer.right - outer.left,
                         outer.bottom - outer.top + grow,
                         SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE);
    }
}

static LRESULT CALLBACK game_window_proc(HWND window, UINT message, WPARAM wparam,
                                         LPARAM lparam) {
    switch (message) {
    case MSG_SYNC_MENU:
        sync_menu_bar(window);
        return 0;
    case WM_INITMENUPOPUP:
        if (g_menu_bar)
            CheckMenuItem(g_menu_bar, MENU_UNLOCK_ID,
                          MF_BYCOMMAND | (g_want_unlocked ? MF_CHECKED : MF_UNCHECKED));
        break;
    case WM_COMMAND:
        if (HIWORD(wparam) == 0 && LOWORD(wparam) == MENU_UNLOCK_ID) {
            toggle_unlock();
            sync_menu_bar(window);
            return 0;
        }
        break;
    case WM_STYLECHANGED:
        /* Fullscreen on/off changes the caption: show or hide the bar after
         * the change settles. */
        PostMessageW(window, MSG_SYNC_MENU, 0, 0);
        break;
    default:
        break;
    }
    return CallWindowProcW(g_previous_proc, window, message, wparam, lparam);
}

typedef struct {
    DWORD pid;
    HWND found;
} FindWindowArgs;

static BOOL CALLBACK find_game_window(HWND window, LPARAM lparam) {
    FindWindowArgs* args = (FindWindowArgs*)lparam;
    DWORD pid = 0;
    wchar_t title[64];
    GetWindowThreadProcessId(window, &pid);
    if (pid != args->pid || !IsWindowVisible(window)) return TRUE;
    if (GetWindowTextW(window, title, 64) <= 0 || wcscmp(title, WINDOW_TITLE) != 0)
        return TRUE;
    args->found = window;
    return FALSE;
}

/* Find the game window and hook it; again if the window is ever recreated.
 * Checked about twice a second, never on every frame. The menu itself is
 * built and attached on the window's own thread (MSG_SYNC_MENU). */
static void ensure_title_menu(void) {
    if (g_vblanks_until_check) {
        --g_vblanks_until_check;
        return;
    }
    g_vblanks_until_check = 30;
    if (g_window && IsWindow(g_window) &&
        (WNDPROC)GetWindowLongPtrW(g_window, GWLP_WNDPROC) == game_window_proc)
        return;
    FindWindowArgs args = {GetCurrentProcessId(), NULL};
    EnumWindows(find_game_window, (LPARAM)&args);
    if (!args.found) return;
    WNDPROC previous = (WNDPROC)SetWindowLongPtrW(args.found, GWLP_WNDPROC,
                                                  (LONG_PTR)game_window_proc);
    if (!previous) return;
    if (previous != game_window_proc) g_previous_proc = previous;
    if (g_window != args.found) g_menu_bar = NULL; /* destroyed with the old window */
    g_window = args.found;
    PostMessageW(g_window, MSG_SYNC_MENU, 0, 0);
}
#else
static void ensure_title_menu(void) {}
#endif

static void unlock_activate(void) {
    read_option();
}

static void unlock_vblank(void) {
    apply_words();
    ensure_title_menu();
}

static int unlock_option_changed(const char* option_id, const char* value) {
    if (!option_id || strcmp(option_id, OPTION) != 0) return 0;
    g_want_unlocked = option_is_on(value);
    return 1; /* applied at the next VBlank; the select screen rereads it */
}

PSX_MOD_CONSTRUCTOR(tobal2_register_unlock_characters_plugin) {
    (void)psx_mod_register_activation_plugin(PLUGIN_ID, unlock_activate);
    (void)psx_mod_register_vblank_plugin(PLUGIN_ID, unlock_vblank);
    (void)psx_mod_register_option_changed_plugin(PLUGIN_ID, unlock_option_changed);
}

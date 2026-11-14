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
 * "All unlocked" turns the base into 0x1DFFFF in every path (0-16 and 18-20).
 *
 * Fighter 17 is the Quest monster list. The save keeps 2 bits per monster in
 * 12 words at 0x8010129C (monster n = character id n + 16; 184 monsters, DOG
 * to LOADER; 3 = usable, which is what the Quest writes when one joins you).
 * The function at 0x800195E8 turns those bits into the list the select screen
 * scrolls through (a count byte, then (n << 8) | bits per entry), and 17 is
 * offered when the list is not empty. "All unlocked" makes that function see
 * every monster 0..183 as 3 without reading the save, so the RAM copy of the
 * save and the memory card stay as they were. Choosing a monster normally
 * also marks it (bit 0) in the save (call at 0x8001A2B8); with "All unlocked"
 * that call ORs 0 instead, so picking a locked monster does not leak into the
 * save either.
 *
 * Eleven instruction words in all, in the main executable. They are written
 * from the VBlank callback, so the choice can change while the game runs: the
 * mask and the list are rebuilt each time the select screen opens. Every word
 * is checked to hold either its original or its unlocked value before
 * anything is written, so other code or data at those addresses is never
 * touched.
 *
 * On Windows the game window's title-bar menu (the icon at the top left, or a
 * right click on the bar) gets an "Unlock all characters" item that switches
 * the option, saves it to mods/state.toml and applies it at once.
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
    /* Quest monster list (0x800195E8); branches stay where they were. The
     * entry index is $t0, the list count $a3, the bits $a1. */
    {0x80019610u, 0x00CB1006u, 0x2D0200B8u}, /* srlv $v0,$t3,$a2 -> sltiu $v0,$t0,184 */
    {0x80019614u, 0x30450003u, 0x00022823u}, /* andi $a1,$v0,3  -> subu $a1,$zero,$v0 */
    {0x8001961Cu, 0x00E01821u, 0x30A50003u}, /* move $v1,$a3     -> andi $a1,$a1,3 */
    {0x80019620u, 0x24E70001u, 0x30E300FFu}, /* addiu $a3,$a3,1  -> andi $v1,$a3,0xFF */
    {0x80019624u, 0x306300FFu, 0x24E70001u}, /* andi $v1,$v1,0xFF -> addiu $a3,$a3,1 */
    /* Chosen monster: mark-as-used call gets 0 instead of 1 (delay slot). */
    {0x8001A2BCu, 0x34050001u, 0x34050000u}, /* ori $a1,$zero,1 -> ori $a1,$zero,0 */
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

/* Bring the words to the wanted state. Does nothing until the executable
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

#define TITLE_MENU_ID 0x0110u /* WM_SYSCOMMAND ids: below 0xF000, low 4 bits 0 */
#define WINDOW_TITLE L"Tobal 2 Recompiled"

static HWND g_window;
static WNDPROC g_previous_proc;
static unsigned g_vblanks_until_check;

static void sync_menu_check(HWND window) {
    HMENU menu = GetSystemMenu(window, FALSE);
    if (menu)
        CheckMenuItem(menu, TITLE_MENU_ID,
                      MF_BYCOMMAND | (g_want_unlocked ? MF_CHECKED : MF_UNCHECKED));
}

static LRESULT CALLBACK title_menu_proc(HWND window, UINT message, WPARAM wparam,
                                        LPARAM lparam) {
    if (message == WM_INITMENUPOPUP && HIWORD(lparam)) {
        sync_menu_check(window);
    } else if (message == WM_SYSCOMMAND && (wparam & 0xFFF0u) == TITLE_MENU_ID) {
        const char* value = g_want_unlocked ? "off" : "on";
        if (psx_mod_feature_set_option(PKG, FEATURE, OPTION, value)) {
            if (psx_mod_set_option_live(PKG, FEATURE, OPTION, value) < 0) {
                /* Refused (netplay): keep the running game as it is. */
                (void)psx_mod_feature_set_option(PKG, FEATURE, OPTION,
                                                 g_want_unlocked ? "on" : "off");
            } else {
                (void)psx_mod_save_selection();
            }
        }
        sync_menu_check(window);
        return 0;
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

/* Find the game window and add the menu item; again if the window is ever
 * recreated. Checked about twice a second, never on every frame. */
static void ensure_title_menu(void) {
    if (g_vblanks_until_check) {
        --g_vblanks_until_check;
        return;
    }
    g_vblanks_until_check = 30;
    if (g_window && IsWindow(g_window) &&
        (WNDPROC)GetWindowLongPtrW(g_window, GWLP_WNDPROC) == title_menu_proc)
        return;
    FindWindowArgs args = {GetCurrentProcessId(), NULL};
    EnumWindows(find_game_window, (LPARAM)&args);
    if (!args.found) return;
    HMENU menu = GetSystemMenu(args.found, FALSE);
    if (!menu) return;
    if (GetMenuState(menu, TITLE_MENU_ID, MF_BYCOMMAND) == (UINT)-1) {
        AppendMenuW(menu, MF_SEPARATOR, 0, NULL);
        AppendMenuW(menu, MF_STRING, TITLE_MENU_ID, L"Unlock all characters");
    }
    WNDPROC previous = (WNDPROC)SetWindowLongPtrW(args.found, GWLP_WNDPROC,
                                                  (LONG_PTR)title_menu_proc);
    if (!previous) return;
    if (previous != title_menu_proc) g_previous_proc = previous;
    g_window = args.found;
    sync_menu_check(g_window);
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

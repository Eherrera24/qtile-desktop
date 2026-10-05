# Dependencies

The audit was performed on Arch Linux with Qtile 0.37.1, Picom 13, Rofi 2.0.0,
Kitty 0.49.2, Feh 3.13.1 and Plank Reloaded 0.11.172.

`packages/pacman.txt` contains the minimal official-package set tied directly
to active config or scripts. `packages/aur.txt` separates the foreign Plank
package and records the user-local `qtile-extras==0.35.0` Python dependency.
`packages/optional.txt` contains helpers for optional UI paths.

Important runtime relationships:

- `qtile-extras` supplies decorated widgets.
- Feh applies workspace backgrounds.
- Pillow powers colour extraction in `walltheme`/`theme.py`.
- iwd/`iwctl` backs `wifi-menu`; BlueZ and optionally Blueman back Bluetooth.
- WirePlumber, Fish and a user-defined Fish `volume` function back volume UI.
- Xorg utilities support monitor counting, touchpad setup and Plank detection.
- Nerd Fonts render bar glyphs. Rofi additionally asks for FiraCode Nerd Font,
  which was referenced but not detected by `fc-list`; install it if glyph/text
  fallback is undesirable.
- Fish uses Fastfetch, LSD and user-local `terminaltexteffects==0.15.0` for its
  customised prompt/greeting. Btop and Cava have versioned visual configs;
  Htop and Ranger are included as optional showcase tools.

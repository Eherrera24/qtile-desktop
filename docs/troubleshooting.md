# Troubleshooting

- Missing bar glyphs: verify UbuntuMono Nerd Font and Hack Nerd Font with
  `fc-match`; Rofi additionally references FiraCode Nerd Font.
- Empty update widget: `checkupdates` comes from `pacman-contrib`.
- Wi-Fi menu fails: the script is intentionally bound to `wlan0` and iwd;
  adjust the copied script if the target interface/backend differs.
- Volume does not change: this desktop relies on a Fish function named
  `volume`, which is outside this repository. Replace commands or recreate it.
- No wallpaper: supply licensed files under
  `~/.config/qtile/workspace-wallpapers/` with the documented names.
- Plank margin detection fails: `plank_api.py` matches a 1920×140 Plank window;
  this is display-specific.
- LightDM differs: its background is a system file and is not installed here.
- Validate Qtile safely before restart with `qtile check -c ~/.config/qtile/config.py`.

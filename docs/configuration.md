# Configuration inventory

Copied active files only:

- Qtile entry point, active modular settings, palettes and theme generator.
- Picom active configuration and animation-profile state.
- Rofi config plus the exact external squared Nord theme it imports.
- Kitty and GTK 3 settings.
- MacWidgets code and current non-secret geometry/preferences.
- Plank dconf snapshot (launcher definitions themselves are excluded).
- LightDM WebKit greeter configuration, without the wallpaper asset.
- Fish prompt/volume function, Fastfetch, Btop and Cava visual settings.

Not copied: backups, experimental Wayland configs, test modules, Python caches,
browser profiles, application histories, full icon/theme trees, launcher files
that embed local web-app profile paths, and wallpapers of unknown provenance.
Htop and Ranger have no user configuration files on the audited machine, so
their screenshots intentionally use upstream defaults inside themed Kitty.

Several source files contain `/home/esteban` because that is the audited source
of truth. The installer replaces that exact prefix with the target `$HOME` in
the staged copy before installation; the repository remains an honest snapshot.

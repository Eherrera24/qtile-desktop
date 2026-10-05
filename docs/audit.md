# Audit record

Audit date: 2026-10-05 (America/Guatemala).

## Platform

- Arch Linux rolling, kernel `7.2.8-arch1-2`, x86_64.
- X11 session (`DISPLAY=:0`, `DESKTOP_SESSION=qtile`).
- One 1920×1200 display was observed during screenshot production.
- Nine EWMH desktops: ` I ` through ` IX `.

## Active software observed

Qtile 0.37.1, Picom 13, Rofi 2.0.0, Kitty 0.49.2, Feh 3.13.1,
Plank Reloaded 0.11.172, Scrot 2.0.0 and Fastfetch 2.69.0 were installed.
The active Qtile configuration also starts cbatticon, volumeicon, Picom, Plank
and MacWidgets. Dunst/libnotify were installed; no user Dunst configuration was
found.

## Appearance inventory

- GTK 3 requests dark-theme preference; GTK 4 had no user settings file.
- No user theme collection was present under `~/.local/share/themes`.
- The local icon tree mainly contained app-specific/hicolor items and was not
  copied wholesale.
- Detected required fonts: UbuntuMono Nerd Font and Hack Nerd Font. Rofi's
  configured FiraCode Nerd Font was not returned by `fc-list`.
- LightDM uses `lightdm-webkit2-greeter` with the `glorious` theme. Its system
  wallpaper is updated by `walltheme` only for workspace I.
- No active Qtile Systray widget exists; tray utilities still start at login.

## Security review

Candidate source files were scanned for password, token, API-key,
authorization, bearer, private-key and cookie markers before copying. No
credential-bearing match was found. A second scan of the final repository found
only documentation language describing the scan. No email or RFC1918/private
IPv4 literal was found.

The audit intentionally excluded SSH material, browser profiles, histories,
caches, backups, web-app launcher commands, full home/config trees and images
without verified redistribution rights.

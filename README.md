# My Qtile Desktop

A workspace-aware Arch Linux desktop powered by Qtile, X11 and a coordinated
wallpaper-to-palette system.

![Desktop overview](assets/screenshots/desktop.png)

## Overview

This repository is a sanitized snapshot of a real Arch Linux session audited on
2026-10-05. Qtile manages nine X11 workspaces; Feh changes their wallpapers and
a Python hook recolours the Qtile bar and borders from stored per-workspace
palettes. Picom supplies blur, shadows, rounded corners and animations. Rofi,
Kitty and Plank complete the main interaction layer, while custom GTK
MacWidgets appear on empty workspaces.

## Screenshots

| Launcher | Terminal |
|---|---|
| ![Rofi](assets/screenshots/rofi.png) | ![Kitty](assets/screenshots/terminal.png) |

### Workspaces

The groups use identical layouts and controls; wallpaper and palette are the
intentional differences.

| Workspace | Screenshot | Description |
|---|---|---|
| I | [View](assets/screenshots/workspaces/workspace-I.png) | Blue/sand palette |
| II | [View](assets/screenshots/workspaces/workspace-II.png) | Green/orange palette |
| III | [View](assets/screenshots/workspaces/workspace-III.png) | Blue/brown palette |
| IV | [View](assets/screenshots/workspaces/workspace-IV.png) | Violet/pink palette |
| V | [View](assets/screenshots/workspaces/workspace-V.png) | Blue/red palette |
| VI | [View](assets/screenshots/workspaces/workspace-VI.png) | Navy/red palette |
| VII | [View](assets/screenshots/workspaces/workspace-VII.png) | Green palette |
| VIII | [View](assets/screenshots/workspaces/workspace-VIII.png) | Blue/rust palette |
| IX | [View](assets/screenshots/workspaces/workspace-IX.png) | Brown/green palette |

## Features

- Nine Qtile groups with matching wallpaper and live bar palette
- Modular keys, groups, layouts, screens, widgets and hooks
- Decorated Qtile Extras bar with updates, network, Bluetooth, layout, clock,
  volume and battery status
- Feh wallpaper changes and Pillow-based colour extraction
- Picom Dual Kawase blur, shadows, rounded corners and selectable animations
- Rofi app launcher plus custom Wi-Fi and Bluetooth menus
- Transparent Kitty setup and intelligent-hiding Plank dock
- Qtile/Plank focus integration and hover-aware layout margins
- Desktop widgets automatically hidden when a workspace has application windows

## Components

| Component | Software |
|---|---|
| Distribution | Arch Linux |
| Window manager | Qtile 0.37.1 |
| Display server | X11 |
| Compositor | Picom 13 |
| Launcher | Rofi 2.0.0 |
| Terminal | Kitty 0.49.2 |
| Dock | Plank Reloaded 0.11.172 |
| Wallpaper | Feh 3.13.1 |
| Screenshots | Scrot 2.0.0 |
| Notifications | Dunst / libnotify |
| Desktop widgets | Custom GTK 3 MacWidgets |

## Installation

Inspect before applying anything:

```bash
./install/install.sh --dry-run
```

The real mode shows targets, asks once for confirmation and backs up every
existing destination before copying. It does not install packages, touch
LightDM or import Plank settings automatically.

```bash
sed '/^#/d;/^$/d' packages/pacman.txt | sudo pacman -S --needed -
python -m pip install --user 'qtile-extras==0.35.0'
./install/install.sh
```

Read the [installation guide](docs/installation.md) and add licensed wallpaper
files before restarting Qtile.

## Dependencies

Official packages are in [`packages/pacman.txt`](packages/pacman.txt), foreign
packages in [`packages/aur.txt`](packages/aur.txt), and feature-specific helpers
in [`packages/optional.txt`](packages/optional.txt). See the
[dependency notes](docs/dependencies.md) for why each group exists.

## Keybindings

- `Mod+1`…`Mod+9`: switch workspace
- `Mod+Shift+1`…`Mod+Shift+9`: move focused window
- `Mod+Return`: Kitty
- `Mod+d`: Rofi application launcher
- `Mod+j/k/h/l`: move focus
- `Mod+Tab`: next layout
- `Mod+s`: screenshot

The complete extracted list is in [docs/keybindings.md](docs/keybindings.md).

## Project structure

```text
config/     active application configuration snapshots
scripts/    wallpaper, Plank, Qtile and utility scripts
themes/     externally referenced Rofi theme
assets/     sanitized screenshots; wallpaper licensing note
docs/       architecture and operational reference
packages/   official, AUR/user-local and optional dependencies
install/    cautious, backup-first installer
```

## Documentation

- [Architecture](docs/architecture.md)
- [System and security audit](docs/audit.md)
- [Configuration inventory](docs/configuration.md)
- [Workspaces](docs/workspaces.md)
- [Widgets](docs/widgets.md)
- [Scripts](docs/scripts.md)
- [Themes and colours](docs/themes.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Third-party material](docs/third-party.md)

## Notes and licensing

Hardware names (`wlan0`), a Fish `volume` function, 1920×1200 geometry and the
Plank detector's 1920×140 match are machine-specific. Absolute home paths in the
snapshot document the audited machine; the installer ports them in installed
copies.

The MIT license covers original code and configuration in this repository. It
does not claim ownership of third-party themes, fonts, icons or wallpapers.
Original wallpapers are not redistributed because their licensing could not be
verified. The squared Nord Rofi file retains its author attribution.

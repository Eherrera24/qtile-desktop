# Scripts

| Script | Called by | Purpose / side effects |
|---|---|---|
| `walltheme` | Manual | Rofi/Zenity selector; copies a chosen image, extracts palette, atomically updates `workspace-themes.json`, optionally updates LightDM background, then asks Qtile to apply it. |
| `animation-profile` | Manual/profile tool | Selects one of six Picom animation blocks; rewrites `picom.conf`, records state and restarts Picom unless `--no-restart`. |
| `wifi-menu` | Net widget click | Rofi frontend to `iwctl`; scans, connects/disconnects known networks or opens an iwctl Kitty. `--list` is read-only. |
| `bluetooth-menu` | Bluetooth widget click | Rofi frontend to paired BlueZ devices; connects/disconnects or opens Blueman. `--list` is read-only. |
| `desktop-profile` | Manual | Switches stored “premium”/“original” config trees using rsync, then optionally restarts desktop pieces. Not invoked at startup. |
| `plank-qtile` | Adapted `.desktop` launchers | If a matching window exists, changes to its group and focuses it; otherwise executes its launcher. |
| `plank-qtile-sync` | `Mod+Ctrl+r` | Adapts selected Plank `.desktop` launchers to use `plank-qtile`, retaining backups outside this repo. |
| `macwidgets` | Qtile autostart and hooks | Wrapper around the GTK desktop-widget program: start/stop/restart/show/hide/configure/edit. |

Examples:

```bash
animation-profile status
animation-profile suave
wifi-menu --list
bluetooth-menu --list
desktop-profile status
walltheme
```

`walltheme`, `animation-profile`, `desktop-profile` and `plank-qtile-sync` modify
live configuration; read their code before using them on another machine.

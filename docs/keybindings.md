# Keybindings

`Mod` is the Super/Windows key (`mod4`). These entries are extracted from the
active `settings/keys.py` and `settings/groups.py`.

## Windows and layouts

| Keys | Action |
|---|---|
| `Mod+j/k/h/l` | Focus down/up/left/right |
| `Mod+Shift+j/k` | Shuffle window down/up |
| `Mod+Shift+h/l` | Shrink/grow MonadTall |
| `Mod+Shift+f` | Toggle floating |
| `Mod+Tab` / `Mod+Shift+Tab` | Next/previous layout |
| `Mod+w` | Kill focused window |
| `Mod+comma/period` | Previous/next screen |

## Workspaces

For each number 1–9, `Mod+number` opens the matching workspace and
`Mod+Shift+number` sends the focused window there.

## Applications and menus

| Keys | Action |
|---|---|
| `Mod+d` | `rofi -show drun` |
| `Mod+Shift+m` | `rofi -show` |
| `Mod+Return` | Kitty |
| `Mod+b` | Firefox |
| `Mod+e` | PCManFM |
| `Mod+r` | Qtile command prompt |
| `Mod+Ctrl+w` | MacWidgets editor |

## System, screenshots and hardware

| Keys | Action |
|---|---|
| `Mod+s` | Full screenshot to `~/images/screenshots/` with Scrot |
| `Mod+Shift+s` | Interactive Scrot selection |
| `Mod+p` | Lock session with logind |
| `Mod+Ctrl+r` | Sync Plank launchers, then restart Qtile |
| `Mod+Ctrl+q` | Shut down Qtile |
| Volume keys | Fish `volume` function: −1/+1/toggle |
| Brightness keys | Brightnessctl ±1% |

Mouse: `Mod+Button1` moves a floating window, `Mod+Button3` resizes it and
`Mod+Button2` brings it to the front.

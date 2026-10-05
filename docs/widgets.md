# Qtile bar and widgets

The primary bar is 40 px high, opacity 0.92, rounded, with 10 px top/side
margins. Default typography is UbuntuMono Nerd Font Bold, 14 px, padding 5.
Most widgets use an unfilled `RectDecoration` with radius 10; colour roles are
registered so the workspace palette can update them live.

| Widget | Purpose and relevant parameters |
|---|---|
| `Sep` | Zero-width visual separator, padding 5. |
| `GroupBox` | Nine groups; UbuntuMono Nerd Font 24; block highlight; 1 px border; drag disabled. |
| `WindowName` | Focused title, 14 px, padding 5. |
| `TextBox` + powerlines | Nerd Font icons and 46 px colour transitions. |
| `CheckUpdates` | `checkupdates`; refresh 1800 s; displays package count or `0`. |
| `Net` | Interface `wlan0`; click opens `wifi-menu`. |
| Bluetooth `TextBox` | Hack Nerd Font 24; click opens `bluetooth-menu`. |
| `CurrentLayout` | Current layout name, 24 px. |
| `Clock` | `%d/%m/%Y - %H:%M`, 24 px. |
| `Volume` | Refresh 0.1 s; Fish `volume` and `wpctl`; click/scroll actions supplied by the widget commands. |
| `Battery` | Nerd icon plus percentage; 24 px; no short text. |

The secondary-monitor bar keeps GroupBox, WindowName, CurrentLayout and Clock.
`Systray` is present only as commented code and is therefore not active.

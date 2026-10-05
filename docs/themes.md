# Colours, wallpapers and visual effects

## Dynamic workspace pipeline

```text
image selected by walltheme
  → copied to ~/.config/qtile/workspace-wallpapers/<GROUP>.<ext>
  → theme.py extracts a palette with Pillow
  → workspace-themes.json stores wallpaper + semantic colour roles
  → setgroup hook runs Feh and recolours Qtile widgets/borders
```

The roles are `dark`, `grey`, `light`, `text`, `focus`, `active`, `inactive`,
`urgent`, and `color1`–`color5`. Full exact values are kept in
`config/qtile/workspace-themes.json`.

## Static component themes

- Kitty: foreground `#f2f2f2`, background `#101010`, white cursor, opacity
  0.55, UbuntuMono Nerd Font 17, padding 10.
- Rofi: squared Nord theme with `#2E3440`, `#3B4252`, `#D8DEE9`, accent
  `#88C0D0`, urgent `#EBCB8B`, FiraCode Nerd Font Medium 12.
- Picom: GLX, VSync, Dual Kawase blur strength 7, shadows radius 20 at 0.20,
  14 px corners and the active “suave” animation profile.
- GTK 3: prefers a dark application theme. No GTK 4 user settings file was
  present.
- Plank: Transparent theme, bottom centre, 56 px icons, intelligent hiding and
  115% zoom.

## Wallpaper inventory

Original images were excluded pending license verification. Expected names and
SHA-256 prefixes: I `8a8d85d1`, II `df53d2c3`, III `4633b818`, IV `17dd398c`,
V `5c26c2d1`, VI `b34e7f83`, VII `34b47b4`, VIII `447fe73e`, IX `7abc0a48`.

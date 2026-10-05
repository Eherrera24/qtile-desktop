#!/bin/sh

# systray battery icon
cbatticon -u 5 &
# systray volume
volumeicon &
# El wallpaper lo controla settings/workspace_theme.py según el workspace.
pkill picom
picom --config /home/esteban/.config/picom/picom.conf &
pkill plank
plank &
/home/esteban/.local/bin/macwidgets restart &

xinput set-prop 7 "libinput Tapping Enabled" 1

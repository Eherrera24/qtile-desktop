# Qtile Config File
# http://www.qtile.org/

# Antonio Sarosi
# https://youtube.com/c/antoniosarosi
# https://github.com/antoniosarosi/dotfiles


from libqtile import hook, qtile

from settings.keys import mod, keys
from settings.groups import groups
from settings.layouts import layouts, floating_layout
from settings.widgets import widget_defaults, extension_defaults
from settings.screens import screens
from settings.mouse import mouse
from settings.path import qtile_path
from settings.plank_api import start_plank
from settings.workspace_theme import apply_workspace_theme
from settings import widget_visibility  # noqa: F401: registra hooks de visibilidad

from os import path
import subprocess


@hook.subscribe.startup_once
def autostart():
    subprocess.call([path.join(qtile_path, 'autostart.sh')])
    start_plank()


@hook.subscribe.startup_complete
def load_initial_workspace_theme():
    apply_workspace_theme(qtile)
    # Algunos widgets asíncronos (por ejemplo Battery) terminan de configurar
    # su fondo después de startup_complete. Reaplicamos cuando ya están listos.
    qtile.call_later(1.0, apply_workspace_theme, qtile)
    # Segunda comprobación cuando ya terminaron autostart, Picom y monitores.
    qtile.call_later(3.0, apply_workspace_theme, qtile)


@hook.subscribe.setgroup
def load_workspace_theme():
    apply_workspace_theme(qtile)

main = None
dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = True
bring_front_click = False
cursor_warp = True
auto_fullscreen = True
focus_on_window_activation = 'urgent'
wmname = 'LG3D'

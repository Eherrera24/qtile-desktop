# Antonio Sarosi
# https://youtube.com/c/antoniosarosi
# https://github.com/antoniosarosi/dotfiles

# Multimonitor support

from libqtile.config import Screen
from libqtile import bar
from libqtile.log_utils import logger
from .widgets import primary_widgets, secondary_widgets
import subprocess


def status_bar(widgets, bottom_margin=0):
    """Crea una barra con margen inferior configurable"""
    return bar.Bar(
        widgets, 
        40, 
        opacity=0.92, 
        margin=[10, 10, bottom_margin, 10],  # bottom_margin ahora es dinámico
        border_color='#000000', 
        rounded=True
    )


def create_screens(bottom_margin=0):
    """Crea las pantallas con el margen inferior especificado"""
    screens = [Screen(top=status_bar(primary_widgets, bottom_margin))]
    
    xrandr = "xrandr | grep -w 'connected' | cut -d ' ' -f 2 | wc -l"
    command = subprocess.run(
        xrandr,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if command.returncode != 0:
        error = command.stderr.decode("UTF-8")
        logger.error(f"Failed counting monitors using {xrandr}:\n{error}")
        connected_monitors = 1
    else:
        connected_monitors = int(command.stdout.decode("UTF-8"))

    if connected_monitors > 1:
        for _ in range(1, connected_monitors):
            screens.append(Screen(top=status_bar(secondary_widgets, bottom_margin)))
    
    return screens


# Crea las pantallas iniciales (sin margen inferior)
screens = create_screens(0)

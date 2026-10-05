#!/usr/bin/env python3

from libqtile import hook
from libqtile.core.manager import Qtile

import subprocess
import threading
import re
import threading


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

NORMAL_MARGIN = 10
PLANK_MARGIN = 70

qtile = None
margin_state = NORMAL_MARGIN


# ==========================================================
# BUSCAR VENTANA PRINCIPAL DE PLANK
# ==========================================================

def find_plank():

    output = subprocess.check_output(
        ["xwininfo", "-root", "-tree"],
        text=True
    )

    for line in output.splitlines():

        if '"plank"' in line and "1920x140" in line:

            return re.search(r"0x[0-9a-fA-F]+", line).group(0)

    return None


# ==========================================================
# CAMBIAR MÁRGENES
# ==========================================================

def set_margin(value):

    global margin_state

    if margin_state == value:
        return

    margin_state = value

    print("QTILE:", qtile)

    for group in qtile.groups_map.values():

        print(group.name, group.layout.margin)
        try:

            layout = group.layout

            if hasattr(layout, "margin"):

                layout.margin = value
                group.layout_all()

        except Exception as e:

            print("Plank:", e)


# ==========================================================
# DETECTOR
# ==========================================================

def detector():

    window = find_plank()

    if window is None:
        print("Plank no encontrado")
        return

    print("Plank:", window)

    proc = subprocess.Popen(
        [
            "xev",
            "-id",
            window,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )

    while True:

        line = proc.stdout.readline()

        if not line:
            break

        if "EnterNotify" in line:

            set_margin(PLANK_MARGIN)

        elif "LeaveNotify" in line:

            set_margin(NORMAL_MARGIN)


# ==========================================================
# QTILE
# ==========================================================

def start_plank():
    print(">>> INICIANDO PLANK DETECTOR")

    threading.Thread(
        target=detector,
        daemon=True
    ).start()

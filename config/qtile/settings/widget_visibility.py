"""Oculta los widgets de escritorio cuando el grupo actual tiene ventanas."""

import subprocess
from pathlib import Path

from libqtile import hook, qtile


COMMAND = str(Path.home() / ".local" / "bin" / "macwidgets")


def _refresh():
    group = qtile.current_group
    windows = [] if group is None else group.windows

    def is_application(window):
        try:
            classes = window.get_wm_class() or ()
        except AttributeError:
            classes = ()
        return not any("macwidgets" in item.lower() for item in classes)

    has_windows = any(is_application(window) for window in windows)
    subprocess.Popen(
        [COMMAND, "hide" if has_windows else "show"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def refresh(*_args):
    qtile.call_later(0.1, _refresh)


hook.subscribe.client_managed(refresh)
hook.subscribe.client_killed(refresh)
hook.subscribe.setgroup(refresh)
hook.subscribe.startup_complete(refresh)

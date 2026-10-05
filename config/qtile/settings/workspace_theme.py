"""Temas de fondo y barra asociados a cada grupo de Qtile."""

import json
import subprocess
from pathlib import Path

from libqtile.log_utils import logger

from .path import qtile_path
from .theme import colors as default_colors


THEMES_FILE = Path(qtile_path) / "workspace-themes.json"
_active_palette = dict(default_colors)


def _load_themes():
    try:
        with THEMES_FILE.open(encoding="utf-8") as stream:
            data = json.load(stream)
        return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError) as error:
        logger.error("No se pudo leer %s: %s", THEMES_FILE, error)
        return {}


def _replace_palette_value(value, old_palette, new_palette):
    for role, old_value in old_palette.items():
        new_value = new_palette.get(role)
        if new_value is None:
            continue
        if value == old_value:
            return new_value
        if isinstance(old_value, list) and old_value and value == old_value[0]:
            return new_value[0] if isinstance(new_value, list) else new_value
    return value


def _recolor_bar(qtile, palette):
    global _active_palette

    attributes = (
        "background", "foreground", "active", "inactive", "urgent_border",
        "this_current_screen_border", "this_screen_border",
        "other_current_screen_border", "other_screen_border",
        "colour_have_updates", "colour_no_updates",
    )
    for screen in qtile.screens:
        for position in ("top", "bottom", "left", "right"):
            current_bar = getattr(screen, position, None)
            if current_bar is None:
                continue
            for current_widget in current_bar.widgets:
                changed = False
                color_roles = getattr(current_widget, "workspace_color_roles", {})
                for attribute, role in color_roles.items():
                    if role not in palette or not hasattr(current_widget, attribute):
                        continue
                    new_value = palette[role]
                    if getattr(current_widget, attribute) != new_value:
                        setattr(current_widget, attribute, new_value)
                        changed = True
                for attribute in attributes:
                    if attribute in color_roles:
                        continue
                    if hasattr(current_widget, attribute):
                        old_value = getattr(current_widget, attribute)
                        new_value = _replace_palette_value(
                            old_value, _active_palette, palette
                        )
                        if new_value != old_value:
                            setattr(current_widget, attribute, new_value)
                            changed = True
                # Battery restaura normal_background en cada sondeo. Si no se
                # sincroniza esta caché, reaparece el color del tema anterior.
                if current_widget.name == "battery" and hasattr(current_widget, "normal_background"):
                    old_normal = current_widget.normal_background
                    current_widget.normal_background = current_widget.background
                    if getattr(current_widget, "low_background", None) == old_normal:
                        current_widget.low_background = current_widget.background
                    if getattr(current_widget, "charging_background", None) == old_normal:
                        current_widget.charging_background = current_widget.background
                if changed and getattr(current_widget, "layout", None):
                    # _TextBox conserva el color visible en layout.colour.
                    # CheckUpdates usa dos colores propios y sólo los refresca
                    # cuando vuelve a consultar paquetes (cada 30 minutos).
                    if hasattr(current_widget, "colour_have_updates"):
                        no_updates = getattr(current_widget, "no_update_string", "")
                        colour = (
                            current_widget.colour_no_updates
                            if str(getattr(current_widget, "text", "")) == str(no_updates)
                            else current_widget.colour_have_updates
                        )
                    else:
                        colour = getattr(current_widget, "foreground", None)
                    if colour is not None:
                        current_widget.layout.colour = colour
                if changed and getattr(current_widget, "drawer", None):
                    current_widget.drawer.clear(current_widget.background)
                    # bar.draw() no reconstruye siempre las superficies en caché.
                    # Los widgets sin temporizador necesitan un draw explícito.
                    current_widget.draw()
            current_bar.draw()
    _active_palette = dict(palette)


def _palette_color(palette, role):
    value = palette.get(role)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _recolor_window_borders(qtile, palette):
    """Actualiza los bordes del layout activo y de ventanas flotantes."""
    focus = _palette_color(palette, "color4")
    normal = _palette_color(palette, "dark")

    for group in qtile.groups:
        for current_layout in group.layouts:
            if focus and hasattr(current_layout, "border_focus"):
                current_layout.border_focus = focus
            if normal and hasattr(current_layout, "border_normal"):
                current_layout.border_normal = normal

    floating_layout = getattr(qtile.config, "floating_layout", None)
    if floating_layout is not None:
        floating_focus = _palette_color(palette, "color3") or focus
        if floating_focus:
            floating_layout.border_focus = floating_focus
        if normal and hasattr(floating_layout, "border_normal"):
            floating_layout.border_normal = normal

    # Fuerza a Qtile a volver a dibujar inmediatamente los bordes visibles.
    for group in qtile.groups:
        if group.screen is not None:
            group.layout_all()


def apply_workspace_theme(qtile, group_name=None):
    """Aplica fondo y paleta del grupo actual; acepta nombres como ``IV``."""
    raw_name = group_name or qtile.current_group.name
    normalized = str(raw_name).strip().upper()
    entry = _load_themes().get(normalized)
    if not entry:
        return False

    wallpaper = Path(entry.get("wallpaper", "")).expanduser()
    if wallpaper.is_file():
        # Esperar a feh evita carreras durante el arranque y cambios rápidos.
        subprocess.run(
            ["feh", "--no-fehbg", "--bg-fill", str(wallpaper)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

    palette = entry.get("palette")
    if isinstance(palette, dict):
        _recolor_window_borders(qtile, palette)
        _recolor_bar(qtile, palette)
    return True

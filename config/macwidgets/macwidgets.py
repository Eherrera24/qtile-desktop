#!/usr/bin/env python3
"""Widgets de escritorio translúcidos para Qtile/X11."""

import calendar
import cairo
import datetime as dt
import json
import math
import os
import re
import signal
import subprocess
import sys
import threading
from pathlib import Path
from urllib.parse import quote

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gdk, GLib, Gtk, Pango  # noqa: E402

try:
    import psutil
except ImportError:
    psutil = None


APP_DIR = Path.home() / ".config" / "macwidgets"
CONFIG_FILE = APP_DIR / "config.json"
PID_FILE = Path.home() / ".cache" / "macwidgets.pid"
EDIT_PID_FILE = Path.home() / ".cache" / "macwidgets-edit.pid"

DEFAULTS = {
    "anchor": "top-right",
    "offset_x": 28,
    "offset_y": 68,
    "width": 330,
    "x": 0,
    "y": 0,
    "custom_position": False,
    "scale": 1.0,
    "opacity": 0.82,
    "clock_style": "iphone",
    "calendar_style": "iphone",
    "weather_location": "Guatemala",
    "custom_text": "Tu espacio, a tu manera.",
    "widget_order": [
        "clock", "calendar", "date", "year_progress", "quote",
        "storage", "weather", "system", "battery",
    ],
    "widget_geometry": {},
    "widgets": {
        "clock": True,
        "calendar": True,
        "weather": True,
        "system": True,
        "battery": True,
        "date": False,
        "year_progress": False,
        "quote": False,
        "storage": False,
    },
}


def load_config():
    try:
        saved = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        saved = {}
    config = {**DEFAULTS, **saved}
    config["widgets"] = {**DEFAULTS["widgets"], **saved.get("widgets", {})}
    requested_order = saved.get("widget_order", DEFAULTS["widget_order"])
    valid_order = [key for key in requested_order if key in DEFAULTS["widgets"]]
    config["widget_order"] = valid_order + [
        key for key in DEFAULTS["widget_order"] if key not in valid_order
    ]
    config["widget_geometry"] = saved.get("widget_geometry", {})
    return config


def save_config(config):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    temporary = CONFIG_FILE.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CONFIG_FILE)


CSS = b"""
window.macwidgets { background-color: transparent; }
.stack { background-color: transparent; }
.resize-handle {
  background-color: rgba(255, 255, 255, 0.28);
  border-radius: 8px;
}
.card {
  background-color: rgba(16, 16, 16, CARD_ALPHA);
  border: 1px solid rgba(255, 255, 255, 0.20);
  border-radius: 22px;
  padding: 18px;
  color: #f5f5f7;
}
.glass-featured {
  background-color: rgba(10, 12, 16, 0.22);
  background-image: linear-gradient(145deg,
    rgba(255, 255, 255, 0.10),
    rgba(255, 255, 255, 0.025) 42%,
    rgba(0, 0, 0, 0.10));
  border: none;
  border-radius: 24px;
  box-shadow:
    inset 0 1px rgba(255, 255, 255, 0.15),
    inset 0 -1px rgba(0, 0, 0, 0.16),
    0 10px 28px rgba(0, 0, 0, 0.18);
}
.glass-featured .title { color: rgba(245,245,247,0.62); letter-spacing: 1px; }
.glass-featured .clock { color: rgba(255,255,255,0.98); font-size: 58px; font-weight: 200; }
.glass-featured .date { color: rgba(245,245,247,0.82); font-size: 14px; }
.glass-featured .accent { color: rgba(255,255,255,0.72); font-size: 13px; font-weight: bold; letter-spacing: 1px; }
.glass-featured .calendar-day { color: rgba(255,255,255,0.98); font-size: 62px; font-weight: 300; }
.glass-featured .calendar-month { color: rgba(255,255,255,0.90); font-size: 17px; font-weight: bold; }
.glass-featured .calendar { color: rgba(255,255,255,0.84); font-size: 13px; }
.clock-digital .clock { font-family: monospace; font-size: 50px; font-weight: bold; }
.clock-digital { background-color: rgba(4, 6, 10, 0.42); border-radius: 14px; }
.clock-minimal { background-color: rgba(10, 12, 16, 0.12); background-image: none; border-radius: 38px; }
.clock-minimal .clock { font-size: 66px; font-weight: 200; }
.clock-minimal .accent { color: rgba(255,255,255,0.68); }
.clock-solo { background-color: rgba(10, 12, 16, 0.18); background-image: none; border-radius: 28px; }
.clock-solo .clock { font-size: 76px; font-weight: 200; }
.clock-pill { background-color: rgba(10, 12, 16, 0.20); background-image: none; border-radius: 60px; }
.clock-pill .clock { font-size: 54px; font-weight: 300; }
.clock-dual { background-color: rgba(10, 12, 16, 0.16); border-radius: 30px; }
.clock-dual .clock { font-size: 34px; font-weight: 300; }
.clock-stacked {
  background-color: rgba(10, 12, 16, 0.16);
  background-image: none;
  border-radius: 24px;
  padding: 2px;
  box-shadow: none;
}
.clock-stacked .stacked-time {
  color: rgba(255,255,255,0.98);
  background-color: transparent;
  background-image: none;
  border: none;
  border-radius: 0;
  font-size: 96px;
  font-weight: 200;
}
.calendar-monthly {
  background-color: rgba(10, 12, 16, 0.16);
  background-image: none;
  border-radius: 24px;
  padding: 2px;
  box-shadow: none;
}
.calendar-monthly .calendar { font-size: 16px; font-weight: bold; }
.calendar-monthly .calendar-month { font-size: 20px; font-weight: bold; }
.calendar-compact { background-color: rgba(10, 12, 16, 0.16); border-radius: 38px; }
.calendar-compact .calendar-day { font-size: 78px; }
.calendar-compact .calendar { font-size: 0; }
.title { color: rgba(245,245,247,0.68); font-size: 12px; font-weight: bold; }
.clock { color: #ffffff; font-size: 46px; font-weight: 300; }
.date { color: rgba(245,245,247,0.78); font-size: 15px; }
.calendar { color: #f5f5f7; font-family: monospace; font-size: 15px; }
.value { color: #ffffff; font-size: 24px; font-weight: bold; }
.detail { color: rgba(245,245,247,0.72); font-size: 13px; }
.weather { color: #ffffff; font-size: 22px; font-weight: bold; }
.standalone-day { color: rgba(255,255,255,0.98); font-size: 76px; font-weight: bold; }
.quote { color: rgba(255,255,255,0.92); font-size: 20px; font-weight: 300; }
.progress trough { background-color: rgba(255,255,255,0.12); border-radius: 8px; min-height: 12px; }
.progress progress { background-color: rgba(255,255,255,0.78); border-radius: 8px; min-height: 12px; }
"""


def label(text="", style=None, align=0.0):
    item = Gtk.Label(label=text, xalign=align)
    item.set_selectable(False)
    if style:
        item.get_style_context().add_class(style)
    return item


def card(title, style=None):
    frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
    frame.get_style_context().add_class("card")
    if style:
        frame.get_style_context().add_class(style)
    if title:
        frame.pack_start(label(title.upper(), "title"), False, False, 0)
    return frame


class AnalogClock(Gtk.DrawingArea):
    """Esfera ligera inspirada en el widget de reloj de iOS."""

    def __init__(self):
        super().__init__()
        self.set_size_request(145, 145)
        self.connect("draw", self._draw)

    def _draw(self, _widget, cr):
        now = dt.datetime.now()
        width, height = self.get_allocated_width(), self.get_allocated_height()
        radius = min(width, height) / 2 - 7
        cx, cy = width / 2, height / 2
        cr.set_source_rgba(0.03, 0.04, 0.06, 0.42)
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.fill()
        for index in range(60):
            angle = index * math.pi / 30 - math.pi / 2
            inner = radius - (10 if index % 5 == 0 else 5)
            cr.set_line_width(2 if index % 5 == 0 else 1)
            cr.set_source_rgba(1, 1, 1, 0.90 if index % 5 == 0 else 0.42)
            cr.move_to(cx + inner * math.cos(angle), cy + inner * math.sin(angle))
            cr.line_to(cx + (radius - 2) * math.cos(angle), cy + (radius - 2) * math.sin(angle))
            cr.stroke()

        def hand(angle, length, width_value, red=False):
            cr.set_line_cap(1)
            cr.set_line_width(width_value)
            cr.set_source_rgba(1, 1, 1, 0.58) if red else cr.set_source_rgba(1, 1, 1, 0.94)
            cr.move_to(cx, cy)
            cr.line_to(cx + length * math.cos(angle), cy + length * math.sin(angle))
            cr.stroke()

        hour = ((now.hour % 12) + now.minute / 60) * math.pi / 6 - math.pi / 2
        minute = (now.minute + now.second / 60) * math.pi / 30 - math.pi / 2
        second = now.second * math.pi / 30 - math.pi / 2
        hand(hour, radius * 0.48, 5)
        hand(minute, radius * 0.70, 3)
        hand(second, radius * 0.78, 1.5, True)
        cr.set_source_rgba(1, 1, 1, 0.88)
        cr.arc(cx, cy, 4, 0, 2 * math.pi)
        cr.fill()
        return False


class StackedClock(Gtk.DrawingArea):
    """Horas y minutos dibujados para llenar dos mitades de un cuadrado."""

    def __init__(self):
        super().__init__()
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.connect("draw", self._draw)

    def _draw_half(self, cr, text, top, width, height):
        cr.save()
        cr.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(100)
        extents = cr.text_extents(text)
        margin = min(width, height) * 0.08
        half_height = height / 2
        center_gap = min(width, height) * 0.025
        target_width = width - 2 * margin
        target_height = half_height - margin - center_gap / 2
        scale = min(
            target_width / max(1, extents.width),
            target_height / max(1, extents.height),
        )
        drawn_width = extents.width * scale
        drawn_height = extents.height * scale
        x = (width - drawn_width) / 2
        y = (
            half_height - drawn_height - center_gap / 2
            if top == 0 else top + center_gap / 2
        )
        cr.translate(x, y)
        cr.scale(scale, scale)
        cr.move_to(-extents.x_bearing, -extents.y_bearing)
        cr.set_source_rgba(1, 1, 1, 0.97)
        cr.show_text(text)
        cr.restore()

    def _draw(self, _widget, cr):
        now = dt.datetime.now()
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        half = height / 2
        self._draw_half(cr, now.strftime("%H"), 0, width, height)
        self._draw_half(cr, now.strftime("%M"), half, width, height)
        return False


class MonthlyCalendar(Gtk.DrawingArea):
    """Calendario mensual dibujado sin imponer tamaño mínimo."""

    def __init__(self):
        super().__init__()
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.connect("draw", self._draw)

    @staticmethod
    def _center_text(cr, text, x, y, size, bold=False):
        cr.select_font_face(
            "DejaVu Sans Mono", cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL,
        )
        cr.set_font_size(size)
        extents = cr.text_extents(text)
        cr.move_to(x - extents.width / 2 - extents.x_bearing,
                   y - extents.height / 2 - extents.y_bearing)
        cr.show_text(text)

    def _draw(self, _widget, cr):
        now = dt.datetime.now()
        width, height = self.get_allocated_width(), self.get_allocated_height()
        margin = min(width, height) * 0.08
        content_width, content_height = width - 2 * margin, height - 2 * margin
        months = ("ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
                  "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE")
        weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(now.year, now.month)
        rows = len(weeks) + 2
        row_height, col_width = content_height / rows, content_width / 7
        font_size = max(8, min(col_width * 0.48, row_height * 0.48))
        cr.set_source_rgba(1, 1, 1, 0.95)
        self._center_text(cr, f"{months[now.month - 1]} {now.year}", width / 2,
                          margin + row_height / 2, font_size * 1.18, True)
        for column, name in enumerate(("Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do")):
            self._center_text(cr, name, margin + (column + 0.5) * col_width,
                              margin + 1.5 * row_height, font_size * 0.85, True)
        for row, week in enumerate(weeks, start=2):
            for column, day in enumerate(week):
                if day:
                    self._center_text(cr, str(day), margin + (column + 0.5) * col_width,
                                      margin + (row + 0.5) * row_height,
                                      font_size, day == now.day)
        return False


class WidgetWindow(Gtk.Window):
    def __init__(self, config, widget_key, index=0, edit_mode=False):
        super().__init__(title="MacWidgets")
        self.config = config
        self.widget_key = widget_key
        self.index = index
        self.edit_mode = edit_mode
        self._drag_origin = None
        self._resize_origin = None
        self._content_scale = None
        self.set_name("macwidgets")
        self.get_style_context().add_class("macwidgets")
        self.set_wmclass("MacWidgets", "MacWidgets")
        self.set_decorated(False)
        self.set_resizable(edit_mode)
        self.set_skip_taskbar_hint(not edit_mode)
        self.set_skip_pager_hint(True)
        self.set_keep_below(not edit_mode)
        self.set_keep_above(edit_mode)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY if edit_mode else Gdk.WindowTypeHint.DESKTOP)
        self.set_accept_focus(edit_mode)
        self.set_app_paintable(True)
        visual = self.get_screen().get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.stack = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.stack.get_style_context().add_class("stack")
        self.overlay = Gtk.Overlay()
        self.overlay.add(self.stack)
        self.add(self.overlay)
        self.clock_time = self.clock_date = self.clock_weekday = None
        self.clock_hours = self.clock_minutes = None
        self.stacked_clock = None
        self.analog_clock = None
        self.calendar_text = self.calendar_day = None
        self.calendar_weekday = self.calendar_month = None
        self.calendar_content = None
        self.monthly_calendar = None
        self.weather_text = self.system_value = self.system_detail = None
        self.battery_value = self.battery_detail = None
        self.date_day = self.date_detail = None
        self.year_value = self.year_detail = self.year_bar = None
        self.quote_text = None
        self.storage_value = self.storage_detail = None
        self._build()
        if self.widget_key == "clock" and self.config.get("clock_style") == "stacked":
            geometry = Gdk.Geometry()
            geometry.min_aspect = 1.0
            geometry.max_aspect = 1.0
            self.set_geometry_hints(None, geometry, Gdk.WindowHints.ASPECT)
        if self.widget_key == "calendar" and self.config.get("calendar_style") == "monthly":
            geometry = Gdk.Geometry()
            geometry.min_aspect = 1.0
            geometry.max_aspect = 1.0
            self.set_geometry_hints(None, geometry, Gdk.WindowHints.ASPECT)
        if edit_mode:
            editor = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            editor.pack_start(label(f"✥ {self.widget_key.upper()} — ARRASTRA", "title"), True, True, 0)
            self.stack.pack_start(editor, False, False, 0)
            self.stack.reorder_child(editor, 0)
            resize_handle = Gtk.EventBox()
            resize_handle.set_size_request(34, 34)
            resize_handle.set_halign(Gtk.Align.END)
            resize_handle.set_valign(Gtk.Align.END)
            resize_handle.set_tooltip_text("Arrastra esta esquina para cambiar ancho y alto")
            resize_handle.get_style_context().add_class("resize-handle")
            resize_handle.add(label("◢", "value", 0.5))
            resize_handle.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            resize_handle.connect("button-press-event", self._begin_free_resize)
            self.overlay.add_overlay(resize_handle)
            self.add_events(
                Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK |
                Gdk.EventMask.POINTER_MOTION_MASK
            )
            self.connect("button-press-event", self._begin_move)
            self.connect("motion-notify-event", self._move_drag)
            self.connect("button-release-event", self._save_geometry)
            self.connect("configure-event", self._save_configure_event)
        self.connect("realize", self._place)
        self.connect("realize", self._make_click_through)
        GLib.timeout_add_seconds(1, self._tick)
        GLib.timeout_add_seconds(30, self._update_system)
        GLib.timeout_add_seconds(900, self._request_weather)
        self._tick()
        self._update_system()
        self._request_weather()

    def _build(self):
        builders = {
            "clock": self._add_clock,
            "calendar": self._add_calendar,
            "weather": self._add_weather,
            "system": self._add_system,
            "battery": self._add_battery,
            "date": self._add_date,
            "year_progress": self._add_year_progress,
            "quote": self._add_quote,
            "storage": self._add_storage,
        }
        builders[self.widget_key]()
        geometry = self.config.get("widget_geometry", {}).get(self.widget_key, {})
        width = int(geometry.get("width", self.config["width"]))
        height = int(geometry.get("height", -1))
        if self.widget_key == "clock" and self.config.get("clock_style") == "stacked":
            side = max(width, height if height > 0 else width)
            width = height = side
        if self.widget_key == "calendar" and self.config.get("calendar_style") == "monthly":
            side = max(width, height if height > 0 else width)
            width = height = side
        self.set_default_size(
            width, height,
        )

    def _begin_free_resize(self, _widget, event):
        if event.button == 1 and self.get_window():
            self.get_window().begin_resize_drag(
                Gdk.WindowEdge.SOUTH_EAST,
                event.button,
                int(event.x_root),
                int(event.y_root),
                event.time,
            )
            return True
        return False

    def _add_clock(self):
            style = self.config.get("clock_style", "iphone")
            box = card("", "glass-featured")
            box.get_style_context().add_class(f"clock-{style}")
            self.clock_weekday = label(style="accent")
            self.clock_time = label(style="clock")
            self.clock_date = label(style="date")
            if style == "iphone":
                self.analog_clock = AnalogClock()
                self.analog_clock.set_halign(Gtk.Align.CENTER)
                self.analog_clock.set_valign(Gtk.Align.CENTER)
                box.pack_start(self.analog_clock, True, True, 0)
            elif style == "dual":
                content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
                self.analog_clock = AnalogClock()
                content.pack_start(self.analog_clock, False, False, 0)
                content.pack_start(self.clock_time, True, True, 0)
                box.pack_start(content, True, True, 0)
            elif style == "stacked":
                self.stacked_clock = StackedClock()
                box.pack_start(self.stacked_clock, True, True, 0)
            else:
                box.pack_start(self.clock_time, False, False, 0)
            self.stack.pack_start(box, True, True, 0)

    def _add_calendar(self):
            style = self.config.get("calendar_style", "iphone")
            box = card("", "glass-featured")
            box.get_style_context().add_class(f"calendar-{style}")
            if style == "monthly":
                self.monthly_calendar = MonthlyCalendar()
                box.pack_start(self.monthly_calendar, True, True, 0)
                self.stack.pack_start(box, True, True, 0)
                return
            heading = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            self.calendar_day = label(style="calendar-day")
            details = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
            self.calendar_weekday = label(style="accent")
            self.calendar_month = label(style="calendar-month")
            details.pack_start(self.calendar_weekday, False, False, 0)
            if style != "monthly":
                details.pack_start(self.calendar_month, False, False, 0)
            heading.pack_start(self.calendar_day, False, False, 0)
            heading.pack_start(details, False, False, 0)
            if style != "monthly":
                box.pack_start(heading, False, False, 0)
            else:
                self.calendar_content = Gtk.Box(
                    orientation=Gtk.Orientation.VERTICAL, spacing=10
                )
                self.calendar_content.set_halign(Gtk.Align.FILL)
                self.calendar_content.set_valign(Gtk.Align.CENTER)
                self.calendar_content.set_hexpand(True)
                self.calendar_content.set_vexpand(False)
                self.calendar_month.set_halign(Gtk.Align.FILL)
                self.calendar_month.set_xalign(0.5)
                self.calendar_content.pack_start(
                    self.calendar_month, False, False, 0
                )
                box.pack_start(self.calendar_content, True, True, 0)
            self.calendar_text = label(style="calendar")
            if style == "monthly":
                self.calendar_text.set_halign(Gtk.Align.FILL)
                self.calendar_text.set_valign(Gtk.Align.CENTER)
                self.calendar_text.set_xalign(0.5)
                self.calendar_text.set_yalign(0.5)
                self.calendar_text.set_justify(Gtk.Justification.CENTER)
                self.calendar_text.set_hexpand(True)
                self.calendar_text.set_vexpand(False)
                self.calendar_content.pack_start(
                    self.calendar_text, False, False, 0
                )
            elif style != "compact":
                box.pack_start(self.calendar_text, False, False, 0)
            self.stack.pack_start(box, True, True, 0)

    def _add_weather(self):
            box = card("Clima")
            self.weather_text = label("Cargando…", "weather")
            box.pack_start(self.weather_text, False, False, 0)
            self.stack.pack_start(box, True, True, 0)

    def _add_system(self):
            box = card("Sistema")
            self.system_value = label(style="value")
            self.system_detail = label(style="detail")
            box.pack_start(self.system_value, False, False, 0)
            box.pack_start(self.system_detail, False, False, 0)
            self.stack.pack_start(box, True, True, 0)

    def _add_battery(self):
            box = card("Batería")
            self.battery_value = label(style="value")
            self.battery_detail = label(style="detail")
            box.pack_start(self.battery_value, False, False, 0)
            box.pack_start(self.battery_detail, False, False, 0)
            self.stack.pack_start(box, True, True, 0)

    def _add_date(self):
            box = card("FECHA", "glass-featured")
            self.date_day = label(style="standalone-day", align=0.5)
            self.date_detail = label(style="date", align=0.5)
            box.pack_start(self.date_day, True, True, 0)
            box.pack_start(self.date_detail, False, False, 0)
            self.stack.pack_start(box, True, True, 0)

    def _add_year_progress(self):
            box = card("PROGRESO DEL AÑO", "glass-featured")
            self.year_value = label(style="value", align=0.5)
            self.year_bar = Gtk.ProgressBar()
            self.year_bar.get_style_context().add_class("progress")
            self.year_detail = label(style="detail", align=0.5)
            box.pack_start(self.year_value, True, True, 0)
            box.pack_start(self.year_bar, False, False, 0)
            box.pack_start(self.year_detail, False, False, 0)
            self.stack.pack_start(box, True, True, 0)

    def _add_quote(self):
            box = card("TEXTO", "glass-featured")
            self.quote_text = label(self.config.get("custom_text", ""), "quote", 0.5)
            self.quote_text.set_line_wrap(True)
            self.quote_text.set_justify(Gtk.Justification.CENTER)
            box.pack_start(self.quote_text, True, True, 0)
            self.stack.pack_start(box, True, True, 0)

    def _add_storage(self):
            box = card("ALMACENAMIENTO", "glass-featured")
            self.storage_value = label(style="value", align=0.5)
            self.storage_detail = label(style="detail", align=0.5)
            box.pack_start(self.storage_value, True, True, 0)
            box.pack_start(self.storage_detail, False, False, 0)
            self.stack.pack_start(box, True, True, 0)

    def _place(self, *_):
        geometry = self.config.get("widget_geometry", {}).get(self.widget_key)
        if geometry:
            self.move(int(geometry["x"]), int(geometry["y"]))
            return
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        area = monitor.get_workarea()
        width, height = self.get_size()
        xoff, yoff = int(self.config["offset_x"]), int(self.config["offset_y"])
        if self.config.get("custom_position"):
            x, y = int(self.config["x"]), int(self.config["y"])
        else:
            anchor = self.config["anchor"]
            x = area.x + xoff if anchor.endswith("left") else area.x + area.width - width - xoff
            y = area.y + yoff if anchor.startswith("top") else area.y + area.height - height - yoff
        # Primera migración: conserva el anclaje y separa las tarjetas.
        self.move(x, y + self.index * 155)

    def _make_click_through(self, *_):
        window = self.get_window()
        if window:
            if not self.edit_mode:
                # Qtile no debe tratar el panel como una ventana normal ni darle foco.
                window.set_override_redirect(True)
                window.set_pass_through(True)
                window.lower()

    def _begin_move(self, _widget, event):
        if isinstance(Gtk.get_event_widget(event), Gtk.Button):
            return False
        if event.button == 1:
            x, y = self.get_position()
            self._drag_origin = (int(event.x_root), int(event.y_root), x, y)
        return True

    def _move_drag(self, _widget, event):
        if self._drag_origin and event.state & Gdk.ModifierType.BUTTON1_MASK:
            root_x, root_y, window_x, window_y = self._drag_origin
            self.move(
                window_x + int(event.x_root) - root_x,
                window_y + int(event.y_root) - root_y,
            )
            return True
        return False

    def _save_geometry(self, *_):
        self._drag_origin = None
        x, y = self.get_position()
        width, _height = self.get_size()
        self.config.setdefault("widget_geometry", {})[self.widget_key] = {
            "x": x, "y": y, "width": width, "height": _height,
        }
        save_config(self.config)
        return False

    def _save_configure_event(self, _widget, event):
        """Guarda movimientos y tamaños realizados por Qtile/X11."""
        self.config.setdefault("widget_geometry", {})[self.widget_key] = {
            "x": int(event.x), "y": int(event.y),
            "width": int(event.width), "height": int(event.height),
        }
        save_config(self.config)
        self._scale_content(int(event.width), int(event.height))
        return False

    def _scale_content(self, width, height):
        """Escala contenido y no sólo el rectángulo de fondo."""
        if self.widget_key == "clock":
            bases = {
                "iphone": (190, 190), "solo": (320, 145),
                "digital": (410, 140), "minimal": (290, 125),
                "pill": (310, 115), "dual": (370, 185),
                "stacked": (224, 224),
            }
            base_width, base_height = bases.get(self.config.get("clock_style"), (320, 145))
            labels = (self.clock_time, self.clock_hours, self.clock_minutes)
        elif self.widget_key == "calendar":
            if self.monthly_calendar is not None:
                return
            bases = {"iphone": (330, 300), "monthly": (320, 320), "compact": (260, 185)}
            base_width, base_height = bases.get(self.config.get("calendar_style"), (330, 300))
            labels = (
                self.calendar_day, self.calendar_weekday,
                self.calendar_month, self.calendar_text,
            )
            if self.calendar_content is not None:
                margin = max(12, int(min(width, height) * 0.08))
                self.calendar_content.set_margin_top(margin)
                self.calendar_content.set_margin_bottom(margin)
                self.calendar_content.set_margin_start(margin)
                self.calendar_content.set_margin_end(margin)
        else:
            return
        factor = max(0.55, min(2.25, math.sqrt(
            max(1, width * height) / (base_width * base_height)
        )))
        if self._content_scale is not None and abs(factor - self._content_scale) < 0.03:
            return
        self._content_scale = factor
        attributes = Pango.AttrList()
        if self.widget_key == "clock" and self.config.get("clock_style") == "stacked":
            digit_size = max(56, min(int(height * 0.39), int(width * 0.43)))
            attributes.insert(Pango.attr_size_new_absolute(digit_size * Pango.SCALE))
        else:
            attributes.insert(Pango.attr_scale_new(factor))
        for current_label in labels:
            if current_label is not None:
                current_label.set_attributes(attributes)
        if self.analog_clock:
            analog_size = max(90, int(min(width, height) * (0.78 if self.config.get("clock_style") == "iphone" else 0.68)))
            self.analog_clock.set_size_request(analog_size, analog_size)

    def _tick(self):
        now = dt.datetime.now()
        weekdays = ("LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO")
        months = ("ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE")
        if self.clock_time:
            clock_format = "%H:%M:%S" if self.config.get("clock_style") == "digital" else "%H:%M"
            self.clock_time.set_text(now.strftime(clock_format))
            if self.analog_clock:
                self.analog_clock.queue_draw()
        if self.clock_hours:
            self.clock_hours.set_text(now.strftime("%H"))
            self.clock_minutes.set_text(now.strftime("%M"))
        if self.stacked_clock:
            self.stacked_clock.queue_draw()
        if self.calendar_text:
            self.calendar_day.set_text(str(now.day))
            self.calendar_weekday.set_text(weekdays[now.weekday()])
            self.calendar_month.set_text(f"{months[now.month - 1]} {now.year}")
            cal = calendar.TextCalendar(firstweekday=0).formatmonth(now.year, now.month)
            lines = cal.rstrip().splitlines()
            self.calendar_text.set_text("\n".join(lines[1:]))
        if self.monthly_calendar:
            self.monthly_calendar.queue_draw()
        if self.date_day:
            self.date_day.set_text(str(now.day))
            self.date_detail.set_text(
                f"{weekdays[now.weekday()]} · {months[now.month - 1]} {now.year}"
            )
        if self.year_value:
            start = dt.datetime(now.year, 1, 1)
            end = dt.datetime(now.year + 1, 1, 1)
            fraction = (now - start).total_seconds() / (end - start).total_seconds()
            self.year_value.set_text(f"{fraction * 100:.1f}%")
            self.year_bar.set_fraction(fraction)
            self.year_detail.set_text(f"Día {now.timetuple().tm_yday} de {(end - start).days}")
        return True

    def _update_system(self):
        if psutil and self.system_value:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            self.system_value.set_text(f"CPU {cpu:.0f}%  ·  RAM {memory.percent:.0f}%")
            self.system_detail.set_text(f"{memory.used / 2**30:.1f} de {memory.total / 2**30:.1f} GB en uso")
        if psutil and self.battery_value:
            battery = psutil.sensors_battery()
            if battery:
                icon = "⚡" if battery.power_plugged else "◉"
                self.battery_value.set_text(f"{icon}  {battery.percent:.0f}%")
                self.battery_detail.set_text("Cargando" if battery.power_plugged else "Usando batería")
            else:
                self.battery_value.set_text("Sin batería")
                self.battery_detail.set_text("Equipo conectado a corriente")
        if psutil and self.storage_value:
            disk = psutil.disk_usage(str(Path.home()))
            self.storage_value.set_text(f"{disk.percent:.0f}% usado")
            self.storage_detail.set_text(
                f"{disk.free / 2**30:.0f} GB libres de {disk.total / 2**30:.0f} GB"
            )
        return True

    def _request_weather(self):
        if not self.weather_text:
            return True
        location = self.config.get("weather_location", "Guatemala")

        def fetch():
            try:
                result = subprocess.run(
                    ["curl", "-fsS", "--max-time", "8", f"https://wttr.in/{quote(location)}?format=%c+%t+%C"],
                    text=True, capture_output=True, timeout=10, check=False,
                )
                text = result.stdout.strip() if result.returncode == 0 else "Clima no disponible"
            except (OSError, subprocess.TimeoutExpired):
                text = "Clima no disponible"
            GLib.idle_add(self.weather_text.set_text, text)

        threading.Thread(target=fetch, daemon=True).start()
        return True


class SettingsWindow(Gtk.Window):
    def __init__(self, config):
        super().__init__(title="Configurar MacWidgets")
        self.set_wmclass("MacWidgets", "MacWidgets")
        self.config = config
        self.original_clock_style = config.get("clock_style", "iphone")
        self.original_calendar_style = config.get("calendar_style", "iphone")
        self.set_default_size(520, 720)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(scroll)
        grid = Gtk.Grid(column_spacing=14, row_spacing=14)
        grid.set_border_width(22)
        scroll.add(grid)
        title = label("Widgets de escritorio", "value")
        grid.attach(title, 0, 0, 2, 1)
        subtitle = label("Activa, quita y cambia el orden de cada tarjeta", "detail")
        grid.attach(subtitle, 0, 1, 2, 1)
        self.checks = {}
        self.names = {
            "clock": "Reloj", "calendar": "Calendario", "weather": "Clima",
            "system": "Sistema", "battery": "Batería",
            "date": "Fecha independiente", "year_progress": "Progreso del año",
            "quote": "Texto personalizado", "storage": "Almacenamiento",
        }
        self.order = list(config["widget_order"])
        self.widget_list = Gtk.ListBox()
        self.widget_list.set_selection_mode(Gtk.SelectionMode.NONE)
        grid.attach(self.widget_list, 0, 2, 2, 1)
        self._rebuild_widget_list()
        row = 3
        grid.attach(label("Estilo del reloj"), 0, row, 1, 1)
        self.clock_style = Gtk.ComboBoxText()
        for value, visible_name in (
            ("iphone", "Analógico iOS — sólo reloj"),
            ("solo", "Sólo hora grande"),
            ("digital", "Digital con segundos"),
            ("minimal", "Minimalista transparente"),
            ("pill", "Cápsula"),
            ("dual", "Analógico + digital"),
            ("stacked", "iPhone apilado — horas/minutos"),
        ):
            self.clock_style.append(value, visible_name)
        self.clock_style.set_active_id(config.get("clock_style", "iphone"))
        grid.attach(self.clock_style, 1, row, 1, 1)
        row += 1
        grid.attach(label("Estilo del calendario"), 0, row, 1, 1)
        self.calendar_style = Gtk.ComboBoxText()
        for value, visible_name in (
            ("iphone", "iPhone"), ("monthly", "Mes completo"),
            ("compact", "Fecha compacta"),
        ):
            self.calendar_style.append(value, visible_name)
        self.calendar_style.set_active_id(config.get("calendar_style", "iphone"))
        grid.attach(self.calendar_style, 1, row, 1, 1)
        row += 1
        grid.attach(label("Texto personalizado"), 0, row, 1, 1)
        self.custom_text = Gtk.Entry(text=config.get("custom_text", ""))
        self.custom_text.set_placeholder_text("Escribe la frase del widget")
        grid.attach(self.custom_text, 1, row, 1, 1)
        row += 1
        grid.attach(label("Ubicación del clima"), 0, row, 1, 1)
        self.location = Gtk.Entry(text=config["weather_location"])
        grid.attach(self.location, 1, row, 1, 1)
        row += 1
        grid.attach(label("Anclar en"), 0, row, 1, 1)
        self.anchor = Gtk.ComboBoxText()
        anchors = {
            "top-right": "Arriba derecha", "top-left": "Arriba izquierda",
            "bottom-right": "Abajo derecha", "bottom-left": "Abajo izquierda",
        }
        for value, visible_name in anchors.items():
            self.anchor.append(value, visible_name)
        self.anchor.set_active_id(config["anchor"])
        grid.attach(self.anchor, 1, row, 1, 1)
        row += 1
        self.offset_x = self._spin(config["offset_x"], 0, 2000, 2)
        self.offset_y = self._spin(config["offset_y"], 0, 2000, 2)
        grid.attach(label("Margen X / Y"), 0, row, 1, 1)
        offsets = Gtk.Box(spacing=8)
        offsets.pack_start(self.offset_x, True, True, 0)
        offsets.pack_start(self.offset_y, True, True, 0)
        grid.attach(offsets, 1, row, 1, 1)
        row += 1
        grid.attach(label("Ancho"), 0, row, 1, 1)
        self.width = self._spin(config["width"], 220, 900, 10)
        grid.attach(self.width, 1, row, 1, 1)
        row += 1
        grid.attach(label("Escala"), 0, row, 1, 1)
        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.70, 1.60, 0.05)
        self.scale.set_value(config["scale"])
        self.scale.set_value_pos(Gtk.PositionType.RIGHT)
        grid.attach(self.scale, 1, row, 1, 1)
        row += 1
        self.position_x = self._spin(config["x"], -10000, 10000, 5)
        self.position_y = self._spin(config["y"], -10000, 10000, 5)
        grid.attach(label("Posición X / Y"), 0, row, 1, 1)
        positions = Gtk.Box(spacing=8)
        positions.pack_start(self.position_x, True, True, 0)
        positions.pack_start(self.position_y, True, True, 0)
        grid.attach(positions, 1, row, 1, 1)
        row += 1
        self.custom_position = Gtk.CheckButton(label="Usar posición X/Y exacta")
        self.custom_position.set_active(config["custom_position"])
        grid.attach(self.custom_position, 0, row, 2, 1)
        row += 1
        grid.attach(label("Transparencia del cristal"), 0, row, 1, 1)
        self.opacity = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.05, 0.90, 0.01)
        # El usuario controla transparencia; CSS internamente necesita opacidad.
        self.opacity.set_value(1.0 - float(config["opacity"]))
        self.opacity.set_value_pos(Gtk.PositionType.RIGHT)
        self.opacity.set_tooltip_text("Mayor valor = widget más transparente y blur más visible")
        self.opacity.connect("value-changed", self._preview_opacity)
        grid.attach(self.opacity, 1, row, 1, 1)
        row += 1
        self.preview = Gtk.EventBox()
        self.preview.set_size_request(-1, 72)
        self.preview.add(label("Vista previa del cristal", "weather", 0.5))
        self.preview.get_style_context().add_class("card")
        grid.attach(self.preview, 0, row, 2, 1)
        row += 1
        actions = Gtk.Box(spacing=10)
        edit_position = Gtk.Button(label="Mover arrastrando")
        edit_position.connect("clicked", self._edit_position)
        actions.pack_start(edit_position, True, True, 0)
        save = Gtk.Button(label="Guardar y aplicar")
        save.connect("clicked", self._save)
        actions.pack_start(save, True, True, 0)
        grid.attach(actions, 0, row, 2, 1)
        self.connect("destroy", Gtk.main_quit)

    @staticmethod
    def _spin(value, minimum, maximum, step):
        control = Gtk.SpinButton.new_with_range(minimum, maximum, step)
        control.set_value(value)
        return control

    def _rebuild_widget_list(self):
        for child in self.widget_list.get_children():
            self.widget_list.remove(child)
        for index, key in enumerate(self.order):
            line = Gtk.Box(spacing=8)
            check = Gtk.CheckButton(label=self.names[key])
            check.set_active(self.config["widgets"].get(key, True))
            self.checks[key] = check
            line.pack_start(check, True, True, 4)
            up = Gtk.Button(label="↑")
            down = Gtk.Button(label="↓")
            up.set_sensitive(index > 0)
            down.set_sensitive(index < len(self.order) - 1)
            up.connect("clicked", self._move_widget, key, -1)
            down.connect("clicked", self._move_widget, key, 1)
            line.pack_start(up, False, False, 0)
            line.pack_start(down, False, False, 0)
            self.widget_list.add(line)
        self.widget_list.show_all()

    def _move_widget(self, _button, key, direction):
        states = {name: control.get_active() for name, control in self.checks.items()}
        self.config["widgets"].update(states)
        old = self.order.index(key)
        new = max(0, min(len(self.order) - 1, old + direction))
        self.order.insert(new, self.order.pop(old))
        self._rebuild_widget_list()

    def _store_controls(self):
        self.config["widgets"] = {key: check.get_active() for key, check in self.checks.items()}
        self.config["widget_order"] = list(self.order)
        self.config["custom_text"] = self.custom_text.get_text().strip()
        new_clock_style = self.clock_style.get_active_id() or "iphone"
        new_calendar_style = self.calendar_style.get_active_id() or "iphone"
        if new_clock_style != self.original_clock_style:
            sizes = {
                "iphone": (190, 190), "solo": (320, 145),
                "digital": (410, 140), "minimal": (290, 125),
                "pill": (310, 115), "dual": (370, 185),
                "stacked": (224, 224),
            }
            geometry = self.config.setdefault("widget_geometry", {}).setdefault("clock", {})
            geometry["width"], geometry["height"] = sizes[new_clock_style]
        if new_calendar_style != self.original_calendar_style:
            sizes = {"iphone": (330, 300), "monthly": (320, 320), "compact": (260, 185)}
            geometry = self.config.setdefault("widget_geometry", {}).setdefault("calendar", {})
            geometry["width"], geometry["height"] = sizes[new_calendar_style]
        self.config["clock_style"] = new_clock_style
        self.config["calendar_style"] = new_calendar_style
        self.config["weather_location"] = self.location.get_text().strip() or "Guatemala"
        self.config["anchor"] = self.anchor.get_active_id() or "top-right"
        self.config["offset_x"] = self.offset_x.get_value_as_int()
        self.config["offset_y"] = self.offset_y.get_value_as_int()
        self.config["width"] = self.width.get_value_as_int()
        self.config["scale"] = round(self.scale.get_value(), 2)
        self.config["x"] = self.position_x.get_value_as_int()
        self.config["y"] = self.position_y.get_value_as_int()
        self.config["custom_position"] = self.custom_position.get_active()
        self.config["opacity"] = round(1.0 - self.opacity.get_value(), 2)

    def _edit_position(self, *_):
        self._store_controls()
        save_config(self.config)
        subprocess.Popen([str(Path.home() / ".local/bin/macwidgets"), "edit"])
        self.destroy()

    def _preview_opacity(self, control):
        preview_config = dict(self.config)
        preview_config["opacity"] = 1.0 - control.get_value()
        provider = Gtk.CssProvider()
        provider.load_from_data(build_css(preview_config))
        self.get_style_context().add_provider(
            provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1
        )

    def _save(self, *_):
        self._store_controls()
        save_config(self.config)
        subprocess.run([str(Path.home() / ".local/bin/macwidgets"), "restart"], check=False)
        self.destroy()


class EditToolbar(Gtk.Window):
    """Barra pequeña para finalizar la edición de ventanas individuales."""

    def __init__(self):
        super().__init__(title="Editar MacWidgets")
        self.set_wmclass("MacWidgets", "MacWidgets")
        self.set_keep_above(True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(12)
        box = Gtk.Box(spacing=10)
        box.pack_start(label("Arrastra y redimensiona cada widget por separado"), True, True, 0)
        finish = Gtk.Button(label="Guardar y salir")
        finish.connect("clicked", lambda *_: Gtk.main_quit())
        box.pack_end(finish, False, False, 0)
        self.add(box)


def stop_running():
    try:
        pid = int(PID_FILE.read_text().strip())
        command = Path(f"/proc/{pid}/cmdline").read_bytes()
        if b"macwidgets.py" in command:
            os.kill(pid, signal.SIGTERM)
    except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError):
        pass
    try:
        PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def stop_editor():
    try:
        pid = int(EDIT_PID_FILE.read_text().strip())
        command = Path(f"/proc/{pid}/cmdline").read_bytes()
        if b"macwidgets.py" in command:
            os.kill(pid, signal.SIGTERM)
    except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError):
        pass
    EDIT_PID_FILE.unlink(missing_ok=True)


def build_css(config):
    opacity = min(0.95, max(0.10, float(config["opacity"])))
    scale = min(1.6, max(0.7, float(config["scale"])))
    css = CSS.decode().replace("CARD_ALPHA", f"{opacity:.2f}")
    return re.sub(
        r"font-size: (\d+)px",
        lambda match: f"font-size: {max(9, round(int(match.group(1)) * scale))}px",
        css,
    ).encode()


def run_widgets(edit_mode=False):
    stop_running()
    if edit_mode:
        stop_editor()
    active_pid_file = EDIT_PID_FILE if edit_mode else PID_FILE
    active_pid_file.parent.mkdir(parents=True, exist_ok=True)
    active_pid_file.write_text(str(os.getpid()))
    config = load_config()
    provider = Gtk.CssProvider()
    provider.load_from_data(build_css(config))
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    windows = [
        WidgetWindow(config, key, index, edit_mode=edit_mode)
        for index, key in enumerate(config["widget_order"])
        if config["widgets"].get(key)
    ]
    toolbar = EditToolbar() if edit_mode else None
    if edit_mode:
        # Qtile oculta los widgets normales cuando detecta una ventana.
        # Durante la edición estas señales no deben cerrar el proceso.
        signal.signal(signal.SIGUSR1, lambda *_: None)
        signal.signal(signal.SIGUSR2, lambda *_: None)
    else:
        def set_visible(visible):
            for current_window in windows:
                (current_window.show_all if visible else current_window.hide)()
            return False

        signal.signal(signal.SIGUSR1, lambda *_: GLib.idle_add(set_visible, False))
        signal.signal(signal.SIGUSR2, lambda *_: GLib.idle_add(set_visible, True))
    for current_window in windows:
        current_window.show_all()

    def arrange_new_windows():
        """Separa widgets migrados que todavía no tienen posición propia."""
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        area = monitor.get_workarea()
        gap = 12
        cursor_y = area.y + int(config["offset_y"])
        for current_window in windows:
            if current_window.widget_key in config.get("widget_geometry", {}):
                continue
            width, height = current_window.get_size()
            if config["anchor"].endswith("left"):
                x = area.x + int(config["offset_x"])
            else:
                x = area.x + area.width - width - int(config["offset_x"])
            current_window.move(x, cursor_y)
            cursor_y += height + gap
        return False

    GLib.idle_add(arrange_new_windows)
    if toolbar:
        toolbar.show_all()
    Gtk.main()
    active_pid_file.unlink(missing_ok=True)


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "start"
    if command == "configure":
        window = SettingsWindow(load_config())
        window.show_all()
        Gtk.main()
    elif command == "stop":
        stop_running()
        stop_editor()
    elif command == "restart":
        stop_running()
        stop_editor()
        subprocess.Popen([sys.executable, __file__, "start"], start_new_session=True)
    elif command in ("hide", "show"):
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, signal.SIGUSR1 if command == "hide" else signal.SIGUSR2)
        except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError):
            pass
    elif command == "edit":
        run_widgets(edit_mode=True)
        subprocess.Popen([sys.executable, __file__, "start"], start_new_session=True)
    else:
        run_widgets()


if __name__ == "__main__":
    main()

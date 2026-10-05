# Antonio Sarosi
# https://youtube.com/c/antoniosarosi
# https://github.com/antoniosarosi/dotfiles

from libqtile import layout
from libqtile.config import Match
from .theme import colors

# Layouts and layout rules


layout_conf = {
    'border_focus': colors['color4'][0],
    'border_normal': "#202124",
    'border_width': 0,
    'margin': 10


}

layouts = [
    #layout.Max(),
    layout.MonadTall(**layout_conf),
    layout.MonadWide(**layout_conf),
    layout.Bsp(**layout_conf),
    layout.Matrix(columns=2, **layout_conf),
    layout.RatioTile(**layout_conf),
    layout.Columns(border_width=0),
    layout.Tile(border_width=0),
    layout.TreeTab(border_width=0),
    layout.VerticalTile(border_width=0),
    layout.Zoomy(border_width=0),
]

floating_layout = layout.Floating(
    float_rules=[
        *layout.Floating.default_float_rules,
        Match(wm_class='confirmreset'),
        Match(wm_class='makebranch'),
        Match(wm_class='maketag'),
        Match(wm_class='ssh-askpass'),
        Match(title='branchdialog'),
        Match(title='pinentry'),
        Match(wm_class='MacWidgets'),
    ],
    border_focus=colors["color3"][0],
    border_width=0,
)

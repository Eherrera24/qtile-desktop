from qtile_extras import widget
from .theme import colors
from qtile_extras.widget.decorations import RectDecoration
from libqtile.lazy import lazy

# Get the icons at https://www.nerdfonts.com/cheat-sheet (you need a Nerd Font)

THEME_ATTRIBUTES = (
    'background', 'foreground', 'active', 'inactive', 'urgent_border',
    'this_current_screen_border', 'this_screen_border',
    'other_current_screen_border', 'other_screen_border',
    'colour_have_updates', 'colour_no_updates',
)


def _same_colour(value, palette_value):
    if value == palette_value:
        return True
    if isinstance(palette_value, list) and palette_value:
        return value == palette_value[0]
    return False


def register_theme_roles(w):
    """Registra qué entrada de la paleta controla cada color del widget."""
    roles = dict(getattr(w, 'workspace_color_roles', {}))
    for attribute in THEME_ATTRIBUTES:
        if not hasattr(w, attribute) or attribute in roles:
            continue
        value = getattr(w, attribute)
        for role, palette_value in colors.items():
            if _same_colour(value, palette_value):
                roles[attribute] = role
                break
    w.workspace_color_roles = roles
    return w

def borde(w):
    w.decorations = [
        RectDecoration(
            line_colour="#000000",
            filled=False,
            radius=10,
            line_width=0,
            group=True,   
        )
    ]
    return register_theme_roles(w)


def workspace_background(w, role):
    """Guarda el rol para que el tema dinámico no dependa del color anterior."""
    register_theme_roles(w)
    w.workspace_color_roles['background'] = role
    return w


def workspace_roles(w, **roles):
    """Asigna roles explícitos a piezas pequeñas como los powerlines."""
    register_theme_roles(w)
    w.workspace_color_roles.update(roles)
    return w

def base(fg='text', bg='dark'): 
    return {
        'foreground': colors[fg],
        'background': colors[bg]
    }


def separator():
    return borde(workspace_roles(
        widget.Sep(**base(), linewidth=0, padding=5),
        foreground='text', background='dark',
    ))


def icon(fg='text', bg='dark', fontsize=24, text="?"):
    return workspace_roles(widget.TextBox(
        **base(fg, bg),
        fontsize=fontsize,
        text=text,
        padding=3
    ), foreground=fg, background=bg)


def powerline(fg="light", bg="dark"):
    return workspace_roles(widget.TextBox(
        **base(fg, bg),
        text="", # Icon: nf-oct-triangle_left
        fontsize=46,
        padding=-2
    ), foreground=fg, background=bg)


def workspaces(): 
    return [
        separator(),
        borde(workspace_roles(widget.GroupBox(
            **base(fg='light'),
            font='UbuntuMono Nerd Font',
            fontsize=24,
            margin_y=3,
            margin_x=3,
            padding_y=2,
            padding_x=2,
            borderwidth=1,
            active=colors['active'],
            inactive=colors['inactive'],
            rounded=True,
            highlight_method='block',
            urgent_alert_method='block',
            urgent_border=colors['urgent'],
            this_current_screen_border=colors['color1'],
            this_screen_border=colors['grey'],
            other_current_screen_border=colors['dark'],
            other_screen_border=colors['dark'],
            disable_drag=True
#	    decorations=[
#            RectDecoration(
#            colour=colors['text'],  # borde
#            filled=False,           # solo borde
#            radius=10,              
#            line_width=2
#                )
#            ],
	), foreground='light', background='dark', active='active',
            inactive='inactive', urgent_border='urgent',
            this_current_screen_border='color1', this_screen_border='grey',
            other_current_screen_border='dark', other_screen_border='dark')),
	
        separator(),
        borde(widget.WindowName(**base(fg='focus'), fontsize=14, padding=5)),
        separator(),
    ]


primary_widgets = [
    *workspaces(),

    separator(),

    borde(powerline('color4', 'dark')),

    borde(icon(bg="color4", text='  ')), # Icon: nf-fa-download
    
    borde(workspace_roles(widget.CheckUpdates(
        background=colors['color4'],
        colour_have_updates=colors['text'],
        colour_no_updates=colors['text'],
        no_update_string='0',
        display_format='{updates}',
        update_interval=1800,
        custom_command='checkupdates',
    ), background='color4', colour_have_updates='text', colour_no_updates='text')),

    borde(powerline('color3', 'color4')),

    borde(icon(bg="color3", text='  ')),  # Icon: nf-fa-feed
    
    borde(workspace_background(widget.Net(
        **base(bg='color3'),
        interface='wlan0',
        mouse_callbacks={
            'Button1': lazy.spawn('wifi-menu'),
        },
    ), 'color3')),

    borde(workspace_background(widget.TextBox(
        **base(bg='color3'),
        font='Hack Nerd Font',
        fontsize=24,
        padding=5,
        text='󰂯',
        mouse_callbacks={
            'Button1': lazy.spawn('bluetooth-menu'),
        },
    ), 'color3')),

    borde(powerline('color2', 'color3')),

    borde(icon(bg='color2', fontsize=24, text=' ')),

#    widget.CurrentLayoutIcon(**base(bg='color2'), padding=5),

    borde(workspace_background(
        widget.CurrentLayout(**base(bg='color2'), fontsize=24, padding=5),
        'color2',
    )),

    borde(powerline('color1', 'color2')),

    borde(icon(bg="color1", fontsize=24, text='   ')), # Icon: nf-mdi-calendar_clock

    borde(workspace_background(
        widget.Clock(**base(bg='color1'), fontsize=24, format='%d/%m/%Y - %H:%M '),
        'color1',
    )),

    borde(powerline('color5', 'color1')),

    borde(workspace_background(widget.TextBox(
        **base(bg='color5'),
        padding=2,
        text=' ',
    ), 'color5')),

    borde(workspace_background(widget.Volume(
        **base(bg='color5'),
        fontsize=24,
        padding=5,
        get_volume_command="/usr/bin/fish -c 'printf \"%s%%\\n\" (volume get)'",
        check_mute_command="/usr/bin/wpctl get-volume @DEFAULT_AUDIO_SINK@ | /usr/bin/awk '{print ($0 ~ /\\[MUTED\\]/) ? \"muted\" : \"active\"}'",
        check_mute_string="muted",
        unmute_format="VOL {volume}%",
        mute_format="MUTE {volume}%",
        update_interval=0.1,
        volume_up_command="/usr/bin/fish -c 'volume +5'",
        volume_down_command="/usr/bin/fish -c 'volume -5'",
        mute_command="/usr/bin/fish -c 'volume toggle'",
    ), 'color5')),

    borde(workspace_background(widget.TextBox(
        **base(bg='color5'),
        fontsize=24,
        padding=0,
        text='',
    ), 'color5')),

#    widget.Systray(background=colors['color5'], padding=5),
#    widget.Battery(background=colors['color5'], padding=5, format='{percent:2.0%}'),
    borde(workspace_background(
        widget.Battery(**base(bg='color5'), fontsize=24, padding=5, format='  {percent:2.0%} ', rounded=True, show_short_text=False),
        'color5',
    ))
]

secondary_widgets = [
    *workspaces(),

    separator(),

    register_theme_roles(powerline('color1', 'dark')),

#    widget.CurrentLayoutIcon(**base(bg='color1'), scale=0.65),

    workspace_background(widget.CurrentLayout(**base(bg='color1'), padding=5), 'color1'),

    register_theme_roles(powerline('color2', 'color1')),

    workspace_background(widget.Clock(**base(bg='color2'), format='%d/%m/%Y - %H:%M '), 'color2'),

    register_theme_roles(powerline('dark', 'color2')),
]

widget_defaults = {
    'font': 'UbuntuMono Nerd Font Bold',
    'fontsize': 14,
    'padding': 5,
}
extension_defaults = widget_defaults.copy()

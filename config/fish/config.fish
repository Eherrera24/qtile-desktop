# Tema de colores pastel masculinos elegantes
set -U fish_color_normal normal
set -U fish_color_command 5D8AA8       # Air Force blue - azul aeronáutico
set -U fish_color_param D4AF37         # Metallic gold - oro metálico
set -U fish_color_redirection 954535   # Chestnut - castaño
set -U fish_color_comment 00d787       # Moss green - verde musgo
set -U fish_color_error B5651D         # Light brown - marrón claro
set -U fish_color_escape 6F4E37        # Coffee - café
set -U fish_color_operator 5F9EA0      # Cadet blue - azul cadete
set -U fish_color_end 4A646C           # Deep space sparkle - azul espacial
set -U fish_color_quote 9C7C38         # Metallic bronze - bronce metálico
set -U fish_color_autosuggestion 848482 # Battleship gray - gris acorazado
set -U fish_color_user 007BA7          # Cerulean - cerúleo
set -U fish_color_host 6D9DC3          # Blue-gray - azul grisáceo
set -U fish_color_valid_path A67B5B    # French beige - beige francés
set -U fish_color_selection white --background=5D8AA8

# Puntero del prompt (cursor)
set -U fish_color_cwd 5F9EA0           # Cadet blue - azul cadete
set -U fish_color_cwd_root B5651D      # Light brown - marrón claro

# Colores para pwd y git
set -U fish_pager_color_prefix normal --underline
set -U fish_pager_color_completion 8A9A5B # Moss green - verde musgo
set -U fish_pager_color_description 555 D4AF37 # Oro metálico
set -U fish_pager_color_progress brwhite --background=5F9EA0

# Prompt personalizado elegante
function fish_prompt
    set -l last_status $status
    set -l steel_blue (set_color -o 5D8AA8)
    set -l metallic_gold (set_color -o D4AF37)
    set -l chestnut (set_color -o 954535)
    set -l cadet_blue (set_color -o 5F9EA0)
    set -l moss_green (set_color -o 00d787)
    set -l bronze (set_color -o 9C7C38)
    set -l normal (set_color normal)

    # Usuario y host
    echo -n -s $bronze (whoami) $normal @ $moss_green (prompt_hostname) $normal " "

    # Directorio actual
    echo -n -s $cadet_blue (prompt_pwd) $normal

    # Git status (si existe)
    if type -q git
        set -l git_branch (git branch 2>/dev/null | grep \* | sed 's/* //')
        if test -n "$git_branch"
            set -l git_status (git status --porcelain 2>/dev/null)
            if test -z "$git_status"
                echo -n -s $normal " on " $moss_green " $git_branch" $normal
            else
                echo -n -s $normal " on " $metallic_gold " $git_branch" $normal
            end
        end
    end

    # Indicador de root
    if fish_is_root_user
        echo -n -s $chestnut ' # ' $normal
    else
        echo -n -s $steel_blue ' ❯ ' $normal
    end
end

# Configuración adicional
#set -g fish_greeting (fastfetch --logo ascii --logo-width 15 --structure "OS:Kernel:Uptime:CPU:Memory" --separator " | " --color cyan --disable line-break)

#function fish_greeting; fastfetch --logo ascii --logo-width 6 --structure "OS:Kernel:Uptime:CPU:Memory" --separator " | " --color cyan; end

#function fish_greeting; fastfetch --logo type-7 --logo-width 15 --structure "OS:Kernel:Uptime:CPU:Memory" --separator " | " --color cyan; end


function fish_greeting
    set_color cyan
    echo -n "  OS:       "| 
    set_color normal
    echo (fastfetch --logo none --pipe | grep "OS:" | cut -d: -f2- | xargs) | tte print \
    --final-gradient-stops 0088FF 00FFFF AA00FF
    echo "-----------------"    

    set_color green
    echo -n "  Kernel:   "
    set_color normal
    echo (fastfetch --logo none --pipe | grep "Kernel:" | cut -d: -f2- | xargs) 
    
#    set_color yellow
#    echo -n "󰔟  Uptime:   "
#    set_color normal
#    echo (fastfetch --logo none --pipe | grep "Uptime:" | cut -d: -f2- | xargs) | terminaltexteffects print
    
    set_color magenta
    echo -n "󰻠  CPU:      "
    set_color normal
    echo (fastfetch --logo none --pipe | grep "CPU:" | cut -d: -f2- | xargs | cut -d' ' -f1-3)
    
    set_color red
    echo -n "󰍛  Memory:   "
    set_color normal
    echo (fastfetch --logo none --pipe | grep "Memory:" | cut -d: -f2- | xargs)
    echo ""
end

# Aliases con colores
alias ls "lsd -l --blocks=permission,size,date,name --date='+%b %d'"
alias grep "grep --color=auto"
alias egrep "egrep --color=auto"
alias fgrep "fgrep --color=auto"

# Mejor autocompletado
set -g fish_autosuggestion_enabled 1
set -g fish_autosuggestion_color 848482

# Historial
set -g fish_history_limit 10000

# Aliases adicionales útiles
alias ..="cd .."
alias ...="cd ../.."
alias ll="ls -lh"
alias la="ls -lha"
alias ip="ip -color=auto"

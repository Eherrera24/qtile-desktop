function volume --description 'Control de volumen con PipeWire'
    if not type -q wpctl
        echo "Error: wpctl no está instalado." >&2
        return 1
    end

    if test (count $argv) -gt 1
        echo "Uso: volume [0-100|+N|-N|mute|unmute|toggle|max|min|get|device|devices]" >&2
        return 2
    end

    set -l sink '@DEFAULT_AUDIO_SINK@'
    set -l action $argv[1]

    switch "$action"
        case ''
            set -l state (wpctl get-volume $sink); or return 1
            set -l percent (math --scale=0 (string match -r '[0-9]+\.[0-9]+' -- $state)' * 100')
            set -l muted no
            string match -q '*[MUTED]*' -- $state; and set muted yes
            echo "Volumen: $percent%"
            echo "Mute: $muted"
        case get
            set -l state (wpctl get-volume $sink); or return 1
            echo (math --scale=0 (string match -r '[0-9]+\.[0-9]+' -- $state)' * 100')
        case mute
            wpctl set-mute $sink 1
        case unmute
            wpctl set-mute $sink 0
        case toggle
            wpctl set-mute $sink toggle
        case max
            wpctl set-volume -l 1 $sink 100%
        case min
            wpctl set-volume -l 1 $sink 0%
        case device
            set -l name (wpctl inspect $sink | string match -r 'node.description = ".*"' | string replace -r '^.* = "(.*)"$' '$1')
            test -n "$name"; and echo $name; or return 1
        case devices
            wpctl status --name | awk '/Sinks:/{show=1; next} /Sources:/{show=0} show && /[0-9]+\./{sub(/^.*[0-9]+\. /, ""); sub(/ \[vol:.*$/, ""); print}'
        case '*'
            if string match -qr '^[0-9]+$' -- $action
                if test $action -gt 100
                    echo "Error: el volumen debe estar entre 0 y 100." >&2
                    return 2
                end
                wpctl set-volume -l 1 $sink "$action%"
            else if string match -qr '^\+[0-9]+$' -- $action
                wpctl set-volume -l 1 $sink (string sub -s 2 -- $action)'%+'
            else if string match -qr '^-[0-9]+$' -- $action
                wpctl set-volume -l 1 $sink (string sub -s 2 -- $action)'%-'
            else
                echo "Uso: volume [0-100|+N|-N|mute|unmute|toggle|max|min|get|device|devices]" >&2
                return 2
            end
    end
end

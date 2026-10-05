#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
case "${1:-}" in
  --dry-run) DRY_RUN=true ;;
  "") ;;
  *) echo "Usage: $0 [--dry-run]" >&2; exit 2 ;;
esac

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
if [[ ! -r /etc/os-release ]] || ! grep -qx 'ID=arch' /etc/os-release; then
  echo "This installer supports Arch Linux only." >&2
  exit 1
fi

required=(qtile picom rofi kitty feh plank scrot xrandr xinput xwininfo xev)
missing=()
for command_name in "${required[@]}"; do
  command -v "$command_name" >/dev/null 2>&1 || missing+=("$command_name")
done

timestamp=$(date +%Y%m%d-%H%M%S)
backup_root="$HOME/.local/state/qtile-desktop/backups/$timestamp"
echo "Source: $ROOT"
echo "Backup: $backup_root"
echo "Mode: $($DRY_RUN && echo dry-run || echo install)"
if ((${#missing[@]})); then
  printf 'Missing commands: %s\n' "${missing[*]}"
fi
echo "Targets: ~/.config/{qtile,picom,rofi,kitty,gtk-3.0,macwidgets} and selected ~/.local/bin scripts"

if $DRY_RUN; then
  echo "Dry run complete: no files or directories were changed."
  exit 0
fi

read -r -p "Continue and modify the listed user configuration paths? [y/N] " answer
[[ "$answer" =~ ^[Yy]$ ]] || { echo "Cancelled."; exit 0; }

mkdir -p "$backup_root" "$HOME/.config" "$HOME/.local/bin" "$HOME/.local/share/rofi/themes"

backup_and_copy() {
  local source=$1 destination=$2 relative=${2#"$HOME"/}
  if [[ -e "$destination" || -L "$destination" ]]; then
    mkdir -p "$backup_root/$(dirname -- "$relative")"
    mv -- "$destination" "$backup_root/$relative"
  fi
  mkdir -p "$(dirname -- "$destination")"
  cp -a -- "$source" "$destination"
}

for name in qtile picom rofi kitty gtk-3.0 macwidgets; do
  backup_and_copy "$ROOT/config/$name" "$HOME/.config/$name"
done
# Preserve local wallpaper assets when upgrading an existing installation.
if [[ -d "$backup_root/.config/qtile/workspace-wallpapers" ]]; then
  cp -a -- "$backup_root/.config/qtile/workspace-wallpapers" "$HOME/.config/qtile/"
fi
backup_and_copy "$ROOT/themes/rofi/squared-nord.rasi" "$HOME/.local/share/rofi/themes/squared-nord.rasi"

installed_scripts=()
for item in \
  scripts/wallpapers/walltheme \
  scripts/utilities/animation-profile \
  scripts/utilities/bluetooth-menu \
  scripts/utilities/wifi-menu \
  scripts/utilities/desktop-profile \
  scripts/plank/plank-qtile \
  scripts/plank/plank-qtile-sync \
  scripts/qtile/macwidgets; do
  backup_and_copy "$ROOT/$item" "$HOME/.local/bin/$(basename -- "$item")"
  chmod 755 "$HOME/.local/bin/$(basename -- "$item")"
  installed_scripts+=("$HOME/.local/bin/$(basename -- "$item")")
done

# Port the audited absolute home path in the newly installed copies only.
find "$HOME/.config/qtile" "$HOME/.config/rofi" "$HOME/.config/picom" \
  "$HOME/.config/kitty" "$HOME/.config/macwidgets" \
  -maxdepth 8 -type f -exec sed -i "s|/home/esteban|$HOME|g" {} +
sed -i "s|/home/esteban|$HOME|g" "${installed_scripts[@]}"

echo "Installed. Backup retained at: $backup_root"
echo "Run: qtile check -c $HOME/.config/qtile/config.py"

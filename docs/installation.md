# Installation

Review the repository and package lists first. On Arch, install official
dependencies, then install `qtile-extras==0.35.0` for the user and an AUR Plank
Reloaded package using your preferred audited AUR workflow.

```bash
sed '/^#/d;/^$/d' packages/pacman.txt | sudo pacman -S --needed -
python -m pip install --user 'qtile-extras==0.35.0'
./install/install.sh --dry-run
./install/install.sh
```

The installer is interactive by default, refuses non-Arch systems, shows its
plan, verifies commands, backs up every destination under a timestamped
directory and only then copies files. It never deletes the backup. Wallpapers
must be supplied separately with publishable files named as documented.

LightDM is intentionally not modified: changing `/etc` needs an explicit,
machine-specific administrative decision. Plank settings are also not imported
automatically because they reference application launchers that were excluded.

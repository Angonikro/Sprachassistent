#!/bin/bash

# ============================================================
# Sprachassistent – Desktop-Launcher
# Erstellt eine Desktop-Verknüpfung ohne Terminalfenster
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROGRAM="$SCRIPT_DIR/Sprachassistent_finale.py"

# Desktop-Ordner automatisch ermitteln
if command -v xdg-user-dir >/dev/null 2>&1; then
    DESKTOP_DIR="$(xdg-user-dir DESKTOP)"
fi

if [ -z "$DESKTOP_DIR" ] || [ "$DESKTOP_DIR" = "Desktop" ]; then
    DESKTOP_DIR="$HOME/Desktop"
fi

mkdir -p "$DESKTOP_DIR"

DESKTOP_FILE="$DESKTOP_DIR/Sprachassistent.desktop"
START_SCRIPT="$SCRIPT_DIR/start_sprachassistent.sh"

if [ ! -f "$PROGRAM" ]; then
    echo "FEHLER: $PROGRAM wurde nicht gefunden."
    echo "Die Dateien müssen im gleichen Ordner liegen."
    exit 1
fi

# Startskript:
# - wechselt zuerst in den Programmordner
# - startet den Sprachassistenten
# - öffnet KEIN Terminal
# - schreibt eventuelle Fehlermeldungen in eine Logdatei
cat > "$START_SCRIPT" <<EOF
#!/bin/bash
cd "$SCRIPT_DIR"
exec python3 "$PROGRAM" >> "$SCRIPT_DIR/sprachassistent.log" 2>&1
EOF

chmod +x "$START_SCRIPT"

# Eigenes einfaches SVG-Icon
ICON_FILE="$SCRIPT_DIR/sprachassistent.svg"

cat > "$ICON_FILE" <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#263b73"/>
      <stop offset="1" stop-color="#101827"/>
    </linearGradient>
    <linearGradient id="mic" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#61dafb"/>
      <stop offset="1" stop-color="#20b8a6"/>
    </linearGradient>
  </defs>
  <rect x="8" y="8" width="240" height="240" rx="52" fill="url(#bg)"/>
  <rect x="88" y="48" width="80" height="124" rx="40" fill="url(#mic)"/>
  <path d="M64 120c0 43 29 72 64 72s64-29 64-72" fill="none" stroke="#ffffff" stroke-width="14" stroke-linecap="round"/>
  <path d="M128 192v28M92 220h72" fill="none" stroke="#ffffff" stroke-width="14" stroke-linecap="round"/>
  <path d="M48 104c-8 6-13 15-13 25M208 104c8 6 13 15 13 25" fill="none" stroke="#61dafb" stroke-width="9" stroke-linecap="round"/>
</svg>
EOF

# Desktop-Datei erstellen
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Sprachassistent
Comment=Sprachassistent starten
Exec=$START_SCRIPT
Path=$SCRIPT_DIR
Icon=$ICON_FILE
Terminal=false
StartupNotify=true
Categories=Utility;AudioVideo;
EOF

chmod +x "$DESKTOP_FILE"

# GNOME/Nautilus: Desktop-Datei als vertrauenswürdig markieren
if command -v gio >/dev/null 2>&1; then
    gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true
fi

# KDE: Desktop-Datei ausführbar machen reicht normalerweise aus.
# Aktualisierung der Desktop-Datenbank, falls vorhanden.
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi

echo
echo "=============================================="
echo " Sprachassistent-Launcher erfolgreich erstellt"
echo "=============================================="
echo
echo "Desktop: $DESKTOP_FILE"
echo "Programm: $PROGRAM"
echo
echo "Der Launcher startet den Sprachassistenten"
echo "OHNE ein Terminalfenster zu öffnen."
echo

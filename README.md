# Sprachassistent v5.3

Deutschsprachiger Sprachassistent von Goldisoft.

## Funktionen
- Sprachsteuerung und Sprachausgabe
- Chat-/Antwortfenster und gespeicherte Fragen/Antworten
- Websuche
- Terminplaner und Erinnerungen
- Windows-Sprachausgabe über den Windows-Soundtreiber
- Weitere Funktionen des Sprachassistenten

## Installation unter Debian 13 / Raspberry Pi
Die Anwendung benötigt die in `requirements.txt` aufgeführten Python-Pakete sowie die auf dem jeweiligen System benötigten Audio-/Sprachkomponenten.

Zum Start aus dem Quellcode:

```bash
python3 -m pip install -r requirements.txt
python3 Sprachassistent.py
```

Der Desktop-Starter kann mit `install_desktop_launcher.sh` eingerichtet werden.

## Persönliche Speicherorte
- **Gespeicherte Fragen und Antworten:** `~/.local/share/Sprachassistent/fragen_antworten.db`
- **Erinnerungen und Termine:** `~/.local/share/Sprachassistent/erinnerungen.json`
- **Einstellungen:** `~/.config/Sprachassistent/config.ini`

Die Anwendung verwendet `XDG_DATA_HOME` bzw. `XDG_CONFIG_HOME`, falls diese Umgebungsvariablen gesetzt sind. Vorhandene Datenbank-, Einstellungs- und Erinnerungsdateien aus dem bisherigen Startverzeichnis werden übernommen, sofern am neuen Speicherort noch keine entsprechende Datei existiert. Persönliche Daten liegen damit getrennt vom Programmverzeichnis und bleiben bei Programmupdates erhalten.

## Manuelle Websuche
Über **„Websuche starten“** wird die manuelle Websuche gestartet. Der Assistent fragt nach dem Suchbegriff und verwendet die nächste gesprochene Eingabe als Suchfrage.

## Abhängigkeiten
Die Python-Abhängigkeiten sind in `requirements.txt` aufgeführt. Für die Sprach- und Audiofunktionen können zusätzlich Systempakete erforderlich sein; deren Verfügbarkeit hängt von Betriebssystem und Distribution ab.

**Version 5.3 – By Goldisoft 2026**

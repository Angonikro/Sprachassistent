import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import json
import threading
import datetime
import requests
import speech_recognition as sr
import subprocess
from rapidfuzz import fuzz
import random
import webbrowser
import time
import os
import configparser

try:
    import cv2
except ImportError:
    cv2 = None
import shutil
import queue
import urllib.parse
import re
from pathlib import Path


# ============================================================
# RECHTSCHREIBPRÜFUNG
# ============================================================


# ============================================================
# KONFIGURATION
# ============================================================

DB_FILE = "fragen_antworten.db"
CONFIG_MAIN = "config.ini"



SPEAKING = False

# Sperrt die Spracherkennung, sobald TTS ansteht oder läuft.
SPEECH_BLOCK_LISTENING = threading.Event()
SPEECH_SHUTDOWN = threading.Event()
SPEECH_THREAD = None
SPEECH_PROCESS = None
APP_INSTANCE = None

HELP_TEXT = """
SPRACHASSISTENT – VOLLSTÄNDIGE ANLEITUNG

Diese Anleitung beschreibt den aktuellen Funktionsstand inklusive
Sprachsteuerung, Sprachansagen, Terminplaner, Gesichtsfunktionen,
Musik/Radio, Fragen & Antworten, Backups, Autoplay und Einstellungen.

1. MIKROFON / AUFNAHME
• STARTEN – Sprachaufnahme starten.
• STOPP – Sprachaufnahme stoppen.
• Während einer Sprachansage wird nicht gleichzeitig aufgenommen.
• Nach einer Ansage wird der vorherige Mikrofonzustand berücksichtigt.

2. UHRZEIT
Befehle:
• „Uhrzeit“
• „Wie spät ist es?“
• „Wie ist die Zeit?“
Ansage: „Es ist HH:MM:SS.“

3. DATUM
Befehle:
• „Datum“
• „Welches Datum haben wir?“
Ansage: „Heute ist der TT.MM.JJJJ.“

4. WOCHENTAG
Befehle:
• „Wochentag“
• „Welcher Tag ist heute?“
Ansage: „Heute ist [Wochentag].“

5. WETTER
Befehle:
• „Wetter“
• „Wie ist das Wetter?“
Der Assistent lädt aktuelle Wetterdaten und gibt sie per Sprache aus.
Zusätzlich ist eine automatische Wetteransage jede halbe Stunde möglich.

6. LOTTO 6aus49
Befehle:
• „Lotto“
• „Lottozahlen“
• „Lotto Zahlen“
• „Gewinnzahlen“
• „Lottoergebnisse“
• „Lotto Ergebnisse“
• „6 aus 49“
• „6 von 49“
• „Sechs aus neunundvierzig“
Bei erfolgreicher Online-Abfrage werden Ziehungsdatum, sechs Gewinnzahlen
und Superzahl angesagt. Bei einem Fehler werden keine erfundenen Zahlen
ausgegeben.

7. BROWSER
Befehl:
• „Öffne Browser“
Ansage: „Ich öffne deinen Browser.“
Danach wird Google geöffnet.

8. WEBSEITEN
Beispiele:
• „Öffne www.google.de“
• „Öffne google.de“
• „Öffne eine Seite www.example.de“
• „Öffne example.com“
Unterstützt werden .de, .com, .net und .org sowie „www.“.
Ansage: „Ich öffne [Adresse].“
Wenn keine Adresse erkannt wird: „Welche Seite soll ich öffnen?“

9. YOUTUBE
Beispiele:
• „YouTube“
• „Spiele Musik auf YouTube“
• „Spiele [Titel] auf YouTube“
• „Suche [Begriff] auf YouTube“
• „Öffne YouTube“
Mit Suchbegriff: „Ich suche [Suchbegriff] auf YouTube.“
Ohne Suchbegriff: „Was soll ich auf YouTube suchen?“

10. YOUTUBE MUSIC
Befehle:
• „YouTube Musik“
• „YouTube Music“
Ansage: „Ich öffne YouTube Musik.“

11. LOKALE MUSIK
Befehle:
• „Spiele Musik“
• „Spiele Lied“
• „Spiele Song“
• „Spiele [Titel]“
• „Spiele das Lied [Titel]“
Der Assistent sucht im eingestellten Musikordner. Ohne Titel wird lokale
Musik gestartet.

12. INTERNETRADIO
Befehle:
• „Radio“
• „Internetradio“
Ansage: „Ich starte dein Radio.“

13. PROGRAMME
Befehle:
• „Öffne [Programmname]“
• „Starte [Programmname]“
Programme müssen vorher in „Programme“ gespeichert werden.
Bei unbekanntem Programm: „Ich kenne dieses Programm noch nicht.“

14. FRAGEN & ANTWORTEN
• Gespeicherte Fragen können normal gestellt werden.
• Exakte Treffer verwenden die gespeicherte Antwort.
• Ähnliche Fragen können ebenfalls erkannt werden.
• Mehrere Antworten können vorhanden sein; eine wird ausgewählt.
• Neue Fragen/Antworten können gespeichert, bearbeitet und gelöscht werden.
• Wenn keine lokale Antwort gefunden wird, kann die automatische Websuche
  als Fallback verwendet werden.

14a. MANUELLE WEBSUCHE
Startbefehle:
• „Websuche“
• „Websuche starten“
• „Web Suche starten“
• „Starte Websuche“

Nach dem Start sagt der Assistent:
„Was möchtest du suchen?“

Danach wird deine nächste gesprochene Eingabe als vollständige Suchfrage
verwendet. Die manuelle Websuche sucht nach einer möglichst direkten Antwort
auf genau diese Frage.

• Wenn ein Satz die Frage vollständig beantwortet, wird nur dieser eine Satz
  ausgegeben und vorgelesen.
• Wenn ein einzelner Satz nicht ausreicht, können bis zu drei passende Sätze
  verwendet werden.
• Die Antwort kann anschließend im Antwortfenster gespeichert werden.
• Die normale automatische Websuche bleibt davon getrennt und unverändert.

Beispiel:
„Websuche starten“
→ „Was möchtest du suchen?“
→ „Wie alt ist Bad Driburg?“
→ kurze, direkte Antwort zur gestellten Frage.

15. TERMINPLANER / ERINNERUNGEN
Startbefehle:
• „Termin“
• „Terminplan“
• „Terminplaner“
• „Termin planer“
• „Erinnerungsplaner“

Nach dem Start sagt der Assistent:
„Für welches Datum soll ich dich erinnern?“

Datumsangaben werden unter anderem erkannt als:
• „heute“
• „morgen“
• „übermorgen“
• „02.09.2026“
• „2. September 2026“

Danach fragt der Assistent nach der Uhrzeit.

Uhrzeiten werden unter anderem erkannt als:
• „4 Uhr“
• „vier Uhr“
• „18 Uhr“
• „18 Uhr 30“
• „18:30“
• „18.30“
• „1830“
• „400“
• „halb sieben“ und weitere erkannte „halb“-Formen

Danach sagt der Assistent:
„Und woran soll ich dich erinnern?“

Nach dem Anliegen erscheint die Bestätigung und der Assistent sagt:
„Ich habe [heute/morgen] um HH:MM Uhr eingetragen: [Anliegen].
Ist alles richtig?“

Tasten:
• „JA – SPEICHERN“
• „ABBRECHEN“

Nach dem Speichern:
„Alles klar. Ich erinnere dich um HH:MM Uhr daran: [Anliegen].“

Beim Abbrechen:
„Der Termin wurde nicht gespeichert.“

Wenn der Termin fällig ist:
„Erinnerung: Du wolltest [Anliegen].“

Abbruch im Sprachmodus:
• „Abbrechen“
• „Abbruch“
• „Stopp“
• „Stop“
• „Cancel“
• „Vergiss es“
• „Doch nicht“
Ansage: „Terminplanung abgebrochen.“

16. TERMINVERWALTUNG
Die Terminverwaltung bietet:
• Termin hinzufügen
• Termin bearbeiten
• Termin löschen
• Termine anzeigen
• „ANZEIGEN AN/AUS“
• alte/erledigte Termine reaktivieren

Abgelaufene Termine werden NICHT automatisch gelöscht.
Sie bleiben in der Terminverwaltung erhalten.

Status:
• AKTIV – zukünftiger aktiver Termin
• AUS – Termin deaktiviert
• ABGELAUFEN – Zeitpunkt liegt zurück
• ERLEDIGT – Erinnerung wurde bereits angesagt

Ein alter oder erledigter Termin kann mit „ANZEIGEN AN/AUS“ mit EINEM Klick
wieder aktiviert werden. Dabei wird die nächste passende Uhrzeit verwendet.
Beim Bearbeiten kann ebenfalls das Häkchen
„Termin anzeigen / Erinnerung aktiv (alte Termine reaktivieren)“
gesetzt werden.

17. DASHBOARD-GLOCKE
• Die Glocke erscheint nur bei einem zukünftigen angezeigten Termin.
• Klick auf die Glocke öffnet die Terminverwaltung.
• Ausgeblendete Termine lösen keine Glocke aus.

18. AUTOPLAY
Unter „Autoplay“:
• „Uhrzeit jede volle Stunde“
• „Wetter jede halbe Stunde“
• „Auto-Fragen“
Auto-Fragen-Intervall:
• 5, 6, 7, 8, 9 oder 10 Minuten
• „Aus“

19. AUDIO / STIMME
Unter „Audio / Stimme“:
• MBROLA-Stimme
• Geschwindigkeit
• Tonhöhe
• Lautstärke
Verfügbare Stimmen in der Oberfläche: mb-de1 bis mb-de8.
Testansage:
„Dies ist ein Test der aktuellen Stimme.“

20. SOUND-TREIBER
Unter „Einstellungen → Sound-Treiber“:
• pulse
• alsa
• sdl
• oss
• jack
• portaudio
Nach dem Speichern wird das Audio-System neu gestartet.

21. MUSIKORDNER
Auf der Musik-Seite:
• Ordner auswählen
• Musik starten
• Titel suchen
Der Musikpfad wird gespeichert.

22. GESICHT SPEICHERN / FOTO
Befehle:
• „Merk dir mein Gesicht“
• „Merke dir mein Gesicht“
• „Mein Gesicht merken“
• „Mach ein Foto von mir“
• „Mach ein Bild von mir“
• „Fotografiere mich“
• „Nimm ein Foto von mir auf“
• „Nimm ein Bild von mir auf“

Typische Ansagen:
• „Wie heißt du?“
• „Okay, ich speichere kein Gesicht.“
• „Der Name ist nicht gültig.“
• „Bitte schaue für [Name] in die Kamera.“
• „Alles klar. Ich merke mir dein Gesicht als [Name].“

23. GESICHT ERKENNEN
Befehle:
• „Wer bin ich?“
• „Weißt du, wer ich bin?“
• „Weißt du wer ich bin?“
• „Weisst du wer ich bin?“

Typische Ansagen:
• „Ich habe noch kein gespeichertes Gesicht.“
• „Ja. Du bist [Name].“
• „Ich erkenne dich nicht in meinen gespeicherten Gesichtern.“

24. GESICHTER VERWALTEN
Unter „Einstellungen → Gesichtserkennung verwalten“:
• gespeicherte Personen anzeigen
• Bildvorschau
• Person hinzufügen
• Foto ersetzen
• Name ändern
• Löschen
• Aktualisieren

Beim Löschen gibt es eine Sicherheitsabfrage.

25. KAMERA
Unter „Kamera“ kann die erkannte Kamera ausgewählt werden.
Die Auswahl wird gespeichert und für die Gesichtsfunktionen verwendet.

26. MIKROFON NACH GESICHTSFUNKTIONEN
Während Fotoaufnahme und Gesichtserkennung wird das normale Zuhören
vorübergehend pausiert. Danach wird es abhängig vom Zustand vor der
Funktion wieder aufgenommen.

27. BACKUP-SYSTEM
Unter „Backup“ / „Backup-System“:
• Backup jetzt ausführen
• Backup-Ordner öffnen
• Automatische Backups aktivieren/deaktivieren
• Backup-Namen ändern
• Backup wiederherstellen

Wiederherstellung:
1. Backup auswählen.
2. Wiederherstellung starten.
3. Sicherheitsabfrage bestätigen.
4. Backup wird geprüft.
5. Aktueller Stand wird vorher als Sicherheits-Backup gesichert.
6. Gewähltes Backup wird wiederhergestellt.
7. Fragen-/Antwortdaten werden neu geladen.

28. DATENBANK EXPORT / IMPORT
Unter „Datei“:
• Datenbank exportieren
• Datenbank importieren
• Beenden

29. THEMES / OBERFLÄCHE
Unter „Theme“:
• Dunkel
• Hell
• Gruvbox

Die Navigation und Oberfläche werden an das gewählte Theme angepasst.

30. NAVIGATION
Die Hauptnavigation enthält:
• Dashboard
• Fragen & Antworten
• Musik
• Termine
• Backup
• Einstellungen
• Programme
• Hilfe

Der aktuell gewählte Bereich wird in der Navigation hervorgehoben.

31. HILFE
Über „Hilfe → Anleitung anzeigen“ wird diese Anleitung direkt im Programm
geöffnet. Die PDF-Anleitung und die integrierte Hilfe beschreiben denselben
Funktionsstand.

32. WICHTIGE KURZBEFEHLE
• „Uhrzeit“
• „Datum“
• „Wochentag“
• „Wetter“
• „Lottozahlen“
• „Öffne Browser“
• „Öffne google.de“
• „YouTube“
• „YouTube Musik“
• „Spiele Musik“
• „Spiele [Titel]“
• „Radio“
• „Internetradio“
• „Öffne [Programmname]“
• „Starte [Programmname]“
• „Termin“
• „Terminplan“
• „Terminplaner“
• „Wer bin ich?“
• „Merk dir mein Gesicht“

33. TERMINPLANER – KOMPLETTES BEISPIEL
Benutzer: „Termin“
Assistent: „Wann soll ich dich erinnern?“
Benutzer: „4 Uhr“
Assistent: „Und woran soll ich dich erinnern?“
Benutzer: „An meinen Arzttermin.“
Assistent: „Ich habe heute um 04:00 Uhr eingetragen: An meinen Arzttermin.
Ist alles richtig?“
Benutzer drückt „JA – SPEICHERN“
Assistent: „Alles klar. Ich erinnere dich um 04:00 Uhr daran:
An meinen Arzttermin.“
Zur Fälligkeit:
„Erinnerung: Du wolltest An meinen Arzttermin.“

34. WICHTIGE HINWEISE
• Termine werden nicht gelöscht, nur weil ihre Uhrzeit vorbei ist.
• Eine Erinnerung wird nach ihrer Ansage als erledigt markiert.
• Ausgeblendete Termine bleiben gespeichert.
• Alte Termine können wieder aktiviert werden.
• Die Glocke zeigt nur zukünftige angezeigte Termine.
• Nur „LÖSCHEN“ entfernt einen Termin wirklich.
• Lotto- und Wetterwerte werden nicht erfunden, wenn die Online-Abfrage
  fehlschlägt.
"""


# ============================================================
# THEMES
# ============================================================

THEME_DARK = {
    "bg": "#282828",
    "bg2": "#1d2021",
    "fg": "#ebdbb2",
    "accent": "#3c3836",
    "hover": "#504945",
    "border": "#3b4252",
    "muted": "#8b93a7",
    "selected": "#30384a",
    "green": "#3fb950"
}

THEME_LIGHT = {
    "bg": "#f2f2f2",
    "bg2": "#ffffff",
    "fg": "#000000",
    "accent": "#d0d0d0",
    "hover": "#b0b0b0",
    "border": "#d5d9e2",
    "muted": "#68707d",
    "selected": "#e7ebf2",
    "green": "#18794e"
}

# Eigener Verweis auf Dark Theme
THEME_GRUVBOX = THEME_DARK

current_theme = THEME_DARK


def set_theme_by_name(name):
    global current_theme

    if name == "dark":
        current_theme = THEME_DARK
    elif name == "light":
        current_theme = THEME_LIGHT
    elif name == "gruvbox":
        current_theme = THEME_GRUVBOX


def apply_theme(root, style, widgets):
    th = current_theme

    root.configure(bg=th["bg"])

    style.configure(
        "TFrame",
        background=th["bg"]
    )

    style.configure(
        "TLabel",
        background=th["bg"],
        foreground=th["fg"]
    )

    style.configure(
        "TButton",
        background=th["accent"],
        foreground=th["fg"],
        padding=6
    )

    style.map(
        "TButton",
        background=[("active", th["hover"])],
        foreground=[("active", th["fg"])]
    )

    style.configure(
        "TRadiobutton",
        background=th["bg"],
        foreground=th["fg"]
    )

    style.configure(
        "TCheckbutton",
        background=th["bg"],
        foreground=th["fg"]
    )

    style.configure(
        "TCombobox",
        fieldbackground=th["bg2"],
        background=th["accent"],
        foreground=th["fg"]
    )

    root.option_add("*Menu.background", th["bg"])
    root.option_add("*Menu.foreground", th["fg"])
    root.option_add("*Menu.activeBackground", th["hover"])
    root.option_add("*Menu.activeForeground", th["fg"])

    for w in widgets:
        try:
            if isinstance(w, tk.Text):
                w.configure(
                    bg=th["bg2"],
                    fg=th["fg"],
                    insertbackground=th["fg"],
                    highlightbackground=th["border"]
                )

            elif isinstance(w, tk.Listbox):
                w.configure(
                    bg=th["bg2"],
                    fg=th["fg"],
                    selectbackground=th["hover"],
                    selectforeground=th["fg"],
                    highlightbackground=th["border"]
                )

            elif isinstance(w, tk.Canvas):
                w.configure(
                    bg=th["bg"]
                )
        except tk.TclError:
            pass


# ============================================================
# CONFIGURATION
# ============================================================

def load_main_config():
    config = configparser.ConfigParser()

    if not os.path.exists(CONFIG_MAIN):
        return {
            "hourly_time": False,
            "half_hour_weather": False,
            "interval": 0,
            "sound_driver": "pulse",
            "microphone_index": 0,
            "voice": "mb-de4",
            "speed": 165,
            "pitch": 45,
            "volume": 185,
            "programs": {},
            "auto_backup": True,
            "backup_name": "assistant",
        }

    try:
        config.read(CONFIG_MAIN)

        programs = (
            dict(config["programs"])
            if "programs" in config
            else {}
        )

        return {
            "hourly_time": config.getboolean(
                "autoplay",
                "hourly_time",
                fallback=False
            ),

            "half_hour_weather": config.getboolean(
                "autoplay",
                "half_hour_weather",
                fallback=False
            ),

            "interval": config.getint(
                "autoplay",
                "interval",
                fallback=0
            ),

            "sound_driver": config.get(
                "audio",
                "sound_driver",
                fallback="pulse"
            ),

            "microphone_index": config.getint(
                "audio",
                "microphone_index",
                fallback=0
            ),

            "voice": config.get(
                "audio",
                "voice",
                fallback="mb-de4"
            ),

            "speed": config.getint(
                "audio",
                "speed",
                fallback=165
            ),

            "pitch": config.getint(
                "audio",
                "pitch",
                fallback=45
            ),

            "volume": config.getint(
                "audio",
                "volume",
                fallback=185
            ),

            "programs": programs,

            "auto_backup": config.getboolean(
                "backup",
                "auto_backup",
                fallback=True
            ),

            "backup_name": config.get(
                "backup",
                "backup_name",
                fallback="assistant"
            ),

        }

    except Exception as e:
        print("Config-Fehler:", e)

        return {
            "hourly_time": False,
            "half_hour_weather": False,
            "interval": 0,
            "sound_driver": "pulse",
            "microphone_index": 0,
            "voice": "mb-de4",
            "speed": 165,
            "pitch": 45,
            "volume": 185,
            "programs": {},
            "auto_backup": True,
            "backup_name": "assistant",
        }


def save_main_config(
    hourly_time,
    half_hour_weather,
    interval,
    sound_driver,
    microphone_index,
    programs,
    voice,
    speed,
    pitch,
    volume,
    auto_backup,
    backup_name,
):
    config = configparser.ConfigParser()

    # Vorhandene Config laden, damit z. B. der Musikpfad
    # nicht versehentlich gelöscht wird.
    if os.path.exists(CONFIG_MAIN):
        try:
            config.read(CONFIG_MAIN)
        except Exception:
            pass

    config["autoplay"] = {
        "hourly_time": str(hourly_time).lower(),
        "half_hour_weather": str(half_hour_weather).lower(),
        "interval": str(interval)
    }

    config["audio"] = {
        "sound_driver": sound_driver,
        "microphone_index": str(microphone_index),
        "voice": voice,
        "speed": str(speed),
        "pitch": str(pitch),
        "volume": str(volume)
    }

    config["programs"] = programs

    config["backup"] = {
        "auto_backup": str(auto_backup).lower(),
        "backup_name": backup_name
    }


    try:
        with open(CONFIG_MAIN, "w", encoding="utf-8") as f:
            config.write(f)

    except Exception as e:
        print("Fehler beim Speichern der Config:", e)


def load_sound_driver():
    if not os.path.exists(CONFIG_MAIN):
        return "pulse"

    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_MAIN)

        return config.get(
            "audio",
            "sound_driver",
            fallback="pulse"
        )

    except Exception:
        return "pulse"


def save_sound_driver(driver):
    config = configparser.ConfigParser()

    if os.path.exists(CONFIG_MAIN):
        try:
            config.read(CONFIG_MAIN)
        except Exception:
            pass

    if "audio" not in config:
        config["audio"] = {}

    config["audio"]["sound_driver"] = driver

    try:
        with open(CONFIG_MAIN, "w", encoding="utf-8") as f:
            config.write(f)
    except Exception as e:
        print("Fehler beim Speichern des Sound-Treibers:", e)


def save_music_path(path):
    config = configparser.ConfigParser()

    if os.path.exists(CONFIG_MAIN):
        try:
            config.read(CONFIG_MAIN)
        except Exception:
            pass

    if "music" not in config:
        config["music"] = {}

    config["music"]["folder"] = path

    try:
        with open(CONFIG_MAIN, "w", encoding="utf-8") as f:
            config.write(f)
    except Exception as e:
        print("Fehler beim Speichern des Musikpfades:", e)


def load_music_path():
    if not os.path.exists(CONFIG_MAIN):
        return "/home/pi/Musik"

    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_MAIN)

        return config.get(
            "music",
            "folder",
            fallback="/home/pi/Musik"
        )

    except Exception:
        return "/home/pi/Musik"


# ============================================================
# SPRACHAUSGABE
# ============================================================

speech_queue = queue.Queue()

# Merkt den tatsächlichen Capture-Zustand vor einer TTS-Ansage.
# Dadurch wird ein vom Benutzer deaktiviertes Mikrofon nach der Ansage
# nicht versehentlich wieder aktiviert.
MIC_STATE_UNKNOWN = None

# Zustand vor dem Start von VLC. Wird beim Ende der Musik wiederhergestellt.
VLC_MIC_STATE_BEFORE_MUSIC = MIC_STATE_UNKNOWN


def get_system_mic_active():
    """Liest den aktuellen Capture-Zustand von ALSA/amixer aus."""
    try:
        result = subprocess.run(
            ["amixer", "get", "Capture"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False
        )
        output = result.stdout or ""
        # Typische ALSA-Ausgabe enthält z. B. [on] oder [off].
        states = re.findall(r"\[(on|off)\]", output, flags=re.IGNORECASE)
        if states:
            # Bei mehreren Kanälen gilt das Mikrofon als aktiv, wenn
            # mindestens ein Capture-Kanal aktiv ist.
            return any(state.lower() == "on" for state in states)
    except Exception as e:
        print("Mikrofonstatus konnte nicht gelesen werden:", e)
    return MIC_STATE_UNKNOWN


def mute_system_mic():
    try:
        subprocess.run(
            ["amixer", "set", "Capture", "nocap"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
    except Exception:
        pass


def unmute_system_mic():
    try:
        subprocess.run(
            ["amixer", "set", "Capture", "cap"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
    except Exception:
        pass


def restore_system_mic_state(active):
    """Stellt den Zustand wieder her, berücksichtigt dabei aber aktives VLC."""
    # Während VLC läuft, muss das Mikrofon unabhängig vom vorherigen Zustand
    # aus bleiben, damit Musik nicht als Sprache erkannt wird.
    if is_vlc_running():
        mute_system_mic()
        return

    if active is True:
        unmute_system_mic()
    elif active is False:
        mute_system_mic()
    else:
        # Wenn amixer den Zustand nicht zuverlässig lesen konnte, bleibt
        # das bisherige Verhalten erhalten: nach TTS wieder freigeben.
        unmute_system_mic()


def is_vlc_running():
    """Prüft unter Linux, ob aktuell ein VLC-Prozess läuft."""
    try:
        result = subprocess.run(
            ["pgrep", "-x", "vlc"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
        return result.returncode == 0
    except Exception:
        # Fallback, falls pgrep nicht verfügbar ist.
        try:
            result = subprocess.run(
                ["ps", "-eo", "comm="],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False
            )
            return any(line.strip().lower() == "vlc" for line in result.stdout.splitlines())
        except Exception:
            return False


def _restore_mic_after_vlc_stops():
    """Wartet bis VLC beendet ist und stellt den Zustand vor Musikstart wieder her."""
    global VLC_MIC_STATE_BEFORE_MUSIC

    while is_vlc_running() and not SPEECH_SHUTDOWN.is_set():
        time.sleep(0.5)

    if not SPEECH_SHUTDOWN.is_set():
        previous = VLC_MIC_STATE_BEFORE_MUSIC
        VLC_MIC_STATE_BEFORE_MUSIC = MIC_STATE_UNKNOWN
        restore_system_mic_state(previous)

        # War das Mikrofon vor dem Start von VLC aktiv, soll der
        # Sprachassistent nach dem Beenden der Musik wieder zuhören.
        # Erst warten, bis TTS und der alte Aufnahme-Thread fertig sind.
        if previous is True and APP_INSTANCE is not None:
            try:
                APP_INSTANCE.root.after(
                    200,
                    APP_INSTANCE._resume_listening_after_vlc
                )
            except Exception:
                pass
        if previous is True and APP_INSTANCE is not None:
            APP_INSTANCE._resume_after_vlc = True
            try:
                APP_INSTANCE.root.after(250, APP_INSTANCE._resume_listening_after_vlc)
            except Exception:
                pass



def start_vlc_with_mic_control(command):
    """Startet VLC, beendet vorher die Sprachaufnahme und stellt sie
    nach dem Ende von VLC nur dann wieder her, wenn sie vorher aktiv war."""
    global VLC_MIC_STATE_BEFORE_MUSIC

    # Entscheidend ist der Zustand des Assistenten, nicht nur [on]/[off]
    # von amixer. Während einer laufenden Aufnahme ist self.listening die
    # verlässlichste Information darüber, ob nach VLC weitergehört werden soll.
    was_listening = bool(APP_INSTANCE is not None and APP_INSTANCE.listening)
    previous = was_listening

    if not was_listening:
        mic_state = get_system_mic_active()
        previous = mic_state

    VLC_MIC_STATE_BEFORE_MUSIC = previous

    # Aufnahme sauber beenden, bevor VLC gestartet wird. Dadurch bleibt
    # kein alter SpeechRecognition-Thread im Zustand "VERARBEITE" hängen.
    if was_listening and APP_INSTANCE is not None:
        try:
            APP_INSTANCE.stop_listening()
        except Exception as e:
            print("Fehler beim Stoppen vor VLC:", e)

    mute_system_mic()

    try:
        process = subprocess.Popen(command)
    except Exception:
        restore_system_mic_state(previous)
        VLC_MIC_STATE_BEFORE_MUSIC = MIC_STATE_UNKNOWN
        if previous is True and APP_INSTANCE is not None:
            try:
                APP_INSTANCE.root.after(300, APP_INSTANCE.start_listening)
            except Exception:
                pass
        raise

    def monitor():
        global VLC_MIC_STATE_BEFORE_MUSIC
        try:
            process.wait()
        except Exception:
            pass
        finally:
            previous_state = VLC_MIC_STATE_BEFORE_MUSIC
            VLC_MIC_STATE_BEFORE_MUSIC = MIC_STATE_UNKNOWN

            if SPEECH_SHUTDOWN.is_set():
                return

            restore_system_mic_state(previous_state)

            # Nur wenn das Mikrofon/der Assistent vor VLC aktiv war,
            # nach dem vollständigen Ende der Musik wieder zuhören.
            if previous_state is True and APP_INSTANCE is not None:
                try:
                    APP_INSTANCE._resume_after_vlc = True
                    APP_INSTANCE.root.after(
                        300,
                        APP_INSTANCE._resume_listening_after_vlc
                    )
                except Exception as e:
                    print("VLC-Wiederaufnahme Fehler:", e)

    threading.Thread(
        target=monitor,
        name="VLCMonitor",
        daemon=True
    ).start()
    return process


def speech_worker():
    global SPEAKING

    while not SPEECH_SHUTDOWN.is_set():
        try:
            item = speech_queue.get(timeout=0.2)
        except queue.Empty:
            continue

        if item is None:
            speech_queue.task_done()
            break

        text, voice, speed, pitch, volume = item

        if not text:
            speech_queue.task_done()
            continue

        # Den Zustand genau vor dieser Ansage merken. Das ist wichtig,
        # wenn der Benutzer das Mikrofon vorher bewusst deaktiviert hat.
        mic_was_active = get_system_mic_active()

        SPEAKING = True
        SPEECH_BLOCK_LISTENING.set()
        mute_system_mic()

        global SPEECH_PROCESS
        try:
            SPEECH_PROCESS = subprocess.Popen(
                [
                    "espeak-ng",
                    "-v", voice,
                    "-s", str(speed),
                    "-p", str(pitch),
                    "-a", str(volume),
                    text
                ],
                start_new_session=True
            )
            SPEECH_PROCESS.wait()
        except Exception as e:
            print("Sprachausgabe Fehler:", e)
        finally:
            SPEECH_PROCESS = None
            restore_system_mic_state(mic_was_active)
            SPEAKING = False
            speech_queue.task_done()
            if speech_queue.empty():
                SPEECH_BLOCK_LISTENING.clear()
            # Nach einer normalen Antwort genau einmal wieder zuhören.
            # Der STOP-Knopf löscht _resume_after_answer und verhindert damit
            # jeden automatischen Neustart.
            try:
                if APP_INSTANCE is not None:
                    if getattr(APP_INSTANCE, "_resume_after_answer", False):
                        APP_INSTANCE.root.after(0, APP_INSTANCE._resume_after_answer_finished)
                    elif not APP_INSTANCE.listening:
                        APP_INSTANCE.root.after(0, APP_INSTANCE.set_assistant_status, "ready")
            except Exception:
                pass

    SPEAKING = False
    SPEECH_BLOCK_LISTENING.clear()
    # Beim Beenden des Workers nichts ungefragt einschalten.


SPEECH_THREAD = threading.Thread(
    target=speech_worker,
    name="SpeechWorker",
    daemon=True
)
SPEECH_THREAD.start()


def shutdown_speech_worker():
    """TTS-Worker sauber beenden und wartende Ansagen verwerfen."""
    SPEECH_SHUTDOWN.set()
    SPEECH_BLOCK_LISTENING.set()

    while True:
        try:
            speech_queue.get_nowait()
        except queue.Empty:
            break
        else:
            speech_queue.task_done()

    try:
        speech_queue.put_nowait(None)
    except Exception:
        pass

    if SPEECH_THREAD and SPEECH_THREAD.is_alive():
        SPEECH_THREAD.join(timeout=2.0)


def speak_mbrola(
    text,
    voice="mb-de4",
    speed=165,
    pitch=45,
    volume=185
):
    if not text or SPEECH_SHUTDOWN.is_set():
        return

    # Bereits beim Einreihen wird das Mikrofon logisch gesperrt.
    SPEECH_BLOCK_LISTENING.set()

    speech_queue.put(
        (str(text), voice, speed, pitch, volume)
    )


# ============================================================
# DATENBANK
# ============================================================

def _configure_db(conn, enable_wal=False):
    """Schnelle und robuste SQLite-Konfiguration für den normalen Betrieb."""
    if enable_wal:
        conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA temp_store=MEMORY")


DB_FTS5_AVAILABLE = False


def init_db():
    global DB_FTS5_AVAILABLE
    DB_FTS5_AVAILABLE = False
    conn = sqlite3.connect(DB_FILE)

    try:
        _configure_db(conn, enable_wal=True)
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS qa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT UNIQUE,
                answer TEXT
            )
        """)

        # Beschleunigt die normalisierte Exaktsuche erheblich.
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_qa_question_normalized
            ON qa(lower(trim(question)))
        """)

        # FTS5 hält eine separate Suchstruktur für die Ähnlichkeitssuche.
        # Sie wird einmalig aufgebaut und anschließend über Trigger synchron gehalten.
        try:
            c.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS qa_fts USING fts5(
                    question,
                    content='qa',
                    content_rowid='id',
                    tokenize='unicode61'
                )
            """)
            c.execute("""
                CREATE TRIGGER IF NOT EXISTS qa_ai AFTER INSERT ON qa BEGIN
                    INSERT INTO qa_fts(rowid, question) VALUES (new.id, new.question);
                END
            """)
            c.execute("""
                CREATE TRIGGER IF NOT EXISTS qa_ad AFTER DELETE ON qa BEGIN
                    INSERT INTO qa_fts(qa_fts, rowid, question) VALUES ('delete', old.id, old.question);
                END
            """)
            c.execute("""
                CREATE TRIGGER IF NOT EXISTS qa_au AFTER UPDATE OF question ON qa BEGIN
                    INSERT INTO qa_fts(qa_fts, rowid, question) VALUES ('delete', old.id, old.question);
                    INSERT INTO qa_fts(rowid, question) VALUES (new.id, new.question);
                END
            """)
            DB_FTS5_AVAILABLE = True
            # Nur bei einer leeren/veralteten Suchstruktur neu aufbauen.
            qa_count = c.execute("SELECT COUNT(*) FROM qa").fetchone()[0]
            fts_count = c.execute("SELECT COUNT(*) FROM qa_fts").fetchone()[0]
            if qa_count != fts_count:
                c.execute("INSERT INTO qa_fts(qa_fts) VALUES('rebuild')")
        except sqlite3.OperationalError as e:
            # Falls eine sehr alte SQLite-Version ohne FTS5 verwendet wird,
            # bleibt der Assistent mit den normalen Indexen funktionsfähig.
            DB_FTS5_AVAILABLE = False
            print("FTS5 nicht verfügbar – normale SQLite-Suche bleibt aktiv:", e)

        conn.commit()

    finally:
        conn.close()


def get_all_qa():
    conn = sqlite3.connect(DB_FILE)

    try:
        _configure_db(conn)
        c = conn.cursor()

        c.execute(
            "SELECT id, question, answer FROM qa ORDER BY question"
        )

        return c.fetchall()

    finally:
        conn.close()


def insert_qa(question, answer):
    """
    Speichert eine Frage mit ihren Antworten.
    Existiert die Frage bereits, werden ihre Antworten aktualisiert.
    Der bisherige Code hat einen UNIQUE-Fehler still verschluckt,
    wodurch im Editor scheinbar nichts gespeichert wurde.
    """
    conn = sqlite3.connect(DB_FILE)

    try:
        c = conn.cursor()

        c.execute(
            """
            INSERT INTO qa (question, answer)
            VALUES (?, ?)
            ON CONFLICT(question)
            DO UPDATE SET answer = excluded.answer
            """,
            (question, answer)
        )

        conn.commit()
        return True

    except sqlite3.Error as e:
        print("Datenbankfehler beim Speichern:", e)
        return False

    finally:
        conn.close()


def update_qa(qid, question, answer):
    conn = sqlite3.connect(DB_FILE)

    try:
        c = conn.cursor()

        c.execute(
            "UPDATE qa SET question=?, answer=? WHERE id=?",
            (question, answer, qid)
        )

        conn.commit()
        return c.rowcount > 0

    except sqlite3.IntegrityError:
        # Falls beim Ändern der Frage bereits eine andere
        # identische Frage existiert, diese vorhandene Frage
        # mit den neuen Antworten aktualisieren.
        try:
            c.execute(
                "UPDATE qa SET answer=? WHERE question=?",
                (answer, question)
            )
            conn.commit()
            return c.rowcount > 0
        except sqlite3.Error as e:
            print("Datenbankfehler beim Aktualisieren:", e)
            return False

    except sqlite3.Error as e:
        print("Datenbankfehler beim Aktualisieren:", e)
        return False

    finally:
        conn.close()


def delete_qa(qid):
    conn = sqlite3.connect(DB_FILE)

    try:
        c = conn.cursor()

        c.execute(
            "DELETE FROM qa WHERE id=?",
            (qid,)
        )

        conn.commit()

    finally:
        conn.close()


# Häufige deutsche Varianten für die Datenbanksuche.
# Die gespeicherten Fragen werden NICHT verändert; nur die Suchanfrage
# wird für FTS5 um sinnverwandte/gesprochene Begriffe erweitert.
GERMAN_SEARCH_SYNONYMS = {
    "mikro": ["mikrofon"],
    "mic": ["mikrofon"],
    "laut": ["lauter", "lautstärke"],
    "lauter": ["laut", "lautstärke"],
    "leiser": ["leise", "lautstärke"],
    "pc": ["computer", "rechner"],
    "rechner": ["computer", "pc"],
    "computer": ["rechner", "pc"],
    "starten": ["start", "öffnen", "einschalten"],
    "öffnen": ["starten", "einschalten"],
    "einschalten": ["starten", "öffnen"],
    "beenden": ["schließen", "stoppen"],
    "schließen": ["beenden", "stoppen"],
    "speichern": ["sichern", "gespeichert"],
    "sichern": ["speichern"],
    "löschen": ["entfernen"],
    "entfernen": ["löschen"],
    "fehler": ["fehlermeldung", "problem"],
    "problem": ["fehler", "fehlermeldung"],
    "einstellung": ["einstellungen", "konfiguration"],
    "einstellungen": ["einstellung", "konfiguration"],
    "verbinden": ["verbindung", "verbunden"],
    "verbindung": ["verbinden", "verbunden"],
    "aktualisieren": ["update", "aktualisierung"],
    "update": ["aktualisieren", "aktualisierung"],
}

GERMAN_SEARCH_FILLER_WORDS = {
    "wie", "kann", "ich", "mein", "meine", "meinen", "der", "die", "das",
    "den", "dem", "des", "ein", "eine", "einen", "einem", "einer",
    "zu", "für", "von", "mit", "und", "oder", "bitte", "mal", "denn",
    "eigentlich", "gerade", "noch", "auch", "mir", "mich", "du", "kannst",
    "ist", "sind", "bin", "bist", "war", "waren", "wäre", "was", "wer",
}

def normalize_question_text(text):
    """Vereinheitlicht Text für exakte und unscharfe Vergleiche."""
    if not text:
        return ""

    text = str(text).strip().lower()
    text = text.strip(".,!?;:¿¡")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def expand_german_search_terms(text):
    """
    Erzeugt robuste FTS5-Suchbegriffe für gesprochene deutsche Fragen.
    Neben dem Original werden Synonyme und vorsichtige Präfixe verwendet,
    damit z.B. 'Mikro', 'Mikrofon', 'lauter' und 'Lautstärke' zusammenfinden.
    """
    normalized = normalize_question_text(text)
    tokens = re.findall(r"[\wäöüÄÖÜß]+", normalized, flags=re.UNICODE)
    tokens = [t for t in dict.fromkeys(tokens) if len(t) >= 2]

    expanded = []
    for token in tokens:
        if token not in GERMAN_SEARCH_FILLER_WORDS:
            expanded.append(token)
            for synonym in GERMAN_SEARCH_SYNONYMS.get(token, []):
                expanded.append(synonym)

        # Für längere Wörter hilft eine Präfixsuche bei Wortformen:
        # 'einstell' findet z.B. 'einstellung'/'einstellungen'.
        if len(token) >= 6 and token not in GERMAN_SEARCH_FILLER_WORDS:
            expanded.append(token[:6] + "*")

    return list(dict.fromkeys(expanded))


def get_qa_count():
    """Liefert nur die Anzahl der Einträge – ohne die ganze Tabelle zu laden."""
    conn = sqlite3.connect(DB_FILE)
    try:
        _configure_db(conn)
        return conn.execute("SELECT COUNT(*) FROM qa").fetchone()[0]
    finally:
        conn.close()


def find_answer(question_text):
    normalized = normalize_question_text(question_text)

    if not normalized:
        return None

    conn = sqlite3.connect(DB_FILE)

    try:
        _configure_db(conn)
        c = conn.cursor()

        c.execute(
            """
            SELECT answer
            FROM qa
            WHERE lower(trim(question)) = ?
            """,
            (normalized,)
        )

        row = c.fetchone()

        return row[0] if row else None

    finally:
        conn.close()


def find_best_similar(question_text):
    """
    Schnelle Ähnlichkeitssuche:
    FTS5 liefert zunächst nur relevante Kandidaten; RapidFuzz bewertet
    anschließend diese kleine Menge. Für „Was ist X?“-Fragen gilt eine
    harte Themenprüfung, damit niemals ein themenfremder Datensatz gewinnt.
    """
    normalized = normalize_question_text(question_text)
    if not normalized:
        return None, None, 0

    # Sehr wichtig: Allgemeine Frageformen wie „Was ist ein X?“ dürfen
    # nicht allein wegen der gemeinsamen Wörter „was/ist/ein“ auf einen
    # völlig fremden Datenbankeintrag springen. Das eigentliche Thema X
    # muss in einem Kandidaten vorkommen (oder über unsere Synonyme passen).
    generic_match = re.fullmatch(
        r"(?:was\s+ist|was\s+sind|wer\s+ist|was\s+versteht\s+man\s+unter)\s+(?:ein|eine|einen|einem|einer|der|die|das)?\s*([\wäöüß]+)",
        normalized,
        flags=re.UNICODE
    )
    requested_topic = generic_match.group(1) if generic_match else None

    conn = sqlite3.connect(DB_FILE)
    try:
        _configure_db(conn)
        c = conn.cursor()

        candidates = []
        try:
            # Deutsche Varianten + Präfixe für Wortformen berücksichtigen.
            tokens = expand_german_search_terms(normalized)
            if tokens:
                # Die ursprünglichen Inhaltswörter werden miteinander verknüpft.
                # Synonyme eines einzelnen Wortes bleiben innerhalb einer Gruppe
                # per OR verbunden. Dadurch darf z.B. "PC" nicht plötzlich einen
                # beliebigen Eintrag wie "Tornado" finden, nur weil die lange
                # Benutzerfrage gemeinsame Füllwörter enthält.
                original_tokens = [
                    t for t in re.findall(r"[\wäöüÄÖÜß]+", normalized, flags=re.UNICODE)
                    if len(t) >= 2 and t not in GERMAN_SEARCH_FILLER_WORDS
                ]
                groups = []
                for token in dict.fromkeys(original_tokens):
                    variants = [token] + GERMAN_SEARCH_SYNONYMS.get(token, [])
                    if len(token) >= 6:
                        variants.append(token[:6] + "*")
                    parts = []
                    for variant in dict.fromkeys(variants):
                        if variant.endswith("*"):
                            safe = variant[:-1].replace('"', '""')
                            parts.append('"' + safe + '"*')
                        else:
                            safe = variant.replace('"', '""')
                            parts.append('"' + safe + '"')
                    if parts:
                        groups.append("(" + " OR ".join(parts) + ")")

                # Bei mehreren echten Begriffen müssen nicht zwingend alle
                # vorhanden sein: OR zwischen den Begriffgruppen erlaubt auch
                # natürlich formulierte Fragen. Entscheidend ist, dass innerhalb
                # einer Gruppe nur das Wort bzw. dessen Synonyme zählen.
                match_expr = " OR ".join(groups[:12])
                c.execute("""
                    SELECT qa.question, qa.answer
                    FROM qa_fts
                    JOIN qa ON qa.id = qa_fts.rowid
                    WHERE qa_fts MATCH ?
                    ORDER BY bm25(qa_fts)
                    LIMIT 150
                """, (match_expr,))
                candidates = c.fetchall()
        except sqlite3.OperationalError:
            candidates = []

        # Falls FTS5 nichts findet, nur dann kontrollierter Fallback.
        if not candidates:
            # Kein FTS-Treffer: gezielt nach einem echten Inhaltswort bzw.
            # seinen Synonymen suchen. Niemals die ersten 5000 Datensätze als
            # Zufallskandidaten verwenden, da das bei großen Datenbanken zu
            # völlig unpassenden Treffern führen kann.
            meaningful = [
                t for t in re.findall(r"[\wäöüÄÖÜß]+", normalized, flags=re.UNICODE)
                if len(t) >= 2 and t not in GERMAN_SEARCH_FILLER_WORDS
            ]
            variants = []
            for token in meaningful:
                variants.extend([token] + GERMAN_SEARCH_SYNONYMS.get(token, []))
            variants = list(dict.fromkeys(variants))
            if variants:
                clauses = ["lower(trim(question)) LIKE ?"] * min(len(variants), 12)
                params = ["%" + v + "%" for v in variants[:12]]
                c.execute(
                    "SELECT question, answer FROM qa WHERE " + " OR ".join(clauses) + " LIMIT 150",
                    params
                )
                candidates = c.fetchall()
    finally:
        conn.close()

    best_q = None
    best_a = None
    best_score = 0

    normalized_tokens = set(re.findall(r"[\wäöüÄÖÜß]+", normalized, flags=re.UNICODE))

    # Synonyme des ausdrücklich gefragten Themas, z.B. PC -> Computer/Rechner.
    topic_variants = set()
    if requested_topic:
        topic_variants.update([requested_topic])
        topic_variants.update(GERMAN_SEARCH_SYNONYMS.get(requested_topic, []))

    for q, a in candidates:
        candidate = normalize_question_text(q)
        if not candidate:
            continue

        candidate_tokens = set(re.findall(r"[\wäöüÄÖÜß]+", candidate, flags=re.UNICODE))

        # Bei „Was ist ein X?“ ist X eine harte Bedingung. Ein Kandidat wie
        # „Kannst du mich was fragen“ darf deshalb niemals als Antwort für
        # „Was ist ein Affe?“ ausgewählt werden.
        if requested_topic:
            # HARTE SICHERHEITSREGEL für Wissensfragen:
            # Bei „Was ist ein X?“ darf ein Kandidat nur dann verwendet
            # werden, wenn X selbst oder ein ausdrücklich definiertes
            # Synonym im Datenbank-Eintrag vorkommt. Eine reine Fuzzy-
            # Ähnlichkeit darf diese Regel niemals umgehen.
            direct_topic_match = any(variant in candidate_tokens for variant in topic_variants)
            prefix_topic_match = any(
                len(variant) >= 5 and any(tok.startswith(variant[:5]) for tok in candidate_tokens)
                for variant in topic_variants
            )
            if not (direct_topic_match or prefix_topic_match):
                continue

        ratio_score = fuzz.ratio(normalized, candidate)
        token_set_score = fuzz.token_set_ratio(normalized, candidate)
        weighted_score = fuzz.WRatio(normalized, candidate)
        score = max(ratio_score, token_set_score, weighted_score)

        if requested_topic:
            # Bei einer klaren Themenübereinstimmung darf ein kurzer
            # Datenbankeintrag wie „Computer“ die längere Frage schlagen.
            if any(variant in candidate_tokens for variant in topic_variants):
                score = max(score, 96)
            elif len(candidate_tokens) == 1:
                # Präfix-Treffer bleiben möglich, aber nur beim konkreten Thema.
                score = max(score, 92)

        elif len(candidate_tokens) == 1:
            keyword = next(iter(candidate_tokens))
            if keyword in normalized_tokens:
                score = max(score, 96)

        if score > best_score:
            best_score = score
            best_q = q
            best_a = a

    return best_q, best_a, best_score




def get_random_question():
    """Zieht einen zufälligen Eintrag über den Primärschlüssel-Index."""
    conn = sqlite3.connect(DB_FILE)
    try:
        _configure_db(conn)
        c = conn.cursor()
        max_id = c.execute("SELECT MAX(id) FROM qa").fetchone()[0]
        if not max_id:
            return None
        random_id = random.randint(1, max_id)
        row = c.execute(
            "SELECT question FROM qa WHERE id >= ? ORDER BY id LIMIT 1",
            (random_id,)
        ).fetchone()
        if row:
            return row[0]
        row = c.execute("SELECT question FROM qa ORDER BY id LIMIT 1").fetchone()
        return row[0] if row else None
    finally:
        conn.close()


# ============================================================
# WETTER
# ============================================================

def get_weather_bad_driburg():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=51.733"
        "&longitude=9.019"
        "&current_weather=true"
        "&timezone=Europe%2FBerlin"
    )

    # Mehrere Versuche, damit die automatische Wetteransage
    # bei einem kurzen Netzwerk/API-Problem nicht fehlschlägt.
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()

            data = r.json()
            cw = data.get("current_weather")

            if not cw:
                raise ValueError("Keine aktuellen Wetterdaten erhalten.")

            temperature = cw.get("temperature")
            windspeed = cw.get("windspeed")

            if temperature is None or windspeed is None:
                raise ValueError("Wetterdaten sind unvollständig.")

            return (
                f"In Bad Driburg sind es aktuell "
                f"{temperature} Grad und "
                f"{windspeed} Kilometer pro Stunde Wind."
            )

        except Exception as e:
            print(f"Wetter Fehler (Versuch {attempt + 1}/3):", e)
            if attempt < 2:
                time.sleep(2)

    return "Die Wetterdaten konnten momentan nicht geladen werden."


def get_weather_warning_with_forecast():
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast?"
            "latitude=51.733&"
            "longitude=9.019&"
            "hourly=precipitation_probability,windspeed_10m&"
            "timezone=Europe%2FBerlin"
        )

        r = requests.get(
            url,
            timeout=5
        )

        r.raise_for_status()

        data = r.json()

        hourly = data.get("hourly")

        if not hourly:
            return None

        rain_list = hourly.get(
            "precipitation_probability",
            []
        )

        wind_list = hourly.get(
            "windspeed_10m",
            []
        )

        if not rain_list or not wind_list:
            return None

        # Die nächsten 12 Stunden prüfen.
        check_count = min(
            12,
            len(rain_list),
            len(wind_list)
        )

        for i in range(check_count):
            rain = rain_list[i]
            wind = wind_list[i]

            if rain is not None and rain >= 70:
                return (
                    "Achtung! In den nächsten Stunden "
                    "besteht eine hohe Regenwahrscheinlichkeit."
                )

            if wind is not None and wind >= 50:
                return (
                    "Warnung! In den nächsten Stunden "
                    "wird starker Wind erwartet."
                )

        return None

    except Exception as e:
        print("Wetterwarnung Fehler:", e)
        return None


# ============================================================
# WEBSUCHE
# ============================================================

def search_web_answer(query):
    try:
        encoded_query = urllib.parse.quote_plus(query)

        url = (
            "https://api.duckduckgo.com/"
            f"?q={encoded_query}"
            "&format=json"
            "&no_redirect=1"
            "&no_html=1"
            "&kl=de-de"
        )

        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        text = (
            data.get("AbstractText")
            or data.get("Definition")
        )

        if not text:
            topics = data.get("RelatedTopics", [])
            for topic in topics:
                if isinstance(topic, dict) and topic.get("Text"):
                    text = topic["Text"]
                    break

        if not text:
            return None

        # Nur den ERSTEN Satz zurückgeben.
        # Dabei auch ! und ? als Satzende berücksichtigen.
        text = re.sub(r"\s+", " ", text).strip()
        match = re.search(r"^(.+?[.!?])(?:\s|$)", text)

        if match:
            short = match.group(1).strip()
        else:
            short = text.strip()

        if not short:
            return None

        # Falls DuckDuckGo einen sehr langen Text ohne Satzende liefert,
        # auf einen einzelnen kurzen Satz begrenzen.
        return short

    except Exception as e:
        print("Websuche Fehler:", e)
        return None



def search_web_answer_extended(query):
    """
    Eigene Websuche für den Sprachbefehl „Websuche starten“.
    Die normale automatische Websuche bleibt vollständig unberührt.

    Ziel:
    - konkrete Frage möglichst direkt beantworten
    - wenn ein Satz genügt: genau ein Satz
    - nur wenn nötig: bis zu drei Sätze
    - keine Fakten aus Jahreszahlen selbst berechnen
    """
    try:
        query = re.sub(r"\s+", " ", str(query or "")).strip()
        if not query:
            return None

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0 Safari/537.36"
            )
        }

        raw_sources = []

        def add_source(text_value, source):
            if not text_value:
                return
            value = re.sub(r"<[^>]+>", " ", str(text_value))
            value = (
                value.replace("&nbsp;", " ")
                .replace("&amp;", "&")
                .replace("&quot;", '"')
                .replace("&#39;", "'")
                .replace("&#x27;", "'")
            )
            value = re.sub(r"\s+", " ", value).strip()
            if len(value) >= 25:
                raw_sources.append((value, source))

        # 1) DuckDuckGo Instant Answer
        try:
            url = (
                "https://api.duckduckgo.com/?q="
                + urllib.parse.quote_plus(query)
                + "&format=json&no_redirect=1&no_html=1&kl=de-de"
            )
            r = requests.get(url, timeout=8, headers=headers)
            if r.ok:
                data = r.json()
                add_source(data.get("AbstractText"), "DuckDuckGo")
                add_source(data.get("Definition"), "DuckDuckGo")
                for topic in data.get("RelatedTopics", []) or []:
                    if isinstance(topic, dict):
                        add_source(topic.get("Text"), "DuckDuckGo")
        except Exception as e:
            print("Websuche DDG API Fehler:", e)

        # 2) Wikipedia: komplette Frage UND Sachbegriffe.
        wiki_queries = [query]
        fact_query = re.sub(
            r"\b(wie|was|wer|wann|wo|warum|wieso|welche|welcher|welches|"
            r"ist|sind|hat|haben|alt|jahr|jahre|kann|können|gibt|es)\b",
            " ",
            query,
            flags=re.I
        )
        fact_query = re.sub(r"[?!.,;:]+", " ", fact_query)
        fact_query = re.sub(r"\s+", " ", fact_query).strip()
        if fact_query and fact_query.lower() != query.lower():
            wiki_queries.append(fact_query)

        try:
            titles_seen = set()
            for wiki_query in wiki_queries:
                url = (
                    "https://de.wikipedia.org/w/api.php"
                    "?action=query&list=search&format=json&utf8=1"
                    "&srlimit=5&srsearch="
                    + urllib.parse.quote_plus(wiki_query)
                )
                r = requests.get(url, timeout=8, headers=headers)
                if not r.ok:
                    continue

                data = r.json()
                for item in data.get("query", {}).get("search", [])[:5]:
                    title = item.get("title")
                    if not title or title.lower() in titles_seen:
                        continue
                    titles_seen.add(title.lower())

                    summary_url = (
                        "https://de.wikipedia.org/api/rest_v1/page/summary/"
                        + urllib.parse.quote(title.replace(" ", "_"))
                    )
                    sr = requests.get(summary_url, timeout=8, headers=headers)
                    if sr.ok:
                        add_source(sr.json().get("extract"), "Wikipedia")
        except Exception as e:
            print("Websuche Wikipedia Fehler:", e)

        # 3) DuckDuckGo HTML-Ergebnisse als zusätzlicher Fallback.
        try:
            url = (
                "https://html.duckduckgo.com/html/?q="
                + urllib.parse.quote_plus(query)
                + "&kl=de-de"
            )
            r = requests.get(url, timeout=10, headers=headers)
            if r.ok:
                matches = re.findall(
                    r'class=["\'][^"\']*result__snippet[^"\']*["\'][^>]*>'
                    r'(.*?)</(?:a|div|span)>',
                    r.text,
                    flags=re.I | re.S
                )
                for raw in matches:
                    add_source(raw, "DuckDuckGo-Suchergebnis")
        except Exception as e:
            print("Websuche HTML Fehler:", e)

        if not raw_sources:
            return None

        # Einzelne Sätze aus den Quellen erzeugen.
        sentences = []
        seen = set()

        topic_words = [
            w.lower()
            for w in re.findall(
                r"[A-Za-zÄÖÜäöüß0-9]+",
                fact_query or query
            )
            if len(w) >= 3
        ]

        for source_text, source_name in raw_sources:
            for sentence in re.split(r"(?<=[.!?])\s+", source_text):
                sentence = sentence.strip()
                if len(sentence) < 25:
                    continue

                key = re.sub(r"\s+", " ", sentence.lower())
                if key in seen:
                    continue
                if any(bad in key for bad in (
                    "captcha",
                    "unusual traffic",
                    "keine ergebnisse",
                    "no results",
                    "javascript erforderlich"
                )):
                    continue

                seen.add(key)
                lower = sentence.lower()

                score = sum(6 for w in topic_words if w in lower)

                # Passender Fragetyp bekommt Vorrang.
                if re.search(r"\bwie\s+alt\b", query, re.I):
                    if re.search(
                        r"\b(gegründet|gründung|erstmals|erwähnt|"
                        r"ersterwähnung|alter|jahre|jahrhundert|geboren)\b",
                        lower
                    ):
                        score += 15
                    if re.search(r"\b(1[0-9]{3}|20[0-2][0-9])\b", lower):
                        score += 10

                elif re.search(r"\bwann\b", query, re.I):
                    if re.search(r"\b(1[0-9]{3}|20[0-2][0-9])\b", lower):
                        score += 15

                elif re.search(r"\bwie\s+viele\b", query, re.I):
                    if re.search(r"\b\d[\d.,]*\b", lower):
                        score += 15

                elif re.search(r"\bwer\b", query, re.I):
                    if re.search(
                        r"\b(ist|war|gründer|autor|präsident|sänger|"
                        r"vorsitzender)\b",
                        lower
                    ):
                        score += 10

                elif re.search(r"\bwo\b", query, re.I):
                    if re.search(
                        r"\b(liegt|befindet|in|bei|standort)\b",
                        lower
                    ):
                        score += 10

                if source_name == "Wikipedia":
                    score += 3

                sentences.append((score, sentence, source_name))

        if not sentences:
            return None

        ranked = sorted(
            enumerate(sentences),
            key=lambda item: (-item[1][0], item[0])
        )

        best = []
        used = set()

        for _, (_, sentence, source_name) in ranked:
            key = sentence.lower()
            if key in used:
                continue
            used.add(key)
            best.append((sentence, source_name))
            if len(best) == 3:
                break

        if not best:
            return None

        first = best[0][0]
        lower_first = first.lower()

        # Ein Satz genügt, wenn er die Frage konkret beantwortet.
        direct = False

        if re.search(r"\bwie\s+alt\b", query, re.I):
            direct = bool(
                re.search(
                    r"\b(gegründet|gründung|erstmals|erwähnt|"
                    r"ersterwähnung|alter|jahre|jahrhundert|geboren)\b",
                    lower_first
                )
                or re.search(
                    r"\b(1[0-9]{3}|20[0-2][0-9])\b",
                    lower_first
                )
            )

        elif re.search(r"\bwann\b", query, re.I):
            direct = bool(
                re.search(
                    r"\b(1[0-9]{3}|20[0-2][0-9])\b",
                    lower_first
                )
            )

        elif re.search(r"\bwie\s+viele\b", query, re.I):
            direct = bool(re.search(r"\b\d[\d.,]*\b", lower_first))

        else:
            direct = bool(
                topic_words
                and any(w in lower_first for w in topic_words)
                and re.search(
                    r"\b(ist|sind|war|waren|hat|haben|liegt|befindet|"
                    r"wurde|wird|bedeutet|bezeichnet|nennt|gilt)\b",
                    lower_first
                )
            )

        if direct:
            return first.strip()

        return " ".join(
            sentence for sentence, _ in best[:3]
        ).strip()

    except Exception as e:
        print("Websuche erweitert Fehler:", e)
        return None


# ============================================================
# GESICHTSERKENNUNG (OPTIONAL)
# ============================================================
# Die Kameraauswahl wird separat in der INI gespeichert.
# Für die eigentliche Erkennung wird OpenCV benötigt.
# Dieses Modul ist absichtlich gekapselt, damit Aufnahme/FTS5
# nicht verändert werden.
FACE_CAMERA_INI_SECTION = "Gesichtserkennung"
FACE_CAMERA_INI_KEY = "kamera"

def get_face_camera_index(config):
    """Liest die gespeicherte Kamera aus der INI; Standard ist 0."""
    try:
        return config.getint(FACE_CAMERA_INI_SECTION, FACE_CAMERA_INI_KEY, fallback=0)
    except Exception:
        return 0

def set_face_camera_index(config, index):
    """Speichert die ausgewählte Kamera in der INI."""
    if not config.has_section(FACE_CAMERA_INI_SECTION):
        config.add_section(FACE_CAMERA_INI_SECTION)
    config.set(FACE_CAMERA_INI_SECTION, FACE_CAMERA_INI_KEY, str(int(index)))


# ============================================================
# PROGRAMME
# ============================================================


# ============================================================
# GESICHTER - BILDER SEPARAT, INI NUR METADATEN
# ============================================================
FACE_DIR_NAME = "gesichter"
FACE_SECTION_PREFIX = "Gesicht_"

def face_directory(base_dir=None):
    base = Path(base_dir) if base_dir else Path(__file__).resolve().parent
    folder = base / FACE_DIR_NAME
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def save_face_record(config, base_dir, name, image_path):
    """Speichert nur Name + relativen Bildpfad in der INI."""
    sections = [
        s for s in config.sections()
        if s.startswith(FACE_SECTION_PREFIX)
    ]
    number = len(sections) + 1
    section = f"{FACE_SECTION_PREFIX}{number}"

    if not config.has_section(section):
        config.add_section(section)

    rel_path = Path(image_path).resolve().relative_to(
        Path(base_dir).resolve()
    )
    config.set(section, "name", name)
    config.set(section, "bild", str(rel_path))

def load_face_records(config, base_dir):
    """Lädt gespeicherte Namen und Bildpfade aus der INI."""
    records = []
    for section in config.sections():
        if not section.startswith(FACE_SECTION_PREFIX):
            continue

        name = config.get(section, "name", fallback="").strip()
        rel_path = config.get(section, "bild", fallback="").strip()
        if not name or not rel_path:
            continue

        image_path = (Path(base_dir) / rel_path).resolve()
        if image_path.is_file():
            records.append((name, image_path))

    return records

def open_program(path, speak=True):
    try:
        if not os.path.exists(path):
            if speak:
                speak_mbrola(
                    "Das Programm wurde nicht gefunden."
                )
            return False

        if speak:
            speak_mbrola(
                f"Ich starte {os.path.basename(path)}."
            )

        subprocess.Popen(
            [path],
            start_new_session=True
        )

        return True

    except Exception as e:
        print("Programmstart Fehler:", e)

        if speak:
            speak_mbrola(
                "Programm konnte nicht gestartet werden."
            )

        return False


# ============================================================
# BROWSER
# ============================================================

def open_browser(url):
    try:
        webbrowser.open(url)
        return True

    except Exception as e:
        print("Browser Fehler:", e)
        return False


# ============================================================
# MUSIK
# ============================================================

def play_local_music(search=None):
    folder = load_music_path()

    if not os.path.isdir(folder):
        speak_mbrola(
            "Der Musikordner wurde nicht gefunden."
        )
        return

    files = []

    try:
        for root, dirs, filenames in os.walk(folder):

            for filename in filenames:

                if filename.lower().endswith(
                    (".mp3", ".wav", ".flac", ".ogg", ".m4a")
                ):
                    files.append(
                        os.path.join(root, filename)
                    )

    except Exception as e:
        print("Musik-Suche Fehler:", e)

    if not files:
        speak_mbrola(
            "Keine Musikdateien gefunden."
        )
        return

    if search:
        search_lower = search.lower()

        matches = [
            f
            for f in files
            if search_lower in os.path.basename(f).lower()
        ]

        if matches:
            try:
                start_vlc_with_mic_control(
                    ["vlc", matches[0]]
                )

                speak_mbrola(
                    f"Ich spiele {os.path.basename(matches[0])}."
                )

            except Exception as e:
                print("VLC Fehler:", e)
                speak_mbrola(
                    "Die Musik konnte nicht gestartet werden."
                )

            return

        speak_mbrola(
            f"Ich habe {search} nicht gefunden."
        )
        return

    try:
        start_vlc_with_mic_control(
            ["vlc"] + files
        )

        speak_mbrola(
            "Ich starte deine Musik."
        )

    except Exception as e:
        print("VLC Fehler:", e)

        speak_mbrola(
            "Die Musik konnte nicht gestartet werden."
        )


# ============================================================
# AUDIO-SYSTEM
# ============================================================

def restart_audio_system(driver):
    try:

        if driver == "pulse":
            os.system(
                "systemctl --user restart pipewire"
            )
            os.system(
                "systemctl --user restart pipewire-pulse"
            )

        elif driver == "alsa":
            os.system("alsactl init")

        elif driver == "jack":
            os.system(
                "systemctl --user restart jackd"
            )

        elif driver == "portaudio":
            print(
                "PortAudio benötigt keinen Neustart."
            )

        else:
            print(
                f"Kein spezieller Neustart für {driver}."
            )

        print(
            f"Audio-System für Treiber "
            f"'{driver}' neu gestartet."
        )

    except Exception as e:
        print(
            "Fehler beim Neustart des Audio-Systems:",
            e
        )


# ============================================================
# KONTEXTMENÜ
# ============================================================

def add_context_menu(widget):
    menu = tk.Menu(
        widget,
        tearoff=0
    )

    menu.add_command(
        label="Ausschneiden",
        command=lambda: widget.event_generate("<<Cut>>")
    )

    menu.add_command(
        label="Kopieren",
        command=lambda: widget.event_generate("<<Copy>>")
    )

    menu.add_command(
        label="Einfügen",
        command=lambda: widget.event_generate("<<Paste>>")
    )

    menu.add_command(
        label="Alles auswählen",
        command=lambda: widget.event_generate("<<SelectAll>>")
    )

    def show_menu(event):
        try:
            menu.tk_popup(
                event.x_root,
                event.y_root
            )
        finally:
            menu.grab_release()

    widget.bind(
        "<Button-3>",
        show_menu
    )

    widget.bind(
        "<Control-a>",
        lambda e: widget.event_generate("<<SelectAll>>")
    )

    widget.bind(
        "<Control-A>",
        lambda e: widget.event_generate("<<SelectAll>>")
    )


# ============================================================
# ASSISTENT APP
# ============================================================

def get_current_lotto_numbers():
    """Holt die aktuell veröffentlichten LOTTO-6aus49-Zahlen mit Ziehungsdatum."""
    urls = [
        "https://www.westlotto.de/infos-und-zahlen/gewinnzahlen/lotto/gewinnzahlen-lotto.html",
        "https://www.lotto.de/lotto-6aus49/lottozahlen",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"
    }

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            page = response.text
            page = re.sub(r"<script[\s\S]*?</script>", " ", page, flags=re.I)
            page = re.sub(r"<style[\s\S]*?</style>", " ", page, flags=re.I)
            page = re.sub(r"<[^>]+>", " ", page)
            page = re.sub(r"\s+", " ", page).strip()

            match = re.search(
                r"Ergebnisse\s+vom\s+(?P<date>(?:Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag),?\s+(?:den\s+)?\d{1,2}\.\d{1,2}\.\d{4})\s+(?P<body>.*?)\s+Superzahl\s+(?P<super>\d)",
                page, flags=re.I
            )
            if not match:
                continue

            draw_date = match.group("date").strip()
            body = match.group("body")
            numbers = []
            for value in re.findall(r"(?<!\d)(\d{1,2})(?!\d)", body):
                n = int(value)
                if 1 <= n <= 49 and n not in numbers:
                    numbers.append(n)
                if len(numbers) == 6:
                    break

            if len(numbers) == 6:
                return draw_date, numbers, int(match.group("super"))
        except Exception as e:
            print("Lotto-Abfrage Fehler:", e)

    return None


class AssistantApp:

    def __init__(self, root):
        global APP_INSTANCE
        APP_INSTANCE = self

        self.root = root

        self.root.title(
            "Sprachassistent"
        )

        self.root.geometry(
            "1300x800"
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_exit
        )

        self.recognizer = sr.Recognizer()

        self.microphone_index = None

        self.listening = False
        self.listen_thread = None
        self._listen_lock = threading.Lock()
        self._stop_requested = False
        self.active_mic_source = None

        self.current_qa_id = None

        self.mic_radius = 12
        self.mic_growing = True
        self.audio_level = 0

        self.last_speech_time = time.time()

        self.scheduler_running = True
        self._resume_after_answer = False
        self._resume_after_vlc = False

        # Terminplaner – bewusst getrennt von Datenbank und übrigen Funktionen
        self.reminders_file = str(Path(__file__).resolve().parent / "erinnerungen.json")
        self.reminders = []
        self._termin_mode = None
        self._termin_pending_date = None
        self._termin_pending_time = None
        self._termin_pending_text = None
        self._termin_confirm_window = None
        self._termin_listening_before_speak = False
        self._termin_load()

        self.style = ttk.Style(
            self.root
        )

        self.apply_gruvbox_style()

        cfg = load_main_config()

        self.autoplay_hourly_time = tk.BooleanVar(
            value=cfg["hourly_time"]
        )

        self.autoplay_halfhour_weather = tk.BooleanVar(
            value=cfg["half_hour_weather"]
        )

        self.autoplay_interval = tk.IntVar(
            value=cfg["interval"]
        )

        self.sound_driver = cfg["sound_driver"]

        self.microphone_index = cfg[
            "microphone_index"
        ]

        self.voice = cfg["voice"]
        self.speed = cfg["speed"]
        self.pitch = cfg["pitch"]
        self.volume = cfg["volume"]

        self.programs = cfg["programs"]

        self.auto_backup_enabled = tk.BooleanVar(
            value=cfg["auto_backup"]
        )

        self.backup_name = tk.StringVar(
            value=cfg["backup_name"]
        )


        self.create_menu()

        self.create_main_layout()
        self._termin_update_dashboard_indicator()
        self.root.after(1000, self._check_reminders)

        add_context_menu(
            self.question_entry
        )

        add_context_menu(
            self.answer1_text
        )

        add_context_menu(
            self.answer2_text
        )

        add_context_menu(
            self.answer3_text
        )

        add_context_menu(
            self.log_text
        )

        self.theme_widgets = [
            self.log_text,
            self.qa_listbox,
            self.answer1_text,
            self.answer2_text,
            self.answer3_text,
            self.mic_canvas,
            self.visual_canvas
        ]

        apply_theme(
            self.root,
            self.style,
            self.theme_widgets
        )

        self.update_datetime()

        self.root.after(
            500,
            self.update_weather_label
        )

        self.root.after(
            200,
            self.animate_mic
        )

        self.root.after(
            200,
            self.animate_visualizer
        )

        # Überwacht das Ende der TTS-Ausgabe und setzt "SPRICHT"
        # anschließend automatisch wieder auf "BEREIT".
        self.root.after(200, self._refresh_speaking_status)

        self.schedule_weather_warning()

        if (
            self.autoplay_interval.get() > 0
            or self.autoplay_hourly_time.get()
            or self.autoplay_halfhour_weather.get()
        ):
            self.schedule_autoplay()


    # ========================================================
    # HAUPT-LAYOUT
    # ========================================================

    def create_main_layout(self):
        """Modernes Desktop-Dashboard mit klarer Navigation und Cards.
        Die bestehenden Widget-Attribute bleiben erhalten, damit die
        vorhandene Sprachsteuerung, Datenbank, Animationen und Seiten
        unverändert weiterarbeiten können.
        """
        th = current_theme

        # Fenster
        self.root.geometry("1440x900")
        self.root.minsize(1100, 700)
        self.root.configure(bg=th["bg"])

        # ---------- Kopfbereich ----------
        header = tk.Frame(self.root, bg=th["bg2"], height=112)
        header.pack(fill=tk.X, padx=16, pady=(16, 10))
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=th["bg2"])
        brand.pack(side=tk.LEFT, fill=tk.Y, padx=22)
        tk.Label(brand, text="◉  SPRACHASSISTENT", font=("TkDefaultFont", 19, "bold"),
                 bg=th["bg2"], fg=th["fg"]).pack(anchor=tk.W, pady=(13, 0))
        tk.Label(brand, text="Persönliches Sprach-Dashboard", font=("TkDefaultFont", 9),
                 bg=th["bg2"], fg=th["muted"]).pack(anchor=tk.W, pady=(1, 0))

        info = tk.Frame(header, bg=th["bg2"])
        info.pack(side=tk.RIGHT, fill=tk.Y, padx=22)
        self.datetime_label = tk.Label(info, text="", font=("TkDefaultFont", 12, "bold"),
                                       bg=th["bg2"], fg=th["fg"])
        self.datetime_label.pack(anchor=tk.E, pady=(14, 0))
        self.weather_label = tk.Label(info, text="", font=("TkDefaultFont", 9),
                                      bg=th["bg2"], fg=th["muted"])
        self.weather_label.pack(anchor=tk.E, pady=(2, 0))

        # Sichtbare Termin-Glocke. Die Glocke wird gezeichnet, damit
        # kein fehlendes Emoji-Zeichen sie unsichtbar macht.
        self._termin_bell_canvas = tk.Canvas(
            info, width=54, height=50, highlightthickness=0,
            bd=0, bg=th["bg2"], cursor="hand2"
        )
        self._termin_bell_canvas.pack(anchor=tk.E, pady=(3, 0))
        self._termin_bell_canvas.bind("<Button-1>", lambda e: self.open_terminverwaltung())
        self._termin_bell_visible = False

        # ---------- Hauptbereich ----------
        body = tk.Frame(self.root, bg=th["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        # ---------- Seitenleiste ----------
        sidebar = tk.Frame(body, bg=th["bg2"], width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        sidebar.pack_propagate(False)
        self.sidebar = sidebar

        tk.Label(sidebar, text="MENÜ", font=("TkDefaultFont", 9, "bold"),
                 bg=th["bg2"], fg=th["muted"]).pack(anchor=tk.W, padx=18, pady=(20, 10))

        self.nav_buttons = []
        self.active_nav_index = 0

        def nav_button(text, command, active=False):
            index = len(self.nav_buttons)
            b = tk.Button(
                sidebar, text=text,
                command=lambda i=index, c=command: self._activate_nav(i, c),
                anchor="w", relief="flat", bd=0, cursor="hand2",
                padx=18, pady=11,
                bg=th["selected"] if active else th["bg2"],
                fg="#ffffff" if active else th["fg"],
                activebackground=th["selected"],
                activeforeground="#ffffff",
                font=("TkDefaultFont", 10, "bold" if active else "normal")
            )
            b.pack(fill=tk.X, padx=9, pady=2)
            self.nav_buttons.append(b)
            return b

        nav_button("⌂   Startseite", self.show_dashboard, True)
        nav_button("☷   Fragen & Antworten", self.show_qa_editor)
        nav_button("▣   Programme", self.open_program_manager)
        nav_button("♫   Audio / Stimme", self.open_audio_settings)
        nav_button("♪   Musik", self.show_music_page)
        nav_button("◫   Backup", self.show_backup_page)
        nav_button("⚙   Einstellungen", self.show_settings_page)
        nav_button("◷   Termine", self.open_terminverwaltung)
        nav_button("?   Hilfe", self.open_help_window)

        tk.Frame(sidebar, bg=th["border"], height=1).pack(fill=tk.X, padx=18, pady=16)
        tk.Label(sidebar, text="SYSTEMSTATUS", font=("TkDefaultFont", 8, "bold"),
                 bg=th["bg2"], fg=th["muted"]).pack(anchor=tk.W, padx=18, pady=(0, 6))
        status_box = tk.Frame(sidebar, bg=th["bg"])
        status_box.pack(fill=tk.X, padx=12, pady=(0, 12))
        self.status_label = tk.Label(status_box, text="●  BEREIT", font=("TkDefaultFont", 10, "bold"),
                                     bg=th["bg"], fg=th["green"])
        self.status_label.pack(anchor=tk.W, padx=10, pady=(9, 3))

        # Zeigt beim Start eindeutig, ob die schnelle FTS5-Suche aktiv ist.
        fts_text = "●  FTS5 TURBO-SUCHE AKTIV" if DB_FTS5_AVAILABLE else "●  FTS5 NICHT VERFÜGBAR – STANDARDSUCHE"
        fts_fg = th["green"] if DB_FTS5_AVAILABLE else th["muted"]
        self.db_status_label = tk.Label(status_box, text=fts_text, font=("TkDefaultFont", 8, "bold"),
                                        bg=th["bg"], fg=fts_fg)
        self.db_status_label.pack(anchor=tk.W, padx=10, pady=(0, 8))

        tk.Label(sidebar, text="MIKROFON", font=("TkDefaultFont", 8, "bold"),
                 bg=th["bg2"], fg=th["muted"]).pack(anchor=tk.W, padx=18, pady=(8, 5))
        self.mic_combo = ttk.Combobox(sidebar, state="readonly")
        self.mic_combo.pack(fill=tk.X, padx=14)
        self.update_mic_list()
        self.mic_combo.bind("<<ComboboxSelected>>", self.on_mic_change)

        tk.Label(sidebar, text="KAMERA", font=("TkDefaultFont", 8, "bold"),
                 bg=th["bg2"], fg=th["muted"]).pack(anchor=tk.W, padx=18, pady=(10, 5))
        self.camera_var = tk.StringVar(value="Keine Kamera")
        self.camera_combo = ttk.Combobox(sidebar, textvariable=self.camera_var, state="readonly")
        self.camera_combo.pack(fill=tk.X, padx=14)
        self.camera_combo.bind("<<ComboboxSelected>>", self.on_camera_selected)
        self.camera_indices = []
        self.detect_cameras()
        self.camera_test_button = tk.Button(
            sidebar, text="KAMERA TESTEN", command=self.preview_camera,
            relief="flat", bd=0, cursor="hand2", padx=10, pady=7,
            bg=th["accent"], fg=th["fg"], activebackground=th["hover"],
            activeforeground=th["fg"]
        )
        self.camera_test_button.pack(fill=tk.X, padx=14, pady=(6, 4))

        # ---------- Dashboard links ----------
        left = tk.Frame(body, bg=th["bg"], width=470)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        self.dashboard_panel = left

        control_card = tk.Frame(left, bg=th["bg2"], padx=20, pady=18)
        control_card.pack(fill=tk.X, pady=(0, 12))
        tk.Label(control_card, text="SPRACHSTEUERUNG", font=("TkDefaultFont", 11, "bold"),
                 bg=th["bg2"], fg=th["fg"]).pack(anchor=tk.W)
        tk.Label(control_card, text="Starte die Aufnahme und sprich deinen Befehl.",
                 bg=th["bg2"], fg=th["muted"]).pack(anchor=tk.W, pady=(3, 13))
        buttons = tk.Frame(control_card, bg=th["bg2"])
        buttons.pack(fill=tk.X)
        self.start_button = tk.Button(buttons, text="●  STARTEN", command=self.manual_start_listening,
                                      relief="flat", bd=0, cursor="hand2", padx=18, pady=11,
                                      bg=th["green"], fg="#ffffff", activebackground=th["green"],
                                      activeforeground="#ffffff", font=("TkDefaultFont", 10, "bold"))
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.stop_button = tk.Button(buttons, text="■  STOPP", command=self.stop_listening,
                                     relief="flat", bd=0, cursor="hand2", padx=18, pady=11,
                                     bg=th["accent"], fg=th["fg"], activebackground=th["hover"],
                                     activeforeground=th["fg"], font=("TkDefaultFont", 10, "bold"))
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        # ---------- Dashboard-Übersicht ----------
        # Stabiles Grid: alle drei Karten bleiben auch bei Maximierung sichtbar.
        stats = tk.Frame(left, bg=th["bg"])
        stats.pack(fill=tk.X, pady=(0, 12))
        for col in range(3):
            stats.grid_columnconfigure(col, weight=1, uniform="stat")

        def stat_card(title, value, icon, column):
            card = tk.Frame(stats, bg=th["bg2"], padx=14, pady=10, height=78)
            card.grid(row=0, column=column, sticky="nsew",
                      padx=(0 if column == 0 else 4, 4 if column < 2 else 0))
            card.grid_propagate(False)
            tk.Label(card, text=icon, font=("TkDefaultFont", 13, "bold"),
                     bg=th["bg2"], fg=th["fg"]).pack(anchor=tk.W)
            value_label = tk.Label(card, text=value, font=("TkDefaultFont", 12, "bold"),
                                   bg=th["bg2"], fg=th["fg"], anchor="w")
            value_label.pack(anchor=tk.W, pady=(2, 0))
            tk.Label(card, text=title, font=("TkDefaultFont", 8),
                     bg=th["bg2"], fg=th["muted"]).pack(anchor=tk.W)
            return value_label

        self.dashboard_clock_value = stat_card("UHRZEIT", "--:--", "◷", 0)
        self.dashboard_qa_value = stat_card("GESPEICHERTE FRAGEN", "0", "☷", 1)
        self.dashboard_state_value = stat_card("ASSISTENT", "BEREIT", "●", 2)

        mic_card = tk.Frame(left, bg=th["bg2"], padx=20, pady=16)
        mic_card.pack(fill=tk.X, pady=(0, 8))
        tk.Label(mic_card, text="MIKROFON & AUDIO", font=("TkDefaultFont", 11, "bold"),
                 bg=th["bg2"], fg=th["fg"]).pack(anchor=tk.W)
        tk.Label(mic_card, text="Live-Pegel und Aktivitätsanzeige", bg=th["bg2"], fg=th["muted"]).pack(anchor=tk.W, pady=(2, 6))
        self.mic_canvas = tk.Canvas(mic_card, width=360, height=55, bg=th["bg2"], highlightthickness=0)
        self.mic_canvas.pack(fill=tk.X, pady=5)
        self.visual_canvas = tk.Canvas(mic_card, width=440, height=45, bg=th["bg2"], highlightthickness=0)
        self.visual_canvas.pack(fill=tk.X, pady=(4, 4))

        # ---------- Echte Chat-/Gesprächsansicht ----------
        # Die Unterhaltung wird als einzelne Nachrichtenblasen aufgebaut.
        # Dadurch ist sofort erkennbar, wer gesprochen hat.
        chat_card = tk.Frame(left, bg=th["bg2"], padx=18, pady=16)
        chat_card.pack(fill=tk.BOTH, expand=True, pady=(0, 2))

        chat_header = tk.Frame(chat_card, bg=th["bg2"])
        chat_header.pack(fill=tk.X)
        title_area = tk.Frame(chat_header, bg=th["bg2"])
        title_area.pack(side=tk.LEFT)
        tk.Label(title_area, text="GESPRÄCH", font=("TkDefaultFont", 12, "bold"),
                 bg=th["bg2"], fg=th["fg"]).pack(anchor=tk.W)
        tk.Label(title_area, text="Deine Unterhaltung mit ALI",
                 font=("TkDefaultFont", 8), bg=th["bg2"], fg=th["muted"]).pack(anchor=tk.W, pady=(1, 0))
        self.chat_status = tk.Label(chat_header, text="Bereit für deinen nächsten Befehl",
                                    font=("TkDefaultFont", 9, "bold"),
                                    bg=th["bg2"], fg=th["muted"])
        self.chat_status.pack(side=tk.RIGHT, anchor=tk.N)

        chat_body = tk.Frame(chat_card, bg=th["bg"], highlightthickness=1,
                             highlightbackground=th["border"])
        chat_body.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        self.chat_canvas = tk.Canvas(chat_body, bg=th["bg"], highlightthickness=0, bd=0)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scroll = ttk.Scrollbar(chat_body, orient=tk.VERTICAL, command=self.chat_canvas.yview)
        chat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.configure(yscrollcommand=chat_scroll.set)

        self.chat_messages = tk.Frame(self.chat_canvas, bg=th["bg"])
        self.chat_window = self.chat_canvas.create_window((0, 0), window=self.chat_messages, anchor="nw")

        self.chat_messages.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        self.chat_canvas.bind(
            "<Configure>",
            lambda e: self.chat_canvas.itemconfigure(self.chat_window, width=e.width)
        )

        # Mausrad für das Chatfenster aktivieren.
        # Die Bindung funktioniert unter Windows/Linux und greift nur,
        # wenn sich der Mauszeiger tatsächlich über dem Chatbereich befindet.
        self.root.bind_all("<MouseWheel>", self._chat_mousewheel, add="+")
        self.root.bind_all("<Button-4>", self._chat_mousewheel, add="+")
        self.root.bind_all("<Button-5>", self._chat_mousewheel, add="+")

        # Unsichtbares Textfeld für bestehende Theme-/Kompatibilitätslogik.
        self.log_text = tk.Text(chat_body, height=1, width=1)
        self.log_text.pack_forget()

        self._insert_chat_message("system", "Gespräch gestartet. Ich bin bereit.")

        # ---------- Q&A ----------
        right = tk.Frame(body, bg=th["bg2"], width=540)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.qa_panel = right
        self.main_body = body

        self.page_frame = tk.Frame(body, bg=th["bg"])
        self.page_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.page_frame.place_forget()

        tk.Label(right, text="FRAGEN & ANTWORTEN", font=("TkDefaultFont", 14, "bold"),
                 bg=th["bg2"], fg=th["fg"]).pack(anchor=tk.W, padx=20, pady=(20, 2))
        tk.Label(right, text="Das Wissen deines Assistenten verwalten", bg=th["bg2"], fg=th["muted"]).pack(anchor=tk.W, padx=20, pady=(0, 12))

        search_frame = tk.Frame(right, bg=th["bg2"])
        search_frame.pack(fill=tk.X, padx=16, pady=(0, 10))
        tk.Label(search_frame, text="Suche", bg=th["bg2"], fg=th["muted"]).pack(side=tk.LEFT, padx=(4, 7))
        self.qa_search_entry = ttk.Entry(search_frame)
        self.qa_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        ttk.Button(search_frame, text="Suchen", command=lambda: self.search_qa(self.qa_search_entry.get())).pack(side=tk.LEFT, padx=4)
        ttk.Button(search_frame, text="Alle", command=self.refresh_qa_list).pack(side=tk.LEFT, padx=4)
        add_context_menu(self.qa_search_entry)

        list_frame = tk.Frame(right, bg=th["bg2"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16)
        self.qa_listbox = tk.Listbox(list_frame, relief="flat", bd=0, activestyle="none",
                                     bg=th["bg"], fg=th["fg"], selectbackground=th["selected"],
                                     selectforeground=th["fg"], highlightthickness=0,
                                     font=("TkDefaultFont", 10))
        self.qa_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.qa_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.qa_listbox.config(yscrollcommand=scrollbar.set)
        self.qa_listbox.bind("<<ListboxSelect>>", self.on_select_qa)

        form = tk.Frame(right, bg=th["bg2"], padx=16)
        form.pack(fill=tk.X, pady=(10, 4))
        ttk.Label(form, text="Frage:").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.question_entry = ttk.Entry(form)
        self.question_entry.grid(row=0, column=1, sticky=tk.EW, padx=4, pady=4)
        self.answer1_text = tk.Text(form, height=2, wrap="word", relief="flat", bd=0, bg=th["bg"], fg=th["fg"], insertbackground=th["fg"], highlightthickness=0, padx=8, pady=6)
        self.answer2_text = tk.Text(form, height=2, wrap="word", relief="flat", bd=0, bg=th["bg"], fg=th["fg"], insertbackground=th["fg"], highlightthickness=0, padx=8, pady=6)
        self.answer3_text = tk.Text(form, height=2, wrap="word", relief="flat", bd=0, bg=th["bg"], fg=th["fg"], insertbackground=th["fg"], highlightthickness=0, padx=8, pady=6)
        for row, label, widget in ((1, "Antwort 1:", self.answer1_text), (2, "Antwort 2:", self.answer2_text), (3, "Antwort 3:", self.answer3_text)):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky=tk.NW, padx=4, pady=4)
            widget.grid(row=row, column=1, sticky=tk.EW, padx=4, pady=4)
        form.columnconfigure(1, weight=1)

        editor_buttons = tk.Frame(right, bg=th["bg2"], padx=16, pady=10)
        editor_buttons.pack(fill=tk.X)
        ttk.Button(editor_buttons, text="＋ Neu", command=self.new_qa).pack(side=tk.LEFT, padx=4)
        ttk.Button(editor_buttons, text="✓ Speichern", command=self.save_qa).pack(side=tk.LEFT, padx=4)
        ttk.Button(editor_buttons, text="Löschen", command=self.delete_selected_qa).pack(side=tk.LEFT, padx=4)

        self.refresh_qa_list()

    # ========================================================
    # NAVIGATION
    # ========================================================

    def _activate_nav(self, index, command):
        """Setzt den angeklickten Menüpunkt dauerhaft auf aktiv."""
        self.active_nav_index = index
        th = current_theme

        for i, button in enumerate(self.nav_buttons):
            try:
                active = (i == index)
                button.configure(
                    bg=th["selected"] if active else th["bg2"],
                    fg="#ffffff" if active else th["fg"],
                    activebackground=th["selected"],
                    activeforeground="#ffffff",
                    font=("TkDefaultFont", 10, "bold" if active else "normal")
                )
            except tk.TclError:
                pass

        command()

    def show_dashboard(self):
        """Zeigt die normale Startseite wieder an."""
        try:
            self.qa_panel.pack_forget()
            self.dashboard_panel.pack_forget()
            self.dashboard_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            self.qa_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            self.status_label.config(text="● BEREIT", fg=current_theme["green"])
            self.log("Startseite ist aktiv.")
        except tk.TclError:
            pass

    def show_qa_editor(self):
        """Zeigt den Fragen-&-Antworten-Editor großflächig an."""
        try:
            self.dashboard_panel.pack_forget()
            self.qa_panel.pack_forget()
            self.qa_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.status_label.config(text="● FRAGEN & ANTWORTEN", fg=current_theme["fg"])
            self.qa_search_entry.focus_set()
            if self.qa_listbox.size() > 0:
                self.qa_listbox.selection_clear(0, tk.END)
                self.qa_listbox.see(0)
            self.log("Fragen & Antworten geöffnet.")
        except tk.TclError:
            pass


    # ========================================================
    # STYLE
    # ========================================================

    def apply_gruvbox_style(self):

        th = current_theme

        style = self.style

        style.theme_use(
            "clam"
        )

        style.configure(
            "TFrame",
            background=th["bg"]
        )

        style.configure(
            "TLabel",
            background=th["bg"],
            foreground=th["fg"]
        )

        style.configure(
            "TButton",
            background=th["accent"],
            foreground=th["fg"],
            padding=6
        )

        style.map(
            "TButton",
            background=[
                ("active", th["hover"])
            ],
            foreground=[
                ("active", th["fg"])
            ]
        )

        self.root.configure(
            bg=th["bg"]
        )

        self.root.option_add(
            "*Menu.background",
            th["bg"]
        )

        self.root.option_add(
            "*Menu.foreground",
            th["fg"]
        )

        self.root.option_add(
            "*Menu.activeBackground",
            th["hover"]
        )

        self.root.option_add(
            "*Menu.activeForeground",
            th["fg"]
        )


    # ========================================================
    # MENÜ
    # ========================================================

    def create_menu(self):

        menubar = tk.Menu(
            self.root
        )

        # Datei
        file_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        file_menu.add_command(
            label="Datenbank exportieren",
            command=self.export_db
        )

        file_menu.add_command(
            label="Datenbank importieren",
            command=self.import_db
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Beenden",
            command=self.on_exit
        )

        menubar.add_cascade(
            label="Datei",
            menu=file_menu
        )

        # Theme
        theme_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        theme_menu.add_command(
            label="Dunkel",
            command=lambda: self.set_theme("dark")
        )

        theme_menu.add_command(
            label="Hell",
            command=lambda: self.set_theme("light")
        )

        theme_menu.add_command(
            label="Gruvbox",
            command=lambda: self.set_theme("gruvbox")
        )

        menubar.add_cascade(
            label="Theme",
            menu=theme_menu
        )

        # Programme
        prog_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        prog_menu.add_command(
            label="Programme verwalten",
            command=self.open_program_manager
        )

        menubar.add_cascade(
            label="Programme",
            menu=prog_menu
        )

        # Einstellungen
        settings_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        settings_menu.add_separator()

        settings_menu.add_command(
            label="Gesichtserkennung verwalten",
            command=self.open_face_management
        )


        backup_menu = tk.Menu(
            settings_menu,
            tearoff=0
        )

        backup_menu.add_command(
            label="Backup jetzt ausführen",
            command=self.run_backup_now
        )

        backup_menu.add_command(
            label="Backup-Ordner öffnen",
            command=self.open_backup_folder
        )

        backup_menu.add_separator()

        backup_menu.add_checkbutton(
            label="Automatische Backups aktiv",
            variable=self.auto_backup_enabled,
            command=self.toggle_auto_backup
        )

        settings_menu.add_cascade(
            label="Backup-System",
            menu=backup_menu
        )

        settings_menu.add_command(
            label="Backup-Namen ändern",
            command=self.change_backup_name
        )

        settings_menu.add_command(
            label="Musik Pfad",
            command=self.change_music_path
        )

        settings_menu.add_command(
            label="Sound-Treiber",
            command=self.change_sound_driver
        )


        menubar.add_cascade(
            label="Einstellungen",
            menu=settings_menu
        )

        # Audio
        audio_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        audio_menu.add_command(
            label="Audio / Stimme einstellen",
            command=self.open_audio_settings
        )

        menubar.add_cascade(
            label="Audio / Stimme",
            menu=audio_menu
        )

        # Autoplay
        autoplay_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        autoplay_menu.add_checkbutton(
            label="Uhrzeit jede volle Stunde",
            variable=self.autoplay_hourly_time,
            command=self.save_all_settings
        )

        autoplay_menu.add_checkbutton(
            label="Wetter jede halbe Stunde",
            variable=self.autoplay_halfhour_weather,
            command=self.save_all_settings
        )

        autoplay_menu.add_separator()

        autoplay_menu.add_command(
            label="Auto-Fragen Intervall:"
        )

        for i in range(5, 11):

            autoplay_menu.add_radiobutton(
                label=f"{i} Minuten",
                variable=self.autoplay_interval,
                value=i,
                command=self.save_all_settings
            )

        autoplay_menu.add_radiobutton(
            label="Aus",
            variable=self.autoplay_interval,
            value=0,
            command=self.save_all_settings
        )

        menubar.add_cascade(
            label="Autoplay",
            menu=autoplay_menu
        )

        # Hilfe
        help_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        help_menu.add_command(
            label="Anleitung anzeigen",
            command=self.open_help_window
        )

        help_menu.add_command(
            label="Info",
            command=self.open_info_window
        )

        menubar.add_cascade(
            label="Hilfe",
            menu=help_menu
        )

        self.root.config(
            menu=menubar
        )


    # ========================================================
    # THEME
    # ========================================================

    def set_theme(self, name):

        set_theme_by_name(name)
        self.apply_modern_theme()

    def apply_modern_theme(self):
        """Wendet das aktuelle Theme auf die zentrale Oberfläche an."""
        th = current_theme
        apply_theme(self.root, self.style, self.theme_widgets)
        self.root.configure(bg=th["bg"])

        # Die zentralen Dashboard-Bereiche gezielt einfärben, statt alle
        # Frames pauschal gleich zu behandeln.
        for widget_name in ("sidebar", "dashboard_panel", "qa_panel", "page_frame"):
            widget = getattr(self, widget_name, None)
            if widget is not None and widget.winfo_exists():
                try:
                    widget.configure(bg=th["bg2"] if widget_name in ("sidebar", "qa_panel") else th["bg"])
                except tk.TclError:
                    pass

        for i, button in enumerate(getattr(self, "nav_buttons", [])):
            try:
                active = (i == getattr(self, "active_nav_index", 0))
                button.configure(
                    bg=th["selected"] if active else th["bg2"],
                    fg="#ffffff" if active else th["fg"],
                    activebackground=th["selected"],
                    activeforeground="#ffffff",
                    font=("TkDefaultFont", 10, "bold" if active else "normal")
                )
            except tk.TclError:
                pass

        try:
            self.start_button.configure(bg=th["green"], activebackground=th["green"], fg="#ffffff")
            self.stop_button.configure(bg=th["accent"], fg=th["fg"], activebackground=th["hover"], activeforeground=th["fg"])
            self.status_label.configure(bg=th["bg"], fg=th["green"])
        except tk.TclError:
            pass


    # ========================================================
    # HILFE
    # ========================================================

    def open_help_window(self):

        win = tk.Toplevel(
            self.root
        )

        win.title(
            "Anleitung"
        )

        win.geometry(
            "700x600"
        )

        win.configure(
            bg=current_theme["bg"]
        )

        text_widget = tk.Text(
            win,
            bg=current_theme["bg2"],
            fg=current_theme["fg"],
            insertbackground=current_theme["fg"],
            wrap="word"
        )

        text_widget.pack(
            fill=tk.BOTH,
            expand=True
        )

        text_widget.insert(
            tk.END,
            HELP_TEXT
        )

        text_widget.config(
            state="disabled"
        )

        ttk.Button(
            win,
            text="Schließen",
            command=win.destroy
        ).pack(
            pady=10
        )


    def open_info_window(self):
        """Zeigt ein kleines Info-Fenster mit der Programmversion."""
        win = tk.Toplevel(self.root)
        win.title("Info")
        win.geometry("300x180")
        win.resizable(False, False)
        win.transient(self.root)
        win.configure(bg=current_theme["bg"])

        tk.Label(
            win,
            text="Version 5.1",
            font=("TkDefaultFont", 16, "bold"),
            bg=current_theme["bg"],
            fg=current_theme["fg"]
        ).pack(pady=(28, 6))

        tk.Label(
            win,
            text="By Goldisoft 2026",
            font=("TkDefaultFont", 10),
            bg=current_theme["bg"],
            fg=current_theme["fg"]
        ).pack()

        ttk.Button(
            win,
            text="Schließen",
            command=win.destroy
        ).pack(pady=(14, 12))


    # ========================================================
    # EINSTELLUNGEN
    # ========================================================



    def save_all_settings(self):

        save_main_config(
            self.autoplay_hourly_time.get(),
            self.autoplay_halfhour_weather.get(),
            self.autoplay_interval.get(),
            self.sound_driver,
            self.microphone_index,
            self.programs,
            self.voice,
            self.speed,
            self.pitch,
            self.volume,
            self.auto_backup_enabled.get(),
            self.backup_name.get()
        )


    # ========================================================
    # SOUND-TREIBER
    # ========================================================

    def change_sound_driver(self):

        win = tk.Toplevel(
            self.root
        )

        win.title(
            "Sound-Treiber auswählen"
        )

        win.geometry(
            "300x260"
        )

        win.configure(
            bg=current_theme["bg"]
        )

        ttk.Label(
            win,
            text="Sound-Treiber für VLC:"
        ).pack(
            pady=10
        )

        current = load_sound_driver()

        drivers = [
            "pulse",
            "alsa",
            "sdl",
            "oss",
            "jack",
            "portaudio"
        ]

        var = tk.StringVar(
            value=current
        )

        for driver in drivers:

            ttk.Radiobutton(
                win,
                text=driver,
                value=driver,
                variable=var
            ).pack(
                anchor=tk.W,
                padx=20
            )

        def save_and_close():

            driver = var.get()

            save_sound_driver(
                driver
            )

            self.sound_driver = driver

            self.log(
                f"Sound-Treiber gesetzt auf: {driver}"
            )

            speak_mbrola(
                f"Sound-Treiber {driver} gespeichert.",
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            restart_audio_system(
                driver
            )

            self.save_all_settings()

            win.destroy()

        btn_frame = ttk.Frame(
            win
        )

        btn_frame.pack(
            pady=15
        )

        ttk.Button(
            btn_frame,
            text="Speichern",
            command=save_and_close
        ).pack(
            side=tk.LEFT,
            padx=10
        )

        ttk.Button(
            btn_frame,
            text="Abbrechen",
            command=win.destroy
        ).pack(
            side=tk.RIGHT,
            padx=10
        )


    # ========================================================
    # MUSIKPFAD
    # ========================================================

    def change_music_path(self):

        new_path = filedialog.askdirectory(
            title="Musikordner auswählen"
        )

        if not new_path:
            return

        save_music_path(
            new_path
        )

        speak_mbrola(
            "Musikordner gespeichert.",
            self.voice,
            self.speed,
            self.pitch,
            self.volume
        )

        self.log(
            f"Neuer Musikordner: {new_path}"
        )


    # ========================================================
    # AUDIO-EINSTELLUNGEN
    # ========================================================

    def open_audio_settings(self):

        win = tk.Toplevel(
            self.root
        )

        win.title(
            "Audio / Stimme einstellen"
        )

        win.geometry(
            "420x360"
        )

        win.configure(
            bg=current_theme["bg"]
        )

        frame = ttk.Frame(
            win
        )

        frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10
        )

        ttk.Label(
            frame,
            text="Stimme (MBROLA):"
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
            pady=5
        )

        voice_var = tk.StringVar(
            value=self.voice
        )

        voice_combo = ttk.Combobox(
            frame,
            textvariable=voice_var,
            state="readonly",
            values=[
                "mb-de1",
                "mb-de2",
                "mb-de3",
                "mb-de4",
                "mb-de5",
                "mb-de6",
                "mb-de7",
                "mb-de8"
            ]
        )

        voice_combo.grid(
            row=0,
            column=1,
            sticky=tk.W,
            pady=5
        )

        ttk.Label(
            frame,
            text="de1–de7: Deutsch | de8: Bayerisch",
            font=("TkDefaultFont", 8)
        ).grid(
            row=0,
            column=2,
            sticky=tk.W,
            padx=8,
            pady=5
        )

        ttk.Label(
            frame,
            text="Geschwindigkeit:"
        ).grid(
            row=1,
            column=0,
            sticky=tk.W,
            pady=5
        )

        speed_var = tk.IntVar(
            value=self.speed
        )

        speed_spin = ttk.Spinbox(
            frame,
            from_=80,
            to=260,
            textvariable=speed_var,
            width=6
        )

        speed_spin.grid(
            row=1,
            column=1,
            sticky=tk.W,
            pady=5
        )

        ttk.Label(
            frame,
            text="Tonhöhe:"
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            pady=5
        )

        pitch_var = tk.IntVar(
            value=self.pitch
        )

        pitch_spin = ttk.Spinbox(
            frame,
            from_=0,
            to=99,
            textvariable=pitch_var,
            width=6
        )

        pitch_spin.grid(
            row=2,
            column=1,
            sticky=tk.W,
            pady=5
        )

        ttk.Label(
            frame,
            text="Lautstärke:"
        ).grid(
            row=3,
            column=0,
            sticky=tk.W,
            pady=5
        )

        volume_var = tk.IntVar(
            value=self.volume
        )

        volume_spin = ttk.Spinbox(
            frame,
            from_=50,
            to=200,
            textvariable=volume_var,
            width=6
        )

        volume_spin.grid(
            row=3,
            column=1,
            sticky=tk.W,
            pady=5
        )

        def test_voice():

            try:
                speak_mbrola(
                    "Dies ist ein Test der aktuellen Stimme.",
                    voice_var.get(),
                    speed_var.get(),
                    pitch_var.get(),
                    volume_var.get()
                )
            except Exception as e:
                print("TTS-Test Fehler:", e)

        def save_audio():

            try:
                self.voice = voice_var.get()
                self.speed = int(speed_var.get())
                self.pitch = int(pitch_var.get())
                self.volume = int(volume_var.get())

            except ValueError:
                messagebox.showwarning(
                    "Fehler",
                    "Bitte gültige Zahlen eingeben."
                )
                return

            self.save_all_settings()

            self.log(
                "Audio-Einstellungen gespeichert."
            )

            speak_mbrola(
                "Audio-Einstellungen gespeichert.",
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            win.destroy()

        btn_frame = ttk.Frame(
            win
        )

        btn_frame.pack(
            pady=10
        )

        ttk.Button(
            btn_frame,
            text="Test",
            command=test_voice
        ).pack(
            side=tk.LEFT,
            padx=10
        )

        ttk.Button(
            btn_frame,
            text="Speichern",
            command=save_audio
        ).pack(
            side=tk.LEFT,
            padx=10
        )

        ttk.Button(
            btn_frame,
            text="Abbrechen",
            command=win.destroy
        ).pack(
            side=tk.LEFT,
            padx=10
        )


    # ========================================================
    # BACKUP-NAME
    # ========================================================

    def change_backup_name(self):

        win = tk.Toplevel(
            self.root
        )

        win.title(
            "Backup-Namen ändern"
        )

        win.geometry(
            "300x150"
        )

        win.configure(
            bg=current_theme["bg"]
        )

        ttk.Label(
            win,
            text="Backup-Dateiname:"
        ).pack(
            pady=10
        )

        entry = ttk.Entry(
            win,
            textvariable=self.backup_name
        )

        entry.pack(
            pady=5,
            padx=10
        )

        def save_name():

            name = self.backup_name.get().strip()

            if not name:
                messagebox.showwarning(
                    "Fehler",
                    "Name darf nicht leer sein."
                )
                return

            self.save_all_settings()

            messagebox.showinfo(
                "Gespeichert",
                f"Backup-Name gesetzt: {name}"
            )

            win.destroy()

        ttk.Button(
            win,
            text="Speichern",
            command=save_name
        ).pack(
            pady=10
        )


    # ========================================================
    # DB EXPORT / IMPORT
    # ========================================================

    def export_db(self):

        if not os.path.exists(DB_FILE):
            messagebox.showwarning(
                "Export",
                "Die Datenbank existiert noch nicht."
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[
                ("SQLite DB", "*.db")
            ]
        )

        if not path:
            return

        try:
            shutil.copy2(
                DB_FILE,
                path
            )

            messagebox.showinfo(
                "Export",
                "Datenbank erfolgreich exportiert."
            )

        except Exception as e:

            messagebox.showerror(
                "Fehler",
                f"Export fehlgeschlagen:\n{e}"
            )


    def import_db(self):

        path = filedialog.askopenfilename(
            filetypes=[
                ("SQLite DB", "*.db")
            ]
        )

        if not path:
            return

        try:

            shutil.copy2(
                path,
                DB_FILE
            )

            self.refresh_qa_list()

            messagebox.showinfo(
                "Import",
                "Datenbank erfolgreich importiert."
            )

        except Exception as e:

            messagebox.showerror(
                "Fehler",
                f"Import fehlgeschlagen:\n{e}"
            )


    # ========================================================
    # BEENDEN
    # ========================================================

    def on_exit(self):

        # Keine neuen Aufnahmen oder geplanten Aktionen mehr starten.
        self.listening = False
        self.scheduler_running = False

        # Aufnahme-Thread kurz sauber auslaufen lassen.
        if (
            self.listen_thread
            and self.listen_thread.is_alive()
            and self.listen_thread is not threading.current_thread()
        ):
            self.listen_thread.join(timeout=1.5)

        # Aktuellen Datenstand beim Beenden sichern, sofern aktiviert.
        try:
            if self.auto_backup_enabled.get():
                backup_database(self.backup_name.get())
        except Exception as e:
            print("Automatisches Backup beim Beenden fehlgeschlagen:", e)

        # TTS-Warteschlange beenden und Mikrofon sicher freigeben.
        shutdown_speech_worker()

        try:
            self.root.destroy()
        except tk.TclError:
            pass
        except Exception as e:
            print("Fehler beim Beenden der Anwendung:", e)


    def _mic_thread_finished(self):
        if not self.listening:
            try:
                if not getattr(self, "_resume_after_vlc", False):
                    self.set_assistant_status("ready")
            except Exception:
                pass


    # ========================================================
    # EDITOR
    # ========================================================

    def search_qa(self, term):

        term = term.strip().lower()

        if not term:
            self.refresh_qa_list()
            return

        results = []

        for qid, question, answers in self.qa_items:

            if (
                term in question.lower()
                or term in answers.lower()
            ):
                results.append(
                    (qid, question, answers)
                )

        self.qa_listbox.delete(
            0,
            tk.END
        )

        # Suchergebnisse separat speichern,
        # damit die Listbox-Auswahl korrekt bleibt.
        self.qa_items = results

        for qid, question, answers in results:

            self.qa_listbox.insert(
                tk.END,
                question
            )


    def refresh_qa_list(self):

        self.qa_listbox.delete(
            0,
            tk.END
        )

        self.qa_items = get_all_qa()

        for row in self.qa_items:

            self.qa_listbox.insert(
                tk.END,
                row[1]
            )


    def on_select_qa(self, event):

        sel = self.qa_listbox.curselection()

        if not sel:
            return

        index = sel[0]

        if index >= len(self.qa_items):
            return

        qid, question, answers = self.qa_items[index]

        self.current_qa_id = qid

        self.question_entry.delete(
            0,
            tk.END
        )

        self.question_entry.insert(
            0,
            question
        )

        parts = answers.split("||")

        while len(parts) < 3:
            parts.append("")

        self.answer1_text.delete(
            "1.0",
            tk.END
        )

        self.answer1_text.insert(
            tk.END,
            parts[0]
        )

        self.answer2_text.delete(
            "1.0",
            tk.END
        )

        self.answer2_text.insert(
            tk.END,
            parts[1]
        )

        self.answer3_text.delete(
            "1.0",
            tk.END
        )

        self.answer3_text.insert(
            tk.END,
            parts[2]
        )


    def new_qa(self):

        self.current_qa_id = None

        self.question_entry.delete(
            0,
            tk.END
        )

        self.answer1_text.delete(
            "1.0",
            tk.END
        )

        self.answer2_text.delete(
            "1.0",
            tk.END
        )

        self.answer3_text.delete(
            "1.0",
            tk.END
        )


    def save_qa(self):

        question = (
            self.question_entry
            .get()
            .strip()
        )

        a1 = (
            self.answer1_text
            .get("1.0", tk.END)
            .strip()
        )

        a2 = (
            self.answer2_text
            .get("1.0", tk.END)
            .strip()
        )

        a3 = (
            self.answer3_text
            .get("1.0", tk.END)
            .strip()
        )

        # Rechtschreibung vor dem Speichern prüfen.
        original_question = question
        original_a1 = a1
        original_a2 = a2
        original_a3 = a3


        answers = "||".join(
            [
                a1,
                a2,
                a3
            ]
        )

        if not question or not a1:

            messagebox.showwarning(
                "Fehler",
                "Mindestens Antwort 1 muss ausgefüllt sein."
            )

            return

        if self.current_qa_id is None:

            question = normalize_question_text(question)

            saved = insert_qa(
                question,
                answers
            )

        else:

            question = normalize_question_text(question)

            saved = update_qa(
                self.current_qa_id,
                question,
                answers
            )

        if not saved:
            messagebox.showerror(
                "Speicherfehler",
                "Die Frage und Antworten konnten nicht "
                "in der Datenbank gespeichert werden."
            )
            return

        self.refresh_qa_list()

        self.log(
            f"Frage gespeichert: {question}"
        )

        messagebox.showinfo(
            "Gespeichert",
            "Frage und Antworten wurden gespeichert."
        )


    def delete_selected_qa(self):

        if self.current_qa_id is None:
            return

        delete_qa(
            self.current_qa_id
        )

        self.current_qa_id = None

        self.refresh_qa_list()

        self.question_entry.delete(
            0,
            tk.END
        )

        self.answer1_text.delete(
            "1.0",
            tk.END
        )

        self.answer2_text.delete(
            "1.0",
            tk.END
        )

        self.answer3_text.delete(
            "1.0",
            tk.END
        )

        self.log(
            "Frage gelöscht."
        )


    # ========================================================
    # BACKUP
    # ========================================================

    def run_backup_now(self):

        result = backup_database(
            self.backup_name.get()
        )

        if result:

            messagebox.showinfo(
                "Backup",
                "Backup wurde erfolgreich erstellt."
            )

        else:

            messagebox.showwarning(
                "Backup",
                "Backup konnte nicht erstellt werden."
            )


    def open_backup_folder(self):

        backup_dir = "backups"

        os.makedirs(
            backup_dir,
            exist_ok=True
        )

        try:
            subprocess.Popen(
                ["xdg-open", os.path.abspath(backup_dir)]
            )

        except Exception as e:
            print(
                "Backup-Ordner konnte nicht geöffnet werden:",
                e
            )


    def toggle_auto_backup(self):

        state = self.auto_backup_enabled.get()

        text = (
            "aktiviert"
            if state
            else "deaktiviert"
        )

        messagebox.showinfo(
            "Backup-System",
            f"Automatische Backups wurden {text}."
        )

        self.save_all_settings()


    # ========================================================
    # MIKROFON
    # ========================================================

    def update_mic_list(self):

        try:

            names = sr.Microphone.list_microphone_names()

        except Exception as e:

            print(
                "Mikrofon-Liste Fehler:",
                e
            )

            names = []

        self.mic_combo["values"] = names

        if names:

            if (
                self.microphone_index is not None
                and 0 <= self.microphone_index < len(names)
            ):

                self.mic_combo.current(
                    self.microphone_index
                )

            else:

                self.mic_combo.current(
                    0
                )

                self.microphone_index = 0

        else:

            self.mic_combo["values"] = [
                "Kein Mikrofon gefunden"
            ]

            self.mic_combo.current(
                0
            )

            self.microphone_index = None


    def on_mic_change(self, event):

        self.microphone_index = (
            self.mic_combo.current()
        )

        self.log(
            f"Soundkarte gewechselt zu: "
            f"{self.mic_combo.get()}"
        )

        self.save_all_settings()


    # ========================================================
    # DATUM / UHRZEIT
    # ========================================================

    def update_datetime(self):

        now = datetime.datetime.now()

        self.datetime_label.config(
            text=now.strftime(
                "%d.%m.%Y %H:%M:%S"
            )
        )

        try:
            self.dashboard_clock_value.config(text=now.strftime("%H:%M:%S"))
            self.dashboard_qa_value.config(text=str(get_qa_count()))
        except Exception:
            pass

        if self.scheduler_running:

            self.root.after(
                1000,
                self.update_datetime
            )


    # ========================================================
    # WETTERLABEL
    # ========================================================

    def update_weather_label(self):

        def worker():

            weather = get_weather_bad_driburg()

            self.root.after(
                0,
                lambda: self.weather_label.config(
                    text=weather
                )
            )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()


    # ========================================================
    # LOG
    # ========================================================

    def _update_chat_status(self, text):
        try:
            self.chat_status.config(text=text)
        except tk.TclError:
            pass

    def _refresh_speaking_status(self):
        """Setzt den Status nach Ende der Sprachausgabe zuverlässig zurück."""
        try:
            if not SPEAKING and speech_queue.empty():
                # Nur zurücksetzen, wenn zuvor wirklich "SPRICHT" angezeigt wurde.
                current = self.status_label.cget("text")
                if "SPRICHT" in current:
                    if not getattr(self, "_resume_after_answer", False):
                        self.set_assistant_status("ready")
        except (tk.TclError, Exception):
            pass
        finally:
            try:
                if self.root.winfo_exists():
                    self.root.after(200, self._refresh_speaking_status)
            except tk.TclError:
                pass

    def set_assistant_status(self, status, color=None):
        labels = {
            "ready": ("● BEREIT", current_theme["green"], "Bereit für deinen nächsten Befehl"),
            "listening": ("● HÖRT ZU", current_theme["green"], "Ich höre dir zu …"),
            "processing": ("● VERARBEITE", "#4da3ff", "Ich verarbeite deine Anfrage …"),
            "speaking": ("● SPRICHT", "#b57cff", "Ich antworte gerade …"),
        }
        text, default_color, chat_text = labels.get(status, labels["ready"])
        if color is None:
            color = default_color
        try:
            self.status_label.config(text=text, fg=color)
            self.dashboard_state_value.config(text=text.replace("● ", ""))
            self.chat_status.config(text=chat_text)
        except tk.TclError:
            pass

    def _chat_mousewheel(self, event):
        """Scrollt das Chatfenster mit dem Mausrad, ohne andere Bereiche zu stören."""
        try:
            canvas = self.chat_canvas
            if not canvas.winfo_exists():
                return None

            # Mausposition relativ zum Chat-Canvas bestimmen.
            x = event.x_root - canvas.winfo_rootx()
            y = event.y_root - canvas.winfo_rooty()
            if not (0 <= x < canvas.winfo_width() and 0 <= y < canvas.winfo_height()):
                return None

            if getattr(event, "num", None) == 4:
                units = -3
            elif getattr(event, "num", None) == 5:
                units = 3
            else:
                delta = getattr(event, "delta", 0)
                if delta:
                    units = -max(1, int(abs(delta) / 120)) * (1 if delta > 0 else -1)
                else:
                    units = 0

            if units:
                canvas.yview_scroll(units, "units")
                return "break"
        except Exception:
            # Ein Scrollfehler darf das übrige Programm nicht beeinflussen.
            return None
        return None

    def _insert_chat_message(self, speaker, text):
        """Fügt eine deutlich sichtbare Nachricht als moderne Chat-Blase ein."""
        if not text:
            return
        try:
            th = current_theme
            now = datetime.datetime.now().strftime("%H:%M")

            row = tk.Frame(self.chat_messages, bg=th["bg"])
            row.pack(fill=tk.X, padx=12, pady=(7, 0))

            if speaker == "user":
                bubble_bg = "#2563eb"
                name = "DU"
                name_fg = "#ffffff"
                text_fg = "#ffffff"
                anchor = tk.E
                side_pad = (55, 0)
            elif speaker == "assistant":
                bubble_bg = th["bg2"]
                name = "ALI"
                name_fg = th["fg"]
                text_fg = th["fg"]
                anchor = tk.W
                side_pad = (0, 55)
            else:
                bubble_bg = th["accent"]
                name = "SYSTEM"
                name_fg = th["muted"]
                text_fg = th["muted"]
                anchor = tk.CENTER
                side_pad = (35, 35)

            bubble = tk.Frame(row, bg=bubble_bg, padx=14, pady=9,
                              highlightthickness=1, highlightbackground=th["border"] if speaker != "user" else bubble_bg)
            bubble.pack(anchor=anchor, padx=side_pad)

            head = tk.Frame(bubble, bg=bubble_bg)
            head.pack(fill=tk.X)
            tk.Label(head, text=name, font=("TkDefaultFont", 8, "bold"),
                     bg=bubble_bg, fg=name_fg).pack(side=tk.LEFT)
            tk.Label(head, text=now, font=("TkDefaultFont", 7),
                     bg=bubble_bg, fg=name_fg).pack(side=tk.RIGHT, padx=(14, 0))

            tk.Label(bubble, text=str(text).strip(), justify=tk.LEFT, anchor=tk.W,
                     wraplength=310, font=("TkDefaultFont", 10),
                     bg=bubble_bg, fg=text_fg).pack(anchor=tk.W, pady=(4, 0))

            self.chat_canvas.update_idletasks()
            self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
            self.chat_canvas.yview_moveto(1.0)

            # Maximal 40 sichtbare Nachrichten behalten.
            children = self.chat_messages.winfo_children()
            if len(children) > 40:
                for old in children[:-40]:
                    old.destroy()
        except tk.TclError:
            pass

    def log(self, text):
        try:
            message = str(text).strip()
            if not message:
                return

            if message.startswith("Du sagst:"):
                self._insert_chat_message("user", message.split(":", 1)[1].strip())
            elif message.startswith("Assistent:"):
                self._insert_chat_message("assistant", message.split(":", 1)[1].strip())
                self.set_assistant_status("speaking")
            elif message.startswith("Du:"):
                self._insert_chat_message("user", message.split(":", 1)[1].strip())
            else:
                self._insert_chat_message("system", message)

        except tk.TclError:
            pass


    # ========================================================
    # AUFNAHME
    # ========================================================

    def _resume_after_answer_finished(self):
        """Nach einer normalen TTS-Antwort sicher und genau einmal zuhören."""
        if getattr(self, "_manual_stop_latched", False):
            self._resume_after_answer = False
            return
        if not self.scheduler_running or SPEECH_SHUTDOWN.is_set():
            self._resume_after_answer = False
            return

        if is_vlc_running():
            self._resume_after_answer = False
            return

        if SPEAKING or SPEECH_BLOCK_LISTENING.is_set() or not speech_queue.empty():
            self.root.after(150, self._resume_after_answer_finished)
            return

        if self.listen_thread is not None and self.listen_thread.is_alive():
            self.root.after(150, self._resume_after_answer_finished)
            return

        self._resume_after_answer = False
        self.listening = False
        self._stop_requested = False
        self.start_listening()


    def _resume_listening_after_vlc(self):
        """Nach VLC erst dann wieder zuhören, wenn TTS und alter
        Aufnahme-Thread vollständig beendet sind."""
        if not self.scheduler_running or SPEECH_SHUTDOWN.is_set():
            self._resume_after_vlc = False
            return

        if is_vlc_running():
            self.root.after(300, self._resume_listening_after_vlc)
            return

        if SPEAKING or not speech_queue.empty():
            self.root.after(300, self._resume_listening_after_vlc)
            return

        if self.listen_thread is not None and self.listen_thread.is_alive():
            self.root.after(200, self._resume_listening_after_vlc)
            return

        self._resume_after_vlc = False
        self.listening = False
        self._stop_requested = False
        self.start_listening()


    def manual_start_listening(self):
        # Bewusstes STARTEN hebt einen vorherigen manuellen STOPP auf.
        self._manual_stop_latched = False
        # Nur der manuelle START-Button zeigt die Statusmeldung im Chat.
        try:
            self.log("Aufnahme gestartet.")
        except Exception:
            pass
        self.start_listening()


    def _camera_device_is_capture(self, device):
        """Prüft ein /dev/video*-Gerät ohne OpenCV/GStreamer-Warnungen."""
        try:
            import fcntl, struct
            VIDIOC_QUERYCAP = 0x80685600
            V4L2_CAP_VIDEO_CAPTURE = 0x00000001
            V4L2_CAP_VIDEO_CAPTURE_MPLANE = 0x00001000
            fd = os.open(str(device), os.O_RDWR | os.O_NONBLOCK)
            try:
                data = bytearray(104)
                fcntl.ioctl(fd, VIDIOC_QUERYCAP, data, True)
                caps = struct.unpack_from("I", data, 84)[0]
                return bool(caps & (V4L2_CAP_VIDEO_CAPTURE | V4L2_CAP_VIDEO_CAPTURE_MPLANE))
            finally:
                os.close(fd)
        except Exception:
            return False

    def detect_cameras(self):
        """Findet unter Linux nur echte Video-Capture-Geräte."""
        self.camera_indices = []
        devices = sorted(Path("/dev").glob("video[0-9]*"), key=lambda p: int(re.search(r"(\d+)$", p.name).group(1)))
        for device in devices:
            if self._camera_device_is_capture(device):
                self.camera_indices.append(int(re.search(r"(\d+)$", device.name).group(1)))

        if not self.camera_indices:
            self.camera_combo["values"] = ["Keine Kamera gefunden"]
            self.camera_combo.current(0)
            return

        self.camera_combo["values"] = [f"Kamera {i} (/dev/video{i})" for i in self.camera_indices]
        saved = 0
        try:
            cfg = configparser.ConfigParser()
            if os.path.exists(CONFIG_MAIN):
                cfg.read(CONFIG_MAIN, encoding="utf-8")
            saved = get_face_camera_index(cfg)
        except Exception:
            pass
        self.camera_combo.current(self.camera_indices.index(saved) if saved in self.camera_indices else 0)

    def on_camera_selected(self, event=None):
        """Speichert die gewählte Kamera direkt in config.ini."""
        if not self.camera_indices:
            return
        index = self.camera_indices[self.camera_combo.current()]
        try:
            cfg = configparser.ConfigParser()
            if os.path.exists(CONFIG_MAIN):
                cfg.read(CONFIG_MAIN, encoding="utf-8")
            set_face_camera_index(cfg, index)
            with open(CONFIG_MAIN, "w", encoding="utf-8") as f:
                cfg.write(f)
            self.log(f"Kamera gespeichert: /dev/video{index}")
        except Exception as exc:
            self.log(f"Kamera konnte nicht gespeichert werden: {exc}")


    def start_listening(self):

        # Ein automatischer Neustart darf einen manuellen STOPP nicht übergehen.
        if getattr(self, "_manual_stop_latched", False):
            return

        # Bereits laufendes Zuhören nicht doppelt starten.
        with self._listen_lock:
            if self.listening:
                return

        # Während TTS oder wartender Sprachausgabe darf das Mikrofon
        # nicht geöffnet werden. Nach dem Ende wird automatisch neu gestartet.
        if SPEAKING or SPEECH_BLOCK_LISTENING.is_set() or not speech_queue.empty():
            self.root.after(200, self.start_listening)
            return

        # Der alte Aufnahme-Thread muss vollständig beendet sein, bevor
        # ein neuer Thread das Mikrofon öffnet.
        if self.listen_thread is not None and self.listen_thread.is_alive():
            self.listening = False
            self._stop_requested = True
            self.root.after(100, self._restart_listening_when_thread_stopped)
            return

        if is_vlc_running():
            mute_system_mic()
            self.log("VLC ist aktiv – Mikrofon bleibt während der Musik deaktiviert.")
            return

        unmute_system_mic()

        if self.microphone_index is None:
            messagebox.showwarning(
                "Fehler",
                "Keine Soundkarte / kein Mikrofon gefunden."
            )
            return

        with self._listen_lock:
            self.listening = True
            self._stop_requested = False

        try:
            self.set_assistant_status("listening")
        except Exception:
            pass

        self.recognizer = sr.Recognizer()

        thread = threading.Thread(
            target=self._listen_thread_wrapper,
            daemon=True
        )
        self.listen_thread = thread
        thread.start()


    def _restart_listening_when_thread_stopped(self):
        thread = self.listen_thread
        if thread is not None and thread.is_alive():
            self.root.after(100, self._restart_listening_when_thread_stopped)
            return
        self.listen_thread = None
        self.listening = False
        self.start_listening()


    def stop_listening(self):
        # STOPP ist ein harter Abbruch: Aufnahme, laufende TTS und
        # wartende Sprachansagen werden gemeinsam beendet.
        global SPEECH_PROCESS
        with self._listen_lock:
            self.listening = False
            self._stop_requested = True
            self._resume_after_answer = False
            self._manual_stop_latched = True
            self.audio_level = 0

        # Bereits geplante TTS sofort beenden.
        proc = SPEECH_PROCESS
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=0.5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

        # Wartende Ansagen verwerfen, damit nach dem Stop nichts nachgesprochen wird.
        while True:
            try:
                speech_queue.get_nowait()
                speech_queue.task_done()
            except queue.Empty:
                break

        SPEECH_BLOCK_LISTENING.set()

        try:
            self.status_label.configure(text="● BEREIT", fg=current_theme["green"])
        except Exception:
            pass

        self.log("Aufnahme gestoppt.")


    def _listen_thread_wrapper(self):
        try:
            self.listen_loop()
        except Exception as e:
            print("Mikrofon-Thread Fehler:", e)
        finally:
            self.listening = False
            self.audio_level = 0
            self._stop_requested = False
            if self.listen_thread is threading.current_thread():
                self.listen_thread = None
            try:
                self.root.after(0, self._mic_thread_finished)
            except Exception:
                pass


    def listen_loop(self):

        try:

            mic = sr.Microphone(
                device_index=self.microphone_index
            )

        except Exception as e:

            self.root.after(
                0,
                self.log,
                f"Fehler beim Öffnen des Mikrofons: {e}"
            )

            self.listening = False

            return

        with mic as source:

            self.active_mic_source = source

            try:

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.7
                )

            except Exception as e:

                print(
                    "Ambient Noise Fehler:",
                    e
                )


            consecutive_errors = 0

            while self.listening:

                # Während TTS läuft oder Ansagen warten, nichts aufnehmen.
                if SPEECH_BLOCK_LISTENING.is_set() or SPEAKING:
                    self.audio_level = 0
                    time.sleep(0.05)
                    continue

                try:

                    audio = self.recognizer.listen(
                        source,
                        timeout=1,
                        phrase_time_limit=8
                    )

                except sr.WaitTimeoutError:

                    consecutive_errors = 0
                    continue

                except Exception as e:

                    consecutive_errors += 1
                    print(
                        "Aufnahme Fehler:",
                        e
                    )

                    # Nach mehreren Gerätefehlern den Thread beenden.
                    # Dadurch kann START anschließend einen frischen
                    # Mikrofon-Thread erzeugen.
                    if consecutive_errors >= 3:
                        self.root.after(
                            0,
                            self.log,
                            "Mikrofon-Thread wird wegen Gerätefehler neu gestartet."
                        )
                        self.listening = False
                        break

                    time.sleep(0.2)
                    continue

                # TTS kann während listen() gestartet worden sein.
                # Dieses Audio wird dann bewusst verworfen.
                if SPEECH_BLOCK_LISTENING.is_set() or SPEAKING:
                    self.audio_level = 0
                    continue

                # ------------------------------------------------
                # Visualizer
                # ------------------------------------------------

                try:

                    raw = audio.get_raw_data()

                    if raw:

                        values = raw[::150]

                        if values:

                            bass = (
                                sum(
                                    abs(
                                        b - 128
                                    )
                                    for b in values
                                )
                                / max(
                                    1,
                                    len(values)
                                )
                                / 128
                            )

                            peak_values = raw[::80]

                            if peak_values:

                                peaks = max(
                                    abs(
                                        b - 128
                                    )
                                    for b in peak_values
                                ) / 128

                            else:
                                peaks = 0

                            level = (
                                bass * 0.7
                                + peaks * 0.3
                            )

                            self.audio_level = min(
                                1.0,
                                level
                            )

                except Exception:

                    self.audio_level = 0

                # ------------------------------------------------
                # Sprache erkennen
                # ------------------------------------------------

                try:

                    text = self.recognizer.recognize_google(
                        audio,
                        language="de-DE"
                    )

                    # Während der Erkennung kann TTS gestartet worden sein.
                    if SPEECH_BLOCK_LISTENING.is_set() or SPEAKING:
                        continue

                    self.root.after(
                        0,
                        self.log,
                        f"Du sagst: {text}"
                    )
                    self.root.after(0, self.set_assistant_status, "processing")

                    # Genau ein Aufnahmezyklus pro Frage. Nach der Antwort
                    # wird ein frischer Aufnahme-Thread gestartet.
                    self._resume_after_answer = True
                    self.listening = False
                    self._stop_requested = True

                    # WICHTIG:
                    # handle_question läuft im Tkinter-Hauptthread.
                    self.root.after(
                        0,
                        self.handle_question,
                        text
                    )

                except sr.UnknownValueError:

                    pass

                except sr.RequestError as e:

                    self.root.after(
                        0,
                        self.log,
                        f"Spracherkennung nicht erreichbar: {e}"
                    )

                except Exception as e:

                    print(
                        "Spracherkennung Fehler:",
                        e
                    )


        # Aufnahme-Thread vollständig beendet.
        # Immer freigeben, damit START garantiert wieder einen neuen
        # Thread erzeugen kann.
        self.listen_thread = None

        if not self.listening and not self._resume_after_answer:
            try:
                self.root.after(0, self.set_assistant_status, "ready")
            except Exception:
                pass


    # ========================================================
    # KI / BEFEHLSLOGIK
    # ========================================================

    # ========================================================
    # GESICHTSERKENNUNG
    # ========================================================

    def _face_speak(self, text):
        """Spricht einen kurzen Status und schreibt ihn ins Chatfenster."""
        try:
            self.log(f"Assistent: {text}")
        except Exception:
            pass
        speak_mbrola(text, self.voice, self.speed, self.pitch, self.volume)

    def _face_camera_index(self):
        """Liest die aktuell ausgewählte Kamera aus config.ini."""
        cfg = configparser.ConfigParser()
        if os.path.exists(CONFIG_MAIN):
            cfg.read(CONFIG_MAIN, encoding="utf-8")
        return get_face_camera_index(cfg)

    def _detect_largest_face(self, gray, cascade):
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )
        if len(faces) == 0:
            return None
        return max(faces, key=lambda r: r[2] * r[3])

    def _open_face_camera(self, camera_index):
        """Öffnet eine V4L2-Kamera robust mit mehreren OpenCV-Backends."""
        if cv2 is None:
            return None

        backends = []
        v4l2 = getattr(cv2, "CAP_V4L2", None)
        if v4l2 is not None:
            backends.append(v4l2)
        backends.append(getattr(cv2, "CAP_ANY", 0))

        for backend in dict.fromkeys(backends):
            cap = None
            try:
                cap = cv2.VideoCapture(int(camera_index), backend)
                if not cap.isOpened():
                    if cap is not None:
                        cap.release()
                    continue

                # Viele USB-Webcams liefern über MJPG zuverlässig Bilder;
                # falls das Gerät es nicht unterstützt, bleibt die Kamera
                # trotzdem geöffnet und OpenCV verwendet das vorhandene Format.
                try:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
                except Exception:
                    pass

                # Nicht nur isOpened(), sondern einen echten Frame prüfen.
                for _ in range(8):
                    ok, frame = cap.read()
                    if ok and frame is not None and getattr(frame, "size", 0) > 0:
                        return cap
                    cv2.waitKey(20)

                cap.release()
            except Exception as exc:
                print(f"Kamera /dev/video{camera_index}, Backend {backend}: {exc}")
                if cap is not None:
                    try:
                        cap.release()
                    except Exception:
                        pass

        return None

    def preview_camera(self):
        """Öffnet die ausgewählte Kamera nur zum Testen in einem Vorschaufenster."""
        if cv2 is None:
            messagebox.showwarning("Kamera", "OpenCV ist nicht installiert.", parent=self.root)
            return

        camera_index = self._face_camera_index()

        def worker():
            cap = self._open_face_camera(camera_index)
            if cap is None:
                self.root.after(0, messagebox.showerror, "Kamera",
                                f"Die Kamera /dev/video{camera_index} konnte nicht geöffnet werden.",
                                parent=self.root)
                return

            window_name = "ALI - Kamera Vorschau"
            try:
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(window_name, 800, 600)
                while True:
                    ok, frame = cap.read()
                    if not ok or frame is None:
                        break
                    cv2.putText(frame, "Kamera-Test - Q oder ESC zum Beenden",
                                (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                (0, 255, 0), 2)
                    cv2.imshow(window_name, frame)
                    key = cv2.waitKey(30) & 0xFF
                    if key in (27, ord("q"), ord("Q")):
                        break
            finally:
                cap.release()
                try:
                    cv2.destroyWindow(window_name)
                    cv2.waitKey(1)
                except Exception:
                    pass

        threading.Thread(target=worker, name="CameraPreview", daemon=True).start()

    def _capture_face_photo(self):
        """Öffnet die ausgewählte Kamera sichtbar und nimmt ein Gesichtsfoto auf."""
        if cv2 is None:
            return None, "OpenCV ist nicht installiert."

        camera_index = self._face_camera_index()
        cap = self._open_face_camera(camera_index)
        if cap is None:
            return None, f"Die Kamera /dev/video{camera_index} konnte nicht geöffnet werden."

        # Haar-Cascade robust suchen.
        cascade_filename = "haarcascade_frontalface_default.xml"
        candidates = [
            Path(__file__).resolve().parent / cascade_filename,
            Path(__file__).resolve().parent / "data" / "haarcascades" / cascade_filename,
            Path("/usr/share/opencv4/haarcascades") / cascade_filename,
            Path("/usr/share/opencv/haarcascades") / cascade_filename,
            Path("/usr/local/share/opencv4/haarcascades") / cascade_filename,
            Path("/usr/local/share/opencv/haarcascades") / cascade_filename,
        ]
        cv2_data = getattr(cv2, "data", None)
        haar_dir = getattr(cv2_data, "haarcascades", None)
        if haar_dir:
            candidates.insert(0, Path(haar_dir) / cascade_filename)

        cascade_path = next((p for p in candidates if p.is_file()), None)
        if cascade_path is None:
            cap.release()
            return None, f"Die Datei für die Gesichtserkennung wurde nicht gefunden: {cascade_filename}"

        try:
            cascade = cv2.CascadeClassifier(str(cascade_path))
            if cascade.empty():
                cap.release()
                return None, "Der Gesichtserkennungs-Klassifikator konnte nicht geladen werden."
        except Exception as exc:
            cap.release()
            return None, f"Gesichtserkennung konnte nicht gestartet werden: {exc}"

        self._face_speak("Bitte schaue kurz in die Kamera.")
        face_image = None
        deadline = time.time() + 15
        window_name = "ALI - Gesicht aufnehmen"

        try:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 800, 600)

            while time.time() < deadline:
                ok, frame = cap.read()
                if not ok:
                    cv2.waitKey(30)
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face = self._detect_largest_face(gray, cascade)
                display = frame.copy()

                if face is not None:
                    x, y, w, h = face
                    cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(
                        display, "Gesicht erkannt - Foto wird aufgenommen",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
                    )
                    face_image = gray[y:y+h, x:x+w].copy()
                    cv2.imshow(window_name, display)
                    cv2.waitKey(500)
                    break

                cv2.putText(
                    display, "Bitte schaue in die Kamera",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2
                )
                cv2.imshow(window_name, display)
                key = cv2.waitKey(30) & 0xFF
                if key in (27, ord("q"), ord("Q")):
                    return None, "Die Fotoaufnahme wurde abgebrochen."
        finally:
            cap.release()
            try:
                cv2.destroyWindow(window_name)
                cv2.waitKey(1)
            except Exception:
                pass

        if face_image is None:
            return None, "Ich konnte in der Kamera kein Gesicht erkennen."

        face_image = cv2.resize(face_image, (200, 200), interpolation=cv2.INTER_AREA)
        face_image = cv2.equalizeHist(face_image)
        return face_image, None


    def _face_opencv_ready(self):
        """Prüft die für Plan Go benötigten OpenCV-4.10-Funktionen."""
        return (
            cv2 is not None
            and hasattr(cv2, "CascadeClassifier")
            and hasattr(cv2, "face")
            and hasattr(cv2.face, "LBPHFaceRecognizer_create")
        )

    def _resume_microphone_after_face(self):
        """Nach Kamera-/Gesichtserkennung das normale Mikro wieder aktivieren."""
        try:
            # Kamera/OpenCV-Fenster sicher schließen.
            if cv2 is not None:
                try:
                    cv2.destroyAllWindows()
                    cv2.waitKey(1)
                except Exception:
                    pass
        except Exception:
            pass

        # Vorhandene Listening-/Microphone-Methoden der Anwendung nutzen.
        for method_name in (
            "start_listening",
            "start_microphone",
            "enable_microphone",
            "resume_listening",
            "listen_start",
        ):
            method = getattr(self, method_name, None)
            if callable(method):
                try:
                    method()
                    return
                except TypeError:
                    try:
                        method(True)
                        return
                    except Exception:
                        pass
                except Exception:
                    pass

        # Falls das Programm über einen Tkinter after-Loop arbeitet,
        # die normale Frage-/Listening-Schleife erneut anstoßen.
        for method_name in ("listen", "start_listening_loop", "poll_microphone"):
            method = getattr(self, method_name, None)
            if callable(method):
                try:
                    method()
                    return
                except Exception:
                    pass


    def open_face_management(self):
        """Verwaltet gespeicherte Gesichter inklusive Bildvorschau."""
        if cv2 is None:
            self._face_speak("Für die Gesichtverwaltung fehlt OpenCV.")
            return

        import tkinter as tk
        from tkinter import messagebox, simpledialog

        win = tk.Toplevel(self.root)
        win.title("Gesichtserkennung verwalten")
        win.geometry("900x600")
        try:
            win.configure(bg=current_theme["bg"])
        except Exception:
            pass

        ttk.Label(
            win,
            text="Gespeicherte Gesichter",
            font=("TkDefaultFont", 16, "bold")
        ).pack(pady=(15, 8))

        main = ttk.Frame(win)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = ttk.LabelFrame(main, text="Bildvorschau", padding=12)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))

        listbox = tk.Listbox(left, font=("TkDefaultFont", 13), height=16)
        listbox.pack(fill=tk.BOTH, expand=True)

        preview_label = ttk.Label(
            right,
            text="Keine Person ausgewählt",
            anchor="center",
            justify="center"
        )
        preview_label.pack(padx=10, pady=10)

        preview_name = ttk.Label(
            right,
            text="",
            font=("TkDefaultFont", 13, "bold"),
            anchor="center"
        )
        preview_name.pack(pady=(0, 10))

        # Referenz auf PhotoImage halten, sonst verschwindet das Bild unter Tkinter.
        preview_label._photo = None

        base_dir = Path(__file__).resolve().parent
        cfg = configparser.ConfigParser()

        def load_cfg():
            cfg.clear()
            if os.path.exists(CONFIG_MAIN):
                cfg.read(CONFIG_MAIN, encoding="utf-8")

        def records():
            return load_face_records(cfg, base_dir)

        def show_preview(event=None):
            items = records()
            sel = listbox.curselection()
            if not sel or sel[0] >= len(items):
                preview_label.configure(image="", text="Keine Person ausgewählt")
                preview_label._photo = None
                preview_name.configure(text="")
                return

            name, image_path = items[sel[0]]
            preview_name.configure(text=name)

            try:
                image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
                if image is None:
                    raise RuntimeError("Bild konnte nicht gelesen werden.")

                # Für die Vorschau vergrößern und in RGB umwandeln.
                image = cv2.resize(image, (320, 320), interpolation=cv2.INTER_AREA)
                rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

                from PIL import Image, ImageTk
                pil_image = Image.fromarray(rgb)
                photo = ImageTk.PhotoImage(pil_image)

                preview_label.configure(image=photo, text="")
                preview_label._photo = photo
            except Exception as exc:
                preview_label.configure(
                    image="",
                    text=f"Bild nicht verfügbar\n\n{exc}"
                )
                preview_label._photo = None

        def refresh():
            load_cfg()
            listbox.delete(0, tk.END)
            for name, image_path in records():
                exists = Path(image_path).is_file()
                listbox.insert(tk.END, f"{'✓' if exists else '⚠'}  {name}")
            show_preview()

        def current_record():
            items = records()
            sel = listbox.curselection()
            if not sel or sel[0] >= len(items):
                messagebox.showinfo(
                    "Gesicht",
                    "Bitte zuerst eine Person auswählen.",
                    parent=win
                )
                return None
            return items[sel[0]]

        def save_config():
            with open(CONFIG_MAIN, "w", encoding="utf-8") as f:
                cfg.write(f)

        def rename():
            item = current_record()
            if not item:
                return
            old_name, _ = item
            new_name = simpledialog.askstring(
                "Name ändern",
                "Neuer Name:",
                initialvalue=old_name,
                parent=win
            )
            if not new_name:
                return
            new_name = re.sub(
                r"[^A-Za-z0-9äöüÄÖÜß _-]",
                "",
                new_name.strip()
            )[:60]
            if not new_name:
                return

            for sec in cfg.sections():
                if cfg.has_option(sec, "name") and cfg.get(sec, "name") == old_name:
                    cfg.set(sec, "name", new_name)
                    save_config()
                    refresh()
                    return

        def delete():
            item = current_record()
            if not item:
                return
            name, image_path = item
            if not messagebox.askyesno(
                "Gesicht löschen",
                f"Das Gesicht von „{name}“ wirklich löschen?",
                parent=win
            ):
                return

            try:
                Path(image_path).unlink(missing_ok=True)
            except Exception as exc:
                messagebox.showwarning(
                    "Gesicht",
                    f"Das Bild konnte nicht gelöscht werden:\n{exc}",
                    parent=win
                )

            for sec in list(cfg.sections()):
                if cfg.has_option(sec, "name") and cfg.get(sec, "name") == name:
                    cfg.remove_section(sec)
            save_config()
            refresh()

        def add_person():
            win.destroy()
            self.handle_remember_face()

        def replace_photo():
            item = current_record()
            if not item:
                return
            name, image_path = item

            self._face_speak(f"Bitte schaue für {name} in die Kamera.")
            face_image, error = self._capture_face_photo()
            if face_image is None:
                messagebox.showerror(
                    "Gesicht",
                    error or "Das Foto konnte nicht aufgenommen werden.",
                    parent=win
                )
                return

            try:
                if not cv2.imwrite(str(image_path), face_image):
                    raise RuntimeError("Das Bild konnte nicht geschrieben werden.")
            except Exception as exc:
                messagebox.showerror(
                    "Gesicht",
                    f"Neues Foto konnte nicht gespeichert werden:\n{exc}",
                    parent=win
                )
                return

            self._face_speak(f"Das Foto von {name} wurde aktualisiert.")
            refresh()

        listbox.bind("<<ListboxSelect>>", show_preview)

        buttons = ttk.Frame(win)
        buttons.pack(fill=tk.X, padx=20, pady=(0, 15))

        ttk.Button(
            buttons, text="Person hinzufügen", command=add_person
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            buttons, text="Foto ersetzen", command=replace_photo
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            buttons, text="Name ändern", command=rename
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            buttons, text="Löschen", command=delete
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            buttons, text="Aktualisieren", command=refresh
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            buttons, text="Schließen", command=win.destroy
        ).pack(side=tk.RIGHT, padx=4)

        refresh()

    def handle_remember_face(self):
        try:
            if not self._face_opencv_ready():
                self._face_speak(
                    "Die Gesichtserkennung ist auf diesem Raspberry Pi noch nicht vollständig verfügbar."
                )
                return

            """Speichert ein Gesicht separat und nur die Zuordnung in config.ini."""
            self.stop_listening()

            if cv2 is None:
                self._face_speak("Für die Gesichtserkennung fehlt OpenCV.")
                return

            records_cfg = configparser.ConfigParser()
            if os.path.exists(CONFIG_MAIN):
                records_cfg.read(CONFIG_MAIN, encoding="utf-8")

            self._face_speak("Wie heißt du?")
            name = simpledialog.askstring("Gesicht merken", "Wie heißt du?", parent=self.root)
            if not name or not name.strip():
                self._face_speak("Okay, ich speichere kein Gesicht.")
                return
            name = re.sub(r"[^A-Za-z0-9äöüÄÖÜß _-]", "", name.strip())[:60]
            if not name:
                self._face_speak("Der Name ist nicht gültig.")
                return

            face_image, error = self._capture_face_photo()
            if face_image is None:
                self._face_speak(error or "Das Foto konnte nicht aufgenommen werden.")
                return

            folder = face_directory(Path(__file__).resolve().parent)
            safe = re.sub(r"[^A-Za-z0-9äöüÄÖÜß_-]+", "_", name).strip("_") or "person"
            image_path = folder / f"{safe}.jpg"
            counter = 2
            while image_path.exists():
                image_path = folder / f"{safe}_{counter}.jpg"
                counter += 1

            if not cv2.imwrite(str(image_path), face_image):
                self._face_speak("Das Gesicht konnte nicht gespeichert werden.")
                return

            save_face_record(
                records_cfg,
                Path(__file__).resolve().parent,
                name,
                image_path
            )
            with open(CONFIG_MAIN, "w", encoding="utf-8") as f:
                records_cfg.write(f)

            self._face_speak(f"Alles klar. Ich merke mir dein Gesicht als {name}.")

        finally:
            self._resume_microphone_after_face()
    def handle_identify_face(self):
        try:
            """Vergleicht das aktuelle Gesicht mit den separat gespeicherten Gesichtern."""
            self.stop_listening()

            if cv2 is None or not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
                self._face_speak(
                    "Die Gesichtserkennung ist noch nicht vollständig installiert. "
                    "Dafür wird die OpenCV-Contrib-Version benötigt."
                )
                return

            cfg = configparser.ConfigParser()
            if os.path.exists(CONFIG_MAIN):
                cfg.read(CONFIG_MAIN, encoding="utf-8")
            records = load_face_records(cfg, Path(__file__).resolve().parent)

            if not records:
                self._face_speak("Ich habe noch kein gespeichertes Gesicht.")
                return

            face_image, error = self._capture_face_photo()
            if face_image is None:
                self._face_speak(error or "Ich konnte dein Gesicht nicht erkennen.")
                return

            images = []
            labels = []
            names = {}
            label = 0
            for name, image_path in records:
                stored = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
                if stored is None:
                    continue
                stored = cv2.resize(stored, (200, 200), interpolation=cv2.INTER_AREA)
                stored = cv2.equalizeHist(stored)
                images.append(stored)
                labels.append(label)
                names[label] = name
                label += 1

            if not images:
                self._face_speak("Die gespeicherten Gesichtsbilder konnten nicht gelesen werden.")
                return

            recognizer = cv2.face.LBPHFaceRecognizer_create(
                radius=1, neighbors=8, grid_x=8, grid_y=8
            )
            recognizer.train(images, __import__('numpy').array(labels, dtype='int32'))
            predicted, confidence = recognizer.predict(face_image)

            # Bei LBPH bedeutet ein kleinerer Wert eine bessere Übereinstimmung.
            # 70 ist bewusst konservativ; bei einem Wert darüber gilt das Gesicht
            # als unbekannt und es wird nicht geraten.
            if predicted in names and confidence <= 70.0:
                self._face_speak(f"Ja. Du bist {names[predicted]}.")
                return

            self._face_speak("Ich erkenne dich nicht in meinen gespeicherten Gesichtern.")
            if messagebox.askyesno(
                "Gesicht unbekannt",
                "Ich kenne dieses Gesicht noch nicht. Soll ich ein Foto speichern?",
                parent=self.root
            ):
                self.handle_remember_face()

        finally:
            self._resume_microphone_after_face()

    # ========================================================
    # TERMINPLANER / ERINNERUNGEN
    # ========================================================

    def _termin_load(self):
        """Lädt Erinnerungen aus einer stabilen Datei neben dem Programm."""
        candidates = [
            Path(self.reminders_file),
            Path.cwd() / "erinnerungen.json",
        ]

        data = None
        source = None
        for path in candidates:
            try:
                if path.exists():
                    raw = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(raw, list):
                        data = raw
                        source = path
                        break
            except Exception as exc:
                self.log(f"Erinnerungen konnten nicht aus {path} geladen werden: {exc}")

        self.reminders = data or []

        # Ältere Termin-Dateien auf das aktuelle Speicherziel übernehmen.
        if source is not None and Path(self.reminders_file) != source:
            try:
                Path(self.reminders_file).write_text(
                    json.dumps(self.reminders, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
            except Exception:
                pass

        self._termin_normalize_loaded()
        return self.reminders

    def _termin_normalize_loaded(self):
        """Normalisiert auch ältere Einträge, damit sie in der Verwaltung erscheinen."""
        normalized = []
        for item in list(self.reminders):
            if not isinstance(item, dict):
                continue

            text = str(
                item.get("text")
                or item.get("anliegen")
                or item.get("reminder")
                or ""
            ).strip()

            due_at = item.get("due_at")
            if due_at:
                try:
                    due = datetime.datetime.fromisoformat(str(due_at))
                    item["due_at"] = due.isoformat()
                except Exception:
                    due_at = None

            # Ältere Versionen hatten teils nur eine Uhrzeit.
            if not due_at:
                raw_time = str(item.get("time") or item.get("uhrzeit") or "").strip()
                parsed = self._parse_reminder_time(raw_time)
                if parsed:
                    hour, minute, _ = parsed
                    now = datetime.datetime.now()
                    due = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if due <= now:
                        due += datetime.timedelta(days=1)
                    item["due_at"] = due.isoformat()

            if text and item.get("due_at"):
                item["text"] = text
                # show = darf dieser Termin angezeigt/erinnert werden?
                # fired = Erinnerung wurde bereits einmal ausgelöst.
                item["show"] = bool(item.get("show", True))
                item["fired"] = bool(item.get("fired", False))
                normalized.append(item)

        self.reminders = normalized

    def _save_reminders(self):
        """Atomar speichern, damit die Termine beim nächsten Start erhalten bleiben."""
        try:
            target = Path(self.reminders_file)
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = Path(str(target) + ".tmp")
            tmp.write_text(
                json.dumps(self.reminders, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            os.replace(str(tmp), str(target))
        except Exception as exc:
            self.log(f"Erinnerungen konnten nicht gespeichert werden: {exc}")

    def _parse_reminder_time(self, text):
        """Erkennt 4 Uhr, 18 Uhr, 18 Uhr 30, 18:30, 18.30 und 1830."""
        t = str(text or "").lower().strip()

        # 18:30 / 18.30
        m = re.search(r'\b(?:um\s*)?(\d{1,2})\s*[:.]\s*(\d{2})\s*(?:uhr)?\b', t)
        if m:
            hour, minute = int(m.group(1)), int(m.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return hour, minute, m.span()

        # 18 Uhr / 4 Uhr
        m = re.search(r'\b(?:um\s*)?(\d{1,2})\s*uhr\b', t)
        if m:
            hour = int(m.group(1))
            if 0 <= hour <= 23:
                return hour, 0, m.span()

        # 1830 / 400
        m = re.search(r'\b(?:um\s*)?(\d{3,4})\b', t)
        if m:
            digits = m.group(1)
            if len(digits) == 3:
                hour, minute = int(digits[0]), int(digits[1:])
            else:
                hour, minute = int(digits[:2]), int(digits[2:])
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return hour, minute, m.span()

        # Gesprochene Zahlen – wichtig für "vier Uhr", wenn die
        # Spracherkennung das Wort statt der Ziffer liefert.
        number_words = {
            "eins": 1, "ein": 1, "eine": 1, "zwei": 2, "drei": 3, "vier": 4,
            "fünf": 5, "funf": 5, "sechs": 6, "sieben": 7, "acht": 8,
            "neun": 9, "zehn": 10, "elf": 11, "zwölf": 12, "zwolf": 12,
            "dreizehn": 13, "vierzehn": 14, "fünfzehn": 15, "funfzehn": 15,
            "sechzehn": 16, "siebzehn": 17, "achtzehn": 18, "neunzehn": 19,
            "zwanzig": 20, "einundzwanzig": 21, "zweiundzwanzig": 22,
            "dreiundzwanzig": 23,
        }

        for word, hour in number_words.items():
            m = re.search(rf'\b{re.escape(word)}\s*uhr\b', t)
            if m:
                return hour, 0, m.span()

        # "halb sieben" usw.
        half = {
            "zwei": 1, "drei": 2, "vier": 3, "fünf": 4, "funf": 4,
            "sechs": 5, "sieben": 6, "acht": 7, "neun": 8, "zehn": 9,
            "elf": 10, "zwölf": 11, "zwolf": 11
        }
        for word, hour in half.items():
            phrase = f"halb {word}"
            if phrase in t:
                pos = t.find(phrase)
                return hour, 30, (pos, pos + len(phrase))

        return None

    def _parse_reminder_date(self, text):
        """Erkennt heute, morgen, übermorgen sowie deutsche Datumsangaben."""
        t = str(text or "").lower().strip()
        today = datetime.datetime.now().date()

        if t in {"heute", "heut"}:
            return today
        if t in {"morgen", "morgens"}:
            return today + datetime.timedelta(days=1)
        if t in {"übermorgen", "uebermorgen"}:
            return today + datetime.timedelta(days=2)

        month_names = {
            "januar": 1, "februar": 2, "märz": 3, "maerz": 3,
            "april": 4, "mai": 5, "juni": 6, "juli": 7,
            "august": 8, "september": 9, "oktober": 10,
            "november": 11, "dezember": 12,
        }

        # 02.09.2026 / 2.9.2026 / 02/09/2026
        m = re.search(r'\b(?:am\s*)?(\d{1,2})[./-](\d{1,2})(?:[./-](\d{2,4}))?\b', t)
        if m:
            day, month = int(m.group(1)), int(m.group(2))
            year = int(m.group(3)) if m.group(3) else today.year
            if year < 100:
                year += 2000
            try:
                result = datetime.date(year, month, day)
            except ValueError:
                return None
            if not m.group(3) and result < today:
                result = datetime.date(year + 1, month, day)
            return result

        # 2. September 2026 / 2. September
        month_pattern = "|".join(re.escape(name) for name in month_names)
        m = re.search(rf'\b(?:am\s*)?(\d{{1,2}})\.?\s+({month_pattern})(?:\s+(\d{{4}}))?\b', t)
        if m:
            day = int(m.group(1))
            month = month_names[m.group(2)]
            year = int(m.group(3)) if m.group(3) else today.year
            try:
                result = datetime.date(year, month, day)
            except ValueError:
                return None
            if not m.group(3) and result < today:
                result = datetime.date(year + 1, month, day)
            return result

        return None

    def _termin_is_cancel(self, text):
        return str(text or "").strip().lower() in {
            "abbrechen", "abbruch", "stopp", "stop", "cancel",
            "vergiss es", "doch nicht"
        }

    def _termin_start(self):
        self._termin_listening_before_speak = bool(getattr(self, "listening", False))
        self._termin_mode = "date"
        self._termin_pending_date = None
        self._termin_pending_time = None
        self._termin_pending_text = None

        answer = "Für welches Datum soll ich dich erinnern?"
        self.log(f"Assistent: {answer}")
        self._resume_after_answer = True
        speak_mbrola(answer, self.voice, self.speed, self.pitch, self.volume)

    def _termin_cancel(self):
        self._termin_mode = None
        self._termin_pending_date = None
        self._termin_pending_time = None
        self._termin_pending_text = None
        self._resume_after_answer = True

        answer = "Terminplanung abgebrochen."
        self.log(f"Assistent: {answer}")
        speak_mbrola(answer, self.voice, self.speed, self.pitch, self.volume)

    def _termin_confirm(self, h, mi, text, due):
        self._termin_mode = "confirm"
        self._termin_pending_time = (h, mi, due)
        self._termin_pending_text = text

        w = tk.Toplevel(self.root)
        self._termin_confirm_window = w
        w.title("Termin bestätigen")
        w.geometry("580x315")
        w.transient(self.root)
        w.grab_set()

        th = current_theme
        w.configure(bg=th["bg"])

        tk.Label(
            w, text="TERMIN ÜBERPRÜFEN",
            font=("TkDefaultFont", 16, "bold"),
            bg=th["bg"], fg=th["fg"]
        ).pack(pady=(22, 10))

        today = datetime.datetime.now().date()
        if due.date() == today:
            day = "heute"
        elif due.date() == today + datetime.timedelta(days=1):
            day = "morgen"
        else:
            day = due.strftime("%d.%m.%Y")

        tk.Label(
            w, text=f"{day} um {h:02d}:{mi:02d} Uhr",
            font=("TkDefaultFont", 14, "bold"),
            bg=th["bg"], fg=th["fg"]
        ).pack(pady=3)

        tk.Label(
            w, text=f"Erinnerung: {text}",
            wraplength=520, justify=tk.CENTER,
            font=("TkDefaultFont", 12),
            bg=th["bg"], fg=th["fg"]
        ).pack(pady=8)

        tk.Label(
            w, text="Ist alles richtig?",
            font=("TkDefaultFont", 12, "bold"),
            bg=th["bg"], fg=th["fg"]
        ).pack(pady=5)

        buttons = tk.Frame(w, bg=th["bg"])
        buttons.pack(fill=tk.X, padx=28, pady=18)

        tk.Button(
            buttons, text="JA – SPEICHERN",
            command=self._termin_confirm_yes,
            font=("TkDefaultFont", 11, "bold"),
            padx=20, pady=11,
            bg=th["green"], fg="#ffffff",
            relief="flat", bd=0, cursor="hand2"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        tk.Button(
            buttons, text="ABBRECHEN",
            command=self._termin_confirm_no,
            font=("TkDefaultFont", 11, "bold"),
            padx=20, pady=11,
            bg=th["accent"], fg=th["fg"],
            relief="flat", bd=0, cursor="hand2"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        answer = f"Ich habe den Termin für {day} um {h:02d}:{mi:02d} Uhr eingetragen: {text}. Ist alles richtig?"
        self.log(f"Assistent: {answer}")
        self._resume_after_answer = False
        speak_mbrola(answer, self.voice, self.speed, self.pitch, self.volume)

    def _termin_confirm_yes(self):
        if self._termin_mode != "confirm" or not self._termin_pending_time:
            return

        h, mi, due = self._termin_pending_time
        text = self._termin_pending_text

        self.reminders.append({
            "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "due_at": due.isoformat(),
            "time": f"{h:02d}:{mi:02d}",
            "text": text,
            "show": True,
            "fired": False,
            "created_at": datetime.datetime.now().isoformat(),
        })
        self._save_reminders()

        try:
            self._termin_confirm_window.destroy()
        except Exception:
            pass

        self._termin_confirm_window = None
        self._termin_mode = None
        self._termin_pending_date = None
        self._termin_pending_time = None
        self._termin_pending_text = None

        answer = f"Alles klar. Ich erinnere dich am {due.strftime('%d.%m.%Y')} um {h:02d}:{mi:02d} Uhr daran: {text}."
        self.log(f"Assistent: {answer}")
        self._resume_after_answer = True
        speak_mbrola(answer, self.voice, self.speed, self.pitch, self.volume)
        self._termin_update_dashboard_indicator()

    def _termin_confirm_no(self):
        try:
            self._termin_confirm_window.destroy()
        except Exception:
            pass

        self._termin_confirm_window = None
        self._termin_mode = None
        self._termin_pending_date = None
        self._termin_pending_time = None
        self._termin_pending_text = None

        answer = "Der Termin wurde nicht gespeichert."
        self.log(f"Assistent: {answer}")
        self._resume_after_answer = True
        speak_mbrola(answer, self.voice, self.speed, self.pitch, self.volume)

    def _termin_update_dashboard_indicator(self):
        """Zeigt eine echte, gut sichtbare Glocke nur bei anstehendem Termin."""
        try:
            c = self._termin_bell_canvas
        except AttributeError:
            return

        th = current_theme
        c.delete("all")
        c.configure(bg=th["bg2"])

        now = datetime.datetime.now()
        upcoming = False
        for r in self.reminders:
            try:
                if (
                    datetime.datetime.fromisoformat(str(r["due_at"])) > now
                    and r.get("show", True)
                ):
                    upcoming = True
                    break
            except Exception:
                continue

        if not upcoming:
            self._termin_bell_visible = False
            return

        self._termin_bell_visible = True
        fg = th["green"]

        # Große, vollständig sichtbare Glocke.
        # Sie wird absichtlich nicht als Emoji dargestellt.
        c.create_arc(
            11, 6, 43, 38, start=0, extent=180,
            style=tk.ARC, outline=fg, width=4
        )
        c.create_line(11, 22, 11, 30, fill=fg, width=4)
        c.create_line(43, 22, 43, 30, fill=fg, width=4)
        c.create_arc(
            8, 24, 46, 39, start=0, extent=180,
            style=tk.ARC, outline=fg, width=4
        )
        c.create_oval(24, 37, 30, 43, fill=fg, outline=fg)
        c.create_text(
            27, 6, text="!",
            fill=fg, font=("TkDefaultFont", 9, "bold")
        )

    def _check_reminders(self):
        """Prüft jede Sekunde auf fällige Erinnerungen."""
        try:
            now = datetime.datetime.now()
            due = []

            for reminder in self.reminders:
                try:
                    due_at = datetime.datetime.fromisoformat(str(reminder["due_at"]))
                except Exception:
                    continue

                # Vergangene Termine bleiben erhalten. Nur die einmalige
                # Erinnerung wird mit "fired" als bereits angesagt markiert.
                if (
                    now >= due_at
                    and not reminder.get("fired", False)
                    and reminder.get("show", True)
                ):
                    due.append(reminder)

            if due:
                # NICHT aus self.reminders entfernen.
                # So bleiben vergangene Termine in der Verwaltung erhalten.
                reminder = due[0]
                reminder["fired"] = True
                self._save_reminders()

                # Nicht mehrere Ansagen gleichzeitig starten.
                if not SPEAKING and speech_queue.empty():
                    # Wenn das Mikrofon vor der Erinnerung aktiv war, wird
                    # der laufende Aufnahmezyklus jetzt sauber beendet.
                    # Sonst kann nach der TTS-Ansage ein alter Aufnahme-Thread
                    # plus der automatische Neustart zusammentreffen – dann
                    # musste STOP bisher manchmal zweimal gedrückt werden.
                    self._termin_listening_before_speak = bool(
                        getattr(self, "listening", False)
                    )
                    self._resume_after_answer = self._termin_listening_before_speak

                    if self._termin_listening_before_speak:
                        with self._listen_lock:
                            self.listening = False
                            self._stop_requested = True
                            self.audio_level = 0
                        try:
                            self.set_assistant_status("speaking")
                        except Exception:
                            pass

                    answer = f"Erinnerung: Du wolltest {reminder.get('text', 'etwas erledigen')}."
                    self.log(f"Assistent: {answer}")
                    speak_mbrola(
                        answer, self.voice, self.speed, self.pitch, self.volume
                    )

            self._termin_update_dashboard_indicator()

        except Exception as exc:
            self.log(f"Erinnerungsprüfung Fehler: {exc}")

        finally:
            if getattr(self, "scheduler_running", True):
                self.root.after(1000, self._check_reminders)

    def open_terminverwaltung(self):
        """Terminverwaltung: vorhandene Termine anzeigen, bearbeiten und löschen."""
        # Immer frisch von der Datei laden, damit auch bereits vorhandene
        # Termine aus vorherigen Starts/Versionen erscheinen.
        self._termin_load()

        content = self._show_page("Terminverwaltung", "Termine anzeigen, bearbeiten, hinzufügen und löschen")
        w = content
        th = current_theme

        list_frame = tk.Frame(w, bg=th["bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        lb = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("TkDefaultFont", 11),
            bg=th["bg2"], fg=th["fg"],
            selectbackground=th["selected"],
            selectforeground="#ffffff"
        )
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=lb.yview)

        def display_time(item):
            try:
                d = datetime.datetime.fromisoformat(str(item.get("due_at", "")))
                return d.strftime("%d.%m.%Y %H:%M")
            except Exception:
                return str(item.get("time") or item.get("uhrzeit") or "unbekannte Zeit")

        def display_text(item):
            return str(
                item.get("text")
                or item.get("anliegen")
                or item.get("reminder")
                or ""
            )

        def display_status(item):
            try:
                due = datetime.datetime.fromisoformat(str(item.get("due_at", "")))
                if item.get("fired", False):
                    return "ERLEDIGT"
                if due <= datetime.datetime.now():
                    return "ABGELAUFEN"
                if not item.get("show", True):
                    return "AUS"
                return "AKTIV"
            except Exception:
                return "AUS" if not item.get("show", True) else "AKTIV"

        def refresh():
            # Vor jeder Anzeige frisch laden.
            self._termin_load()
            lb.delete(0, tk.END)
            for item in self.reminders:
                lb.insert(
                    tk.END,
                    f"[{display_status(item)}]  {display_time(item)}  –  {display_text(item)}"
                )

            self._termin_update_dashboard_indicator()

        def edit():
            sel = lb.curselection()
            if not sel:
                messagebox.showinfo(
                    "Terminverwaltung",
                    "Bitte zuerst einen Termin auswählen.",
                    parent=self.root
                )
                return

            index = sel[0]
            item = self.reminders[index]

            try:
                due = datetime.datetime.fromisoformat(str(item.get("due_at", "")))
                default_date = due.strftime("%d.%m.%Y")
                default_time = due.strftime("%H:%M")
            except Exception:
                default_date = datetime.datetime.now().strftime("%d.%m.%Y")
                default_time = str(item.get("time") or item.get("uhrzeit") or "")

            dlg = tk.Toplevel(w)
            dlg.title("Termin bearbeiten")
            dlg.geometry("500x330")
            dlg.transient(self.root)
            dlg.grab_set()
            dlg.configure(bg=th["bg"])

            tk.Label(
                dlg, text="Datum (z. B. 02.09.2026):",
                bg=th["bg"], fg=th["fg"]
            ).pack(anchor="w", padx=15, pady=(16, 4))

            date_var = tk.StringVar(value=default_date)
            tk.Entry(dlg, textvariable=date_var, font=("TkDefaultFont", 12)).pack(
                fill=tk.X, padx=15
            )

            tk.Label(
                dlg, text="Uhrzeit (z. B. 18:30):",
                bg=th["bg"], fg=th["fg"]
            ).pack(anchor="w", padx=15, pady=(10, 4))

            time_var = tk.StringVar(value=default_time)
            tk.Entry(dlg, textvariable=time_var, font=("TkDefaultFont", 12)).pack(
                fill=tk.X, padx=15
            )

            tk.Label(
                dlg, text="Woran soll ich erinnern?",
                bg=th["bg"], fg=th["fg"]
            ).pack(anchor="w", padx=15, pady=(12, 4))

            text_var = tk.StringVar(value=display_text(item))
            tk.Entry(dlg, textvariable=text_var, font=("TkDefaultFont", 12)).pack(
                fill=tk.X, padx=15
            )

            show_var = tk.BooleanVar(value=bool(item.get("show", True)))
            tk.Checkbutton(
                dlg,
                text="Termin anzeigen / Erinnerung aktiv (alte Termine reaktivieren)",
                variable=show_var,
                bg=th["bg"], fg=th["fg"],
                activebackground=th["bg"], activeforeground=th["fg"],
                selectcolor=th["bg2"]
            ).pack(anchor="w", padx=15, pady=(12, 0))

            def save_edit():
                parsed = self._parse_reminder_time(time_var.get())
                parsed_date = self._parse_reminder_date(date_var.get())
                text = text_var.get().strip()

                if not parsed or not parsed_date or not text:
                    messagebox.showwarning(
                        "Terminverwaltung",
                        "Bitte ein gültiges Datum, eine Uhrzeit und eine Erinnerung eingeben.",
                        parent=dlg
                    )
                    return

                h, mi, _ = parsed
                new_due = datetime.datetime.combine(
                    parsed_date, datetime.time(hour=h, minute=mi)
                )

                item["due_at"] = new_due.isoformat()
                item["time"] = f"{h:02d}:{mi:02d}"
                item["text"] = text
                item["show"] = bool(show_var.get())

                if item["show"]:
                    # Wenn ein alter/erledigter Termin wieder aktiviert wird,
                    # bekommt er die nächste passende Uhrzeit.
                    try:
                        current_due = datetime.datetime.fromisoformat(
                            str(item.get("due_at", ""))
                        )
                    except Exception:
                        current_due = new_due

                    if item.get("fired", False) or current_due <= datetime.datetime.now():
                        next_due = datetime.datetime.now().replace(
                            hour=h, minute=mi, second=0, microsecond=0
                        )
                        if next_due <= datetime.datetime.now():
                            next_due += datetime.timedelta(days=1)
                        item["due_at"] = next_due.isoformat()

                    item["fired"] = False
                else:
                    # Ausgeblendete Termine bleiben gespeichert und werden
                    # erst wieder erinnert, wenn sie aktiviert werden.
                    item["fired"] = False

                self._save_reminders()

                dlg.destroy()
                refresh()

            tk.Button(
                dlg, text="SPEICHERN",
                command=save_edit,
                padx=18, pady=9
            ).pack(side=tk.LEFT, padx=15, pady=20)

            tk.Button(
                dlg, text="ABBRECHEN",
                command=dlg.destroy,
                padx=18, pady=9
            ).pack(side=tk.RIGHT, padx=15, pady=20)

        def _reactivate_if_needed(item):
            """Macht einen alten/erledigten Termin wieder zu einer zukünftigen Erinnerung."""
            try:
                due = datetime.datetime.fromisoformat(str(item.get("due_at", "")))
            except Exception:
                due = datetime.datetime.now()

            now = datetime.datetime.now()

            if item.get("fired", False) or due <= now:
                # Gleiche Uhrzeit, nächste mögliche Ausführung.
                new_due = now.replace(
                    hour=due.hour,
                    minute=due.minute,
                    second=0,
                    microsecond=0
                )
                if new_due <= now:
                    new_due += datetime.timedelta(days=1)

                item["due_at"] = new_due.isoformat()
                item["time"] = new_due.strftime("%H:%M")

            item["fired"] = False
            item["show"] = True

        def toggle_show():
            sel = lb.curselection()
            if not sel:
                messagebox.showinfo(
                    "Terminverwaltung",
                    "Bitte zuerst einen Termin auswählen.",
                    parent=self.root
                )
                return

            item = self.reminders[sel[0]]

            # Ein alter/erledigter Termin gilt unabhängig vom bisherigen
            # show-Wert als "nicht aktiv". Ein einziger Klick aktiviert ihn
            # deshalb direkt wieder. Nur ein aktuell zukünftiger und aktiver
            # Termin wird mit dem gleichen Button ausgeschaltet.
            try:
                current_due = datetime.datetime.fromisoformat(
                    str(item.get("due_at", ""))
                )
            except Exception:
                current_due = datetime.datetime.min

            is_currently_active = (
                bool(item.get("show", True))
                and not bool(item.get("fired", False))
                and current_due > datetime.datetime.now()
            )

            if is_currently_active:
                item["show"] = False
            else:
                _reactivate_if_needed(item)

            self._save_reminders()
            refresh()

        def delete():
            sel = lb.curselection()
            if not sel:
                messagebox.showinfo(
                    "Terminverwaltung",
                    "Bitte zuerst einen Termin auswählen.",
                    parent=self.root
                )
                return

            if messagebox.askyesno(
                "Terminverwaltung",
                "Diesen Termin wirklich löschen?",
                parent=self.root
            ):
                self.reminders.pop(sel[0])
                self._save_reminders()
                refresh()

        buttons = tk.Frame(w, bg=th["bg"])
        buttons.pack(fill=tk.X, padx=16, pady=14)

        def add_new():
            # Neuer Termin über dasselbe Bestätigungsfenster wie bei der Spracheingabe.
            dlg = tk.Toplevel(w)
            dlg.title("Termin hinzufügen")
            dlg.geometry("500x330")
            dlg.transient(self.root)
            dlg.grab_set()
            dlg.configure(bg=th["bg"])

            tk.Label(
                dlg, text="Datum (z. B. 02.09.2026):",
                bg=th["bg"], fg=th["fg"]
            ).pack(anchor="w", padx=15, pady=(16, 4))

            date_var = tk.StringVar(value=datetime.datetime.now().strftime("%d.%m.%Y"))
            tk.Entry(
                dlg, textvariable=date_var, font=("TkDefaultFont", 12)
            ).pack(fill=tk.X, padx=15)

            tk.Label(
                dlg, text="Uhrzeit (z. B. 18:30):",
                bg=th["bg"], fg=th["fg"]
            ).pack(anchor="w", padx=15, pady=(10, 4))

            time_var = tk.StringVar()
            tk.Entry(
                dlg, textvariable=time_var,
                font=("TkDefaultFont", 12)
            ).pack(fill=tk.X, padx=15)

            tk.Label(
                dlg, text="Woran soll ich erinnern?",
                bg=th["bg"], fg=th["fg"]
            ).pack(anchor="w", padx=15, pady=(12, 4))

            text_var = tk.StringVar()
            tk.Entry(
                dlg, textvariable=text_var,
                font=("TkDefaultFont", 12)
            ).pack(fill=tk.X, padx=15)

            def create_new():
                parsed = self._parse_reminder_time(time_var.get())
                parsed_date = self._parse_reminder_date(date_var.get())
                text = text_var.get().strip()

                if not parsed or not parsed_date or not text:
                    messagebox.showwarning(
                        "Termin hinzufügen",
                        "Bitte ein gültiges Datum, eine Uhrzeit und eine Erinnerung eingeben.",
                        parent=dlg
                    )
                    return

                hour, minute, _ = parsed
                due = datetime.datetime.combine(
                    parsed_date, datetime.time(hour=hour, minute=minute)
                )

                if due <= datetime.datetime.now():
                    messagebox.showwarning(
                        "Termin hinzufügen",
                        "Der gewählte Zeitpunkt liegt bereits in der Vergangenheit.",
                        parent=dlg
                    )
                    return

                dlg.destroy()
                self._termin_confirm(hour, minute, text, due)
                # Nach dem Bestätigungsdialog wird die Verwaltung beim
                # nächsten Öffnen bzw. Refresh den neuen Termin anzeigen.

            tk.Button(
                dlg, text="WEITER",
                command=create_new,
                padx=18, pady=9
            ).pack(side=tk.LEFT, padx=15, pady=20)

            tk.Button(
                dlg, text="ABBRECHEN",
                command=dlg.destroy,
                padx=18, pady=9
            ).pack(side=tk.RIGHT, padx=15, pady=20)

        tk.Button(
            buttons, text="TERMIN HINZUFÜGEN",
            command=add_new, padx=18, pady=10
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            buttons, text="BEARBEITEN",
            command=edit, padx=18, pady=10
        ).pack(side=tk.LEFT)

        tk.Button(
            buttons, text="ANZEIGEN AN/AUS",
            command=toggle_show, padx=18, pady=10
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            buttons, text="LÖSCHEN",
            command=delete, padx=18, pady=10
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            buttons, text="SCHLIESSEN",
            command=self.show_dashboard, padx=18, pady=10
        ).pack(side=tk.RIGHT)

        refresh()

    def handle_question(self, question_text):

        self.last_speech_time = time.time()

        original_text = str(question_text or "").strip()
        text_lower = original_text.lower().strip()

        # ====================================================
        # EXPLIZITER BEFEHL: WEBSUCHE STARTEN
        # ====================================================
        # WICHTIG: Dieser Block steht absichtlich ganz am Anfang
        # der Frageverarbeitung. Dadurch kann "starte websuche"
        # nicht vorher vom Programm-Handler abgefangen werden.
        if (
            text_lower in {
                "websuche",
                "web suche",
                "websuche starten",
                "web suche starten",
                "starte websuche",
                "starte web suche"
            }
            or text_lower.startswith("websuche starten ")
            or text_lower.startswith("web suche starten ")
        ):
            self._explicit_web_search_next = True
            answer = "Was möchtest du suchen?"
            self.log(f"Assistent: {answer}")
            speak_mbrola(
                answer,
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )
            return

        # Die nächste erkannte Spracheingabe nach dem Startbefehl
        # wird ausschließlich als Websuchfrage verarbeitet.
        if getattr(self, "_explicit_web_search_next", False):
            self._explicit_web_search_next = False

            web_answer = search_web_answer_extended(original_text)

            if web_answer:
                self.log(f"Websuche: {web_answer}")
                speak_mbrola(
                    web_answer,
                    self.voice,
                    self.speed,
                    self.pitch,
                    self.volume
                )
                self.ask_new_answer_window(
                    original_text,
                    web_answer
                )
                return

            answer = "Ich konnte zu dieser Suche keine richtige Antwort finden."
            self.log(f"Assistent: {answer}")
            speak_mbrola(
                answer,
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )
            return


        # ====================================================
        # TERMINPLANER – immer vor Websuche / Datenbanksuche
        # ====================================================
        if getattr(self, "_termin_mode", None):
            if self._termin_is_cancel(text_lower):
                self._termin_cancel()
                return

            if self._termin_mode == "date":
                parsed_date = self._parse_reminder_date(original_text)
                if not parsed_date:
                    answer = (
                        "Ich habe das Datum nicht verstanden. "
                        "Bitte sage zum Beispiel heute, morgen oder 02.09.2026."
                    )
                    self.log(f"Assistent: {answer}")
                    self._resume_after_answer = True
                    speak_mbrola(
                        answer, self.voice, self.speed, self.pitch, self.volume
                    )
                    return

                self._termin_pending_date = parsed_date
                self._termin_mode = "time"

                answer = "Um welche Uhrzeit soll ich dich erinnern?"
                self.log(f"Assistent: {answer}")
                self._resume_after_answer = True
                speak_mbrola(
                    answer, self.voice, self.speed, self.pitch, self.volume
                )
                return

            if self._termin_mode == "time":
                parsed = self._parse_reminder_time(original_text)
                if not parsed:
                    answer = (
                        "Ich habe die Uhrzeit nicht verstanden. "
                        "Bitte sage zum Beispiel 4 Uhr, 18 Uhr 30 oder 18:30."
                    )
                    self.log(f"Assistent: {answer}")
                    self._resume_after_answer = True
                    speak_mbrola(
                        answer, self.voice, self.speed, self.pitch, self.volume
                    )
                    return

                hour, minute, _ = parsed
                self._termin_pending_time = (hour, minute)
                self._termin_mode = "text"

                answer = "Und woran soll ich dich erinnern?"
                self.log(f"Assistent: {answer}")
                self._resume_after_answer = True
                speak_mbrola(
                    answer, self.voice, self.speed, self.pitch, self.volume
                )
                return

            if self._termin_mode == "text":
                subject = original_text
                if not subject:
                    answer = "Woran soll ich dich erinnern?"
                    self.log(f"Assistent: {answer}")
                    self._resume_after_answer = True
                    speak_mbrola(
                        answer, self.voice, self.speed, self.pitch, self.volume
                    )
                    return

                hour, minute = self._termin_pending_time
                due = datetime.datetime.combine(
                    self._termin_pending_date,
                    datetime.time(hour=hour, minute=minute)
                )

                if due <= datetime.datetime.now():
                    answer = (
                        "Dieser Zeitpunkt liegt bereits in der Vergangenheit. "
                        "Bitte nenne ein zukünftiges Datum und eine Uhrzeit."
                    )
                    self.log(f"Assistent: {answer}")
                    self._termin_mode = "date"
                    self._termin_pending_date = None
                    self._termin_pending_time = None
                    self._resume_after_answer = True
                    speak_mbrola(
                        answer, self.voice, self.speed, self.pitch, self.volume
                    )
                    return

                self._termin_confirm(hour, minute, subject, due)
                return

            # Während des Bestätigungsfensters wird keine normale Suche ausgelöst.
            if self._termin_mode == "confirm":
                return

        # Startwörter bewusst exakt und zusätzlich tolerant gegenüber
        # kleinen Spracherkennungs-Abweichungen.
        if (
            text_lower in {"termin", "terminplan", "terminplaner"}
            or "termin planer" in text_lower
            or "erinnerungsplaner" in text_lower
            or text_lower.startswith("terminplan ")
            or text_lower.startswith("terminplaner ")
        ):
            self._termin_start()
            return

        # ====================================================
        # GESICHTSBEFEHLE – VOR DER DATENBANKSUCHE
        # ====================================================
        # Diese beiden Befehle werden bewusst vor der normalen
        # Fragen-/Antwortsuche abgefangen. Dadurch kann niemals eine
        # zufällige Datenbankantwort auf den Gesichtsbefehl kommen.
        if (
            "merk dir mein gesicht" in text_lower
            or "merke dir mein gesicht" in text_lower
            or "mein gesicht merken" in text_lower
            or "mach ein foto von mir" in text_lower
            or "mach ein foto von mir" in text_lower
            or "mach ein bild von mir" in text_lower
            or "fotografiere mich" in text_lower
            or "nimm ein foto von mir auf" in text_lower
            or "nimm ein bild von mir auf" in text_lower
        ):
            self.handle_remember_face()
            return

        if (
            "weißt du wer ich bin" in text_lower
            or "weisst du wer ich bin" in text_lower
            or "weißt du, wer ich bin" in text_lower
            or "weisst du, wer ich bin" in text_lower
            or text_lower in ("wer bin ich", "wer bin ich?")
            or text_lower.startswith("wer bin ich ")
        ):
            self.handle_identify_face()
            return

        # ====================================================
        # LOTTO 6aus49
        # ====================================================
        # Vor der normalen Fragen-/Antwortsuche abfangen, damit keine
        # alte Datenbankantwort auf "Lottozahlen" verwendet wird.
        lotto_begriffe = (
            "lotto",
            "lottozahlen",
            "lotto zahlen",
            "gewinnzahlen",
            "lottoergebnisse",
            "lotto ergebnisse",
            "6 aus 49",
            "6 von 49",
            "sechs aus neunundvierzig",
        )

        if any(begriff in text_lower for begriff in lotto_begriffe):
            self.log("Aktuelle Lottozahlen werden geladen...")

            # Die Webabfrage läuft in einem eigenen Thread, damit die
            # Tkinter-Oberfläche währenddessen nicht einfriert.
            def lotto_worker():
                result = get_current_lotto_numbers()

                if result:
                    draw_date, numbers, superzahl = result
                    answer = (
                        f"Die aktuellen Lottozahlen vom {draw_date} sind "
                        + ", ".join(str(n) for n in numbers)
                        + f". Die Superzahl ist {superzahl}."
                    )
                else:
                    answer = (
                        "Ich konnte die aktuellen Lottozahlen gerade nicht abrufen."
                    )

                self.root.after(0, self.log, f"Assistent: {answer}")
                speak_mbrola(
                    answer,
                    self.voice,
                    self.speed,
                    self.pitch,
                    self.volume
                )

            threading.Thread(
                target=lotto_worker,
                name="LottoWorker",
                daemon=True
            ).start()
            return

        # ====================================================
        # UHRZEIT
        # ====================================================

        if (
            "uhr" in text_lower
            or "zeit" in text_lower
            or "wie spät" in text_lower
        ):

            now = datetime.datetime.now().strftime(
                "%H:%M:%S"
            )

            answer = f"Es ist {now}."

            self.log(
                f"Assistent: {answer}"
            )

            speak_mbrola(
                answer,
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            return

        # ====================================================
        # DATUM
        # ====================================================

        if (
            "datum" in text_lower
            or "welches datum" in text_lower
        ):

            today = datetime.datetime.now().strftime(
                "%d.%m.%Y"
            )

            answer = (
                f"Heute ist der {today}."
            )

            self.log(
                f"Assistent: {answer}"
            )

            speak_mbrola(
                answer,
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            return

        # ====================================================
        # WOCHENTAG
        # ====================================================

        if (
            "wochentag" in text_lower
            or "welcher tag" in text_lower
        ):

            weekdays = [
                "Montag",
                "Dienstag",
                "Mittwoch",
                "Donnerstag",
                "Freitag",
                "Samstag",
                "Sonntag"
            ]

            weekday = weekdays[
                datetime.datetime.now().weekday()
            ]

            answer = (
                f"Heute ist {weekday}."
            )

            self.log(
                f"Assistent: {answer}"
            )

            speak_mbrola(
                answer,
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            return

        # ====================================================
        # WETTER
        # ====================================================

        if "wetter" in text_lower:

            self.log(
                "Wetter wird geladen..."
            )

            def worker():

                answer = (
                    get_weather_bad_driburg()
                )

                self.root.after(
                    0,
                    self.log,
                    f"Assistent: {answer}"
                )

                speak_mbrola(
                    answer,
                    self.voice,
                    self.speed,
                    self.pitch,
                    self.volume
                )

            threading.Thread(
                target=worker,
                daemon=True
            ).start()

            return

        # ====================================================
        # YOUTUBE MUSIK
        # MUSS VOR LOKALER MUSIK KOMMEN!
        # ====================================================

        if (
            "youtube" in text_lower
            and (
                "spiel" in text_lower
                or "spiele" in text_lower
                or "öffne" in text_lower
            )
        ):

            words = (
                text_lower
                .split()
            )

            remove_words = [
                "spiel",
                "spiele",
                "musik",
                "lied",
                "song",
                "auf",
                "youtube",
                "von",
                "ein",
                "eine",
                "das",
                "den",
                "die",
                "mir"
            ]

            search_terms = [
                word
                for word in words
                if word not in remove_words
            ]

            search = " ".join(
                search_terms
            ).strip()

            if not search:

                speak_mbrola(
                    "Was soll ich auf YouTube suchen?",
                    self.voice,
                    self.speed,
                    self.pitch,
                    self.volume
                )

                open_browser(
                    "https://music.youtube.com"
                )

                return

            query = urllib.parse.quote_plus(
                search
            )

            answer = (
                f"Ich suche {search} auf YouTube."
            )

            self.log(
                f"Assistent: {answer}"
            )

            speak_mbrola(
                answer,
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            open_browser(
                "https://www.youtube.com/results?search_query="
                + query
            )

            return

        # ====================================================
        # YOUTUBE MUSIC DIREKT
        # ====================================================

        if (
            "youtube musik" in text_lower
            or "youtube music" in text_lower
        ):

            speak_mbrola(
                "Ich öffne YouTube Musik.",
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            open_browser(
                "https://music.youtube.com"
            )

            return

        # ====================================================
        # LOKALE MUSIK
        # ====================================================

        if (
            (
                "musik" in text_lower
                or "lied" in text_lower
                or "song" in text_lower
            )
            and
            (
                "spiel" in text_lower
                or "spiele" in text_lower
            )
        ):

            words = (
                text_lower
                .split()
            )

            remove_words = [
                "spiel",
                "spiele",
                "musik",
                "lied",
                "song",
                "von",
                "ein",
                "eine",
                "das",
                "den",
                "die",
                "mir"
            ]

            search_terms = [
                word
                for word in words
                if word not in remove_words
            ]

            if not search_terms:

                play_local_music(
                    None
                )

                return

            search = " ".join(
                search_terms
            )

            play_local_music(
                search
            )

            return

        # ====================================================
        # RADIO
        # ====================================================

        if (
            "radio" in text_lower
            or "internetradio" in text_lower
        ):

            speak_mbrola(
                "Ich starte dein Radio.",
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            open_browser(
                "https://www.radio.de"
            )

            return

        # ====================================================
        # BROWSER
        # ====================================================

        if (
            "öffne" in text_lower
            and "browser" in text_lower
        ):

            speak_mbrola(
                "Ich öffne deinen Browser.",
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            open_browser(
                "https://www.google.de"
            )

            return

        # ====================================================
        # WEBSEITEN
        # ====================================================

        if (
            "öffne" in text_lower
            and (
                "seite" in text_lower
                or ".de" in text_lower
                or ".com" in text_lower
                or ".net" in text_lower
                or ".org" in text_lower
            )
        ):

            words = (
                question_text
                .split()
            )

            for word in words:

                clean_word = (
                    word
                    .strip(".,!?")
                )

                if (
                    clean_word.startswith(
                        "www."
                    )
                    or clean_word.endswith(
                        (".de", ".com", ".net", ".org")
                    )
                ):

                    url = (
                        clean_word
                        if clean_word.startswith(
                            "http"
                        )
                        else "https://" + clean_word
                    )

                    speak_mbrola(
                        f"Ich öffne {clean_word}.",
                        self.voice,
                        self.speed,
                        self.pitch,
                        self.volume
                    )

                    open_browser(
                        url
                    )

                    return

            speak_mbrola(
                "Welche Seite soll ich öffnen?",
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            return

        # ====================================================
        # PROGRAMME
        # ====================================================

        if (
            "öffne" in text_lower
            or "starte" in text_lower
        ):

            words = (
                text_lower
                .split()
            )

            for word in words:

                word = (
                    word
                    .strip(".,!?")
                )

                if word in self.programs:

                    open_program(
                        self.programs[word]
                    )

                    return

            # Nur dann "Programm nicht bekannt",
            # wenn es wirklich wie ein Programm-Befehl klingt.
            if (
                "öffne" in text_lower
                or "starte" in text_lower
            ):

                speak_mbrola(
                    "Ich kenne dieses Programm noch nicht.",
                    self.voice,
                    self.speed,
                    self.pitch,
                    self.volume
                )

                return


            answer = "Ich konnte zu dieser Suche keine richtige Antwort finden."
            self.log(f"Assistent: {answer}")
            speak_mbrola(
                answer,
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )
            return

        # ====================================================
        # EXAKTE DATENBANK-ANTWORT
        # ====================================================

        answer = find_answer(
            question_text
        )

        if answer:

            parts = [
                p.strip()
                for p in answer.split("||")
                if p.strip()
            ]

            if parts:

                final = random.choice(
                    parts
                )

                self.log(
                    f"Assistent: {final}"
                )

                speak_mbrola(
                    final,
                    self.voice,
                    self.speed,
                    self.pitch,
                    self.volume
                )

                return

        # ====================================================
        # ÄHNLICHKEITS-SUCHE
        # ====================================================

        sq, sa, score = (
            find_best_similar(
                question_text
            )
        )

        if (
            sa
            and score >= 85
        ):
            # Bei einem ähnlichen Treffer können bis zu drei Antworten
            # mit "||" gespeichert sein. Es wird IMMER genau eine
            # Antwort gesprochen. Die Antworten werden dabei der Reihe
            # nach verwendet: 1 -> 2 -> 3 -> 1 ...
            parts = [
                p.strip()
                for p in str(sa).split("||")
                if p.strip()
            ]

            if parts:
                # Zähler pro gefundener Frage. Dadurch wird nicht immer
                # Antwort 1 verwendet, sondern bei wiederholten ähnlichen
                # Fragen die nächste vorhandene Antwort genommen.
                if not hasattr(self, "similar_answer_index"):
                    self.similar_answer_index = {}

                answer_key = str(sq or question_text).strip().lower()
                index = self.similar_answer_index.get(answer_key, 0)
                final = parts[index % len(parts)]
                self.similar_answer_index[answer_key] = (index + 1) % len(parts)

                self.log(
                    f"Assistent "
                    f"(Ähnlichkeit {score}% / Antwort {(index % len(parts)) + 1}): {final}"
                )

                speak_mbrola(
                    final,
                    self.voice,
                    self.speed,
                    self.pitch,
                    self.volume
                )

            return

        # ====================================================
        # EINZELNES HAUPTWORT -> WEB-SUCHE
        # ====================================================
        # Nur nach erfolgloser Datenbanksuche. Befehle und gespeicherte
        # Datenbankeinträge werden dadurch nicht verändert.
        single_word = re.sub(
            r"[^\\wäöüÄÖÜß-]",
            "",
            question_text.strip()
        )

        protected_words = {
            "start", "stop", "stopp", "hilfe", "ja", "nein",
            "okay", "ok", "hallo", "danke", "bitte"
        }

        if (
            single_word
            and len(single_word) >= 2
            and single_word.lower() not in protected_words
            and len(re.findall(r"[\\wäöüÄÖÜß-]+", question_text.strip())) == 1
        ):
            self.log(
                f"Einzelnes unbekanntes Hauptwort: {single_word}. "
                "Starte Websuche..."
            )

            web_answer = search_web_answer(single_word)

            if web_answer:
                self.stop_listening()

                speak_mbrola(
                    web_answer,
                    self.voice,
                    self.speed,
                    self.pitch,
                    self.volume
                )

                self.ask_new_answer_window(
                    single_word,
                    web_answer
                )
                return

            # Wenn die Websuche nichts liefert, fällt der Code wie bisher
            # in die normale "unbekannte Frage"-Behandlung.
            self.log(
                "Keine Webantwort für das einzelne Hauptwort gefunden."
            )

        # ====================================================
        # WEBSUCHE ALS FALLBACK
        # ====================================================
        # Wenn die Frage weder exakt noch ähnlich in der Datenbank
        # gefunden wurde, wird zuerst eine Websuche versucht.
        # Nur wenn auch diese keine Antwort liefert, erscheint
        # das Fenster zum manuellen Anlegen einer Antwort.

        self.log(
            "Frage nicht in der Datenbank gefunden. Starte Websuche..."
        )

        web_answer = search_web_answer(
            question_text
        )

        if web_answer:
            self.log(
                f"Websuche: {web_answer}"
            )

            # Mikrofon vor der Web-TTS-Ausgabe wirklich schließen.
            self.stop_listening()

            speak_mbrola(
                web_answer,
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            # Nach einer erfolgreichen Websuche die gefundene Antwort
            # direkt zum Speichern in die Datenbank anbieten.
            self.ask_new_answer_window(
                question_text,
                web_answer
            )

            return

        self.log(
            "Websuche lieferte keine verwertbare Antwort."
        )

        self.handle_unknown_question(
            question_text
        )

        return


    # ========================================================
    # UNBEKANNTE FRAGE
    # ========================================================

    def handle_unknown_question(
        self,
        question_text
    ):

        # Mikrofon zuerst wirklich schließen, damit während der Eingabe
        # keine Sprache mehr aufgenommen wird.
        self.stop_listening()

        speak_mbrola(
            "Diese Frage kenne ich nicht. "
            "Bitte gib eine Antwort ein.",
            self.voice,
            self.speed,
            self.pitch,
            self.volume
        )

        self.ask_new_answer_window(
            question_text
        )


    # ========================================================
    # NEUE ANTWORT
    # ========================================================

    def ask_new_answer_window(
        self,
        question_text,
        initial_answer=""
    ):

        win = tk.Toplevel(
            self.root
        )

        win.title(
            "Webantwort speichern" if initial_answer else "Neue Antworten eingeben"
        )

        win.geometry(
            "620x560"
        )

        win.configure(
            bg=current_theme["bg"]
        )

        ttk.Label(
            win,
            text=f"Frage:\n{question_text}"
        ).pack(
            padx=10,
            pady=10
        )

        ttk.Label(
            win,
            text="Webantwort / Antwort 1:" if initial_answer else "Antwort 1 (Pflichtfeld):"
        ).pack(
            anchor=tk.W,
            padx=10
        )

        ans1_entry = tk.Text(
            win,
            height=4,
            width=70,
            bg=current_theme["bg2"],
            fg=current_theme["fg"],
            insertbackground=current_theme["fg"]
        )

        ans1_entry.pack(
            fill=tk.X,
            padx=10,
            pady=(3, 8)
        )

        # Webantwort automatisch als Antwort 1 eintragen, damit sie
        # mit einem Klick gespeichert werden kann.
        if initial_answer:
            ans1_entry.insert("1.0", initial_answer)

        ttk.Label(
            win,
            text="Antwort 2 (optional):"
        ).pack(
            anchor=tk.W,
            padx=10
        )

        ans2_entry = tk.Text(
            win,
            height=4,
            width=70,
            bg=current_theme["bg2"],
            fg=current_theme["fg"],
            insertbackground=current_theme["fg"]
        )

        ans2_entry.pack(
            fill=tk.X,
            padx=10,
            pady=(3, 8)
        )

        ttk.Label(
            win,
            text="Antwort 3 (optional):"
        ).pack(
            anchor=tk.W,
            padx=10
        )

        ans3_entry = tk.Text(
            win,
            height=4,
            width=70,
            bg=current_theme["bg2"],
            fg=current_theme["fg"],
            insertbackground=current_theme["fg"]
        )

        ans3_entry.pack(
            fill=tk.X,
            padx=10,
            pady=(3, 10)
        )

        add_context_menu(ans1_entry)
        add_context_menu(ans2_entry)
        add_context_menu(ans3_entry)

        def save_and_close():

            new_answer1 = (
                ans1_entry
                .get("1.0", tk.END)
                .strip()
            )

            new_answer2 = (
                ans2_entry
                .get("1.0", tk.END)
                .strip()
            )

            new_answer3 = (
                ans3_entry
                .get("1.0", tk.END)
                .strip()
            )

            if not new_answer1:
                messagebox.showwarning(
                    "Fehler",
                    "Antwort 1 darf nicht leer sein."
                )
                return


            answers = "||".join(
                [
                    new_answer1,
                    new_answer2,
                    new_answer3
                ]
            )

            saved = insert_qa(
                question_text,
                answers
            )

            if not saved:
                messagebox.showerror(
                    "Speicherfehler",
                    "Die Antworten konnten nicht "
                    "gespeichert werden."
                )
                return

            self.refresh_qa_list()

            self.log(
                f"Neue Antworten gespeichert: "
                f"{new_answer1}"
            )

            win.destroy()

            speak_mbrola(
                "Antworten gespeichert.",
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            self.root.after(
                1500,
                self.start_listening
            )

        def cancel():

            self.log(
                "Eingabe abgebrochen."
            )

            speak_mbrola(
                "Okay, ich breche ab.",
                self.voice,
                self.speed,
                self.pitch,
                self.volume
            )

            win.destroy()

            self.root.after(
                500,
                self.start_listening
            )

        btn_frame = ttk.Frame(
            win
        )

        btn_frame.pack(
            pady=10
        )

        ttk.Button(
            btn_frame,
            text="Speichern",
            command=save_and_close
        ).pack(
            side=tk.LEFT,
            padx=10
        )

        ttk.Button(
            btn_frame,
            text="Abbrechen",
            command=cancel
        ).pack(
            side=tk.LEFT,
            padx=10
        )

        ans1_entry.focus_set()


    # ========================================================
    # MIKROFON VISUALIZER
    # ========================================================

    def draw_mic_circle(self):
        self.mic_canvas.delete("all")
        lvl = self.audio_level
        if lvl < 0.25:
            color = "#8ec07c"
        elif lvl < 0.50:
            color = "#fabd2f"
        elif lvl < 0.75:
            color = "#fe8019"
        else:
            color = "#fb4934"

        # Kleine, mittige Bereitschaftsanzeige.
        dynamic_boost = lvl * 8
        r = self.mic_radius + dynamic_boost
        cx = max(1, self.mic_canvas.winfo_width() // 2)
        cy = max(1, self.mic_canvas.winfo_height() // 2)
        self.mic_canvas.create_oval(
            cx-r-3, cy-r-3, cx+r+3, cy+r+3,
            fill=color, outline=color, stipple="gray50"
        )
        self.mic_canvas.create_oval(
            cx-r, cy-r, cx+r, cy+r,
            fill=color, outline=color
        )

    def animate_mic(self):
        if self.listening:
            if self.mic_growing:
                self.mic_radius += 0.5
                if self.mic_radius >= 17:
                    self.mic_growing = False
            else:
                self.mic_radius -= 0.5
                if self.mic_radius <= 10:
                    self.mic_growing = True
        else:
            self.mic_radius = 12
        self.draw_mic_circle()
        if self.scheduler_running:
            self.root.after(40, self.animate_mic)

    # ========================================================
    # VISUALIZER
    # ========================================================

    def draw_visualizer(self):
        """Moderne, lebendige Audio-Wellenanzeige für das aktive Zuhören."""
        self.visual_canvas.delete("all")
        width = max(220, self.visual_canvas.winfo_width())
        height = max(90, self.visual_canvas.winfo_height())
        cx = width / 2
        cy = height / 2

        # Ruhiger Hintergrund mit feinem Mittelpunkt
        self.visual_canvas.create_line(18, cy, width - 18, cy,
                                       fill=current_theme["border"], width=1)

        import math
        now = time.time()
        active = bool(self.listening)
        level = max(0.02, min(1.0, self.audio_level))

        # Wenn zugehört wird, bleibt die Welle sichtbar und bewegt sich auch
        # bei leiser/kurzer Sprache weiter. So wirkt sie nicht eingefroren.
        if active:
            base = 0.18 + level * 0.72
        else:
            base = level * 0.35

        bars = 31
        gap = 4
        bar_w = max(3, (width - 36 - (bars - 1) * gap) / bars)
        start_x = (width - (bars * bar_w + (bars - 1) * gap)) / 2
        max_h = height * 0.78

        for i in range(bars):
            # Symmetrische, weiche Wellenbewegung
            distance = abs(i - (bars - 1) / 2) / ((bars - 1) / 2)
            envelope = 1.0 - distance * 0.55
            wave = (math.sin(now * 5.2 + i * 0.62) + 1.0) / 2.0
            wave2 = (math.sin(now * 2.7 - i * 0.35) + 1.0) / 2.0
            amount = 0.25 + 0.55 * wave + 0.20 * wave2
            h = max(5, min(max_h, max_h * base * envelope * amount))

            # Farbübergang anhand des Pegels
            if level < 0.35:
                color = "#8ec07c"
            elif level < 0.65:
                color = "#fabd2f"
            elif level < 0.85:
                color = "#fe8019"
            else:
                color = "#fb4934"

            x1 = start_x + i * (bar_w + gap)
            x2 = x1 + bar_w
            self.visual_canvas.create_rectangle(
                x1, cy - h / 2, x2, cy + h / 2,
                fill=color, outline=""
            )

        # Leuchtender Mittelpunkt zeigt eindeutig: ALI hört zu
        if active:
            pulse = 5 + int((math.sin(now * 5) + 1) * 2.5)
            self.visual_canvas.create_oval(
                cx - pulse, cy - pulse, cx + pulse, cy + pulse,
                fill="#4da3ff", outline=""
            )

    def animate_visualizer(self):
        # Audiopegel weich auslaufen lassen, aber während des Zuhörens niemals
        # komplett verschwinden lassen. Die Welle selbst animiert weiter.
        if self.listening:
            self.audio_level = max(0.06, self.audio_level - 0.025)
        else:
            self.audio_level = max(0.0, self.audio_level - 0.06)
        self.draw_visualizer()
        if self.scheduler_running:
            self.root.after(35, self.animate_visualizer)


    # ========================================================
    # AUTOPLAY
    # ========================================================

    def resume_listening_after_speech(self, delay=200, resume_listening=True):
        """Stellt nach TTS nur dann die Sprachaufnahme wieder her, wenn sie vorher lief."""
        if getattr(self, "_manual_stop_latched", False):
            return
        if not self.scheduler_running:
            return

        if SPEAKING or SPEECH_BLOCK_LISTENING.is_set() or not speech_queue.empty():
            self.root.after(delay, self.resume_listening_after_speech, delay, resume_listening)
            return

        # War das Mikrofon vorher bewusst deaktiviert, hat speech_worker
        # diesen Zustand bereits wiederhergestellt. Dann darf hier nichts
        # erneut aktiviert werden.
        if not resume_listening:
            return

        if is_vlc_running():
            mute_system_mic()
            return

        # Kurze Pause, damit ALSA/PulseAudio das Capture-Gerät sicher
        # wieder freigibt, bevor der neue Aufnahme-Thread startet.
        self.root.after(300, self.start_listening)


    def schedule_autoplay(self):

        if not self.scheduler_running:
            return

        now = datetime.datetime.now()

        # ----------------------------------------------------
        # VOLLE STUNDE
        # ----------------------------------------------------

        if self.autoplay_hourly_time.get():

            if (
                now.minute == 0
                and now.second < 5
            ):

                if (
                    time.time()
                    - self.last_speech_time
                    > 10
                    and not SPEAKING
                ):

                    was_listening = self.listening
                    self.stop_listening()

                    answer = (
                        f"Es ist jetzt "
                        f"{now.strftime('%H:%M Uhr')}."
                    )

                    self.log(
                        f"Assistent: {answer}"
                    )

                    speak_mbrola(
                        answer,
                        self.voice,
                        self.speed,
                        self.pitch,
                        self.volume
                    )

                    self.last_speech_time = (
                        time.time()
                    )

                    self.resume_listening_after_speech(resume_listening=was_listening)

        # ----------------------------------------------------
        # HALBE STUNDE WETTER
        # ----------------------------------------------------

        if self.autoplay_halfhour_weather.get():

            if (
                now.minute == 30
                and now.second < 5
            ):

                if (
                    time.time()
                    - self.last_speech_time
                    > 10
                    and not SPEAKING
                ):

                    was_listening = self.listening
                    self.stop_listening()

                    def weather_worker():

                        weather = (
                            get_weather_bad_driburg()
                        )

                        self.root.after(
                            0,
                            self.log,
                            f"Wetter: {weather}"
                        )

                        speak_mbrola(
                            weather,
                            self.voice,
                            self.speed,
                            self.pitch,
                            self.volume
                        )

                        self.root.after(
                            0,
                            self.resume_listening_after_speech,
                            200,
                            was_listening
                        )

                    threading.Thread(
                        target=weather_worker,
                        daemon=True
                    ).start()

                    self.last_speech_time = (
                        time.time()
                    )

        # ----------------------------------------------------
        # AUTO-FRAGEN
        # ----------------------------------------------------

        interval = (
            self.autoplay_interval.get()
        )

        if interval > 0:

            if (
                time.time()
                - self.last_speech_time
                > interval * 60
                and not SPEAKING
            ):

                question = (
                    get_random_question()
                )

                if question:

                    was_listening = self.listening
                    self.stop_listening()

                    self.log(
                        f"Assistent fragt: {question}"
                    )

                    speak_mbrola(
                        question,
                        self.voice,
                        self.speed,
                        self.pitch,
                        self.volume
                    )

                    self.last_speech_time = (
                        time.time()
                    )

                    self.root.after(
                        0,
                        self.resume_listening_after_speech,
                        200,
                        was_listening
                    )

        self.root.after(
            1000,
            self.schedule_autoplay
        )


    # ========================================================
    # WETTERWARNUNGEN
    # ========================================================

    def schedule_weather_warning(self):

        if not self.scheduler_running:
            return

        delay = (
            random.randint(
                300,
                600
            )
            * 1000
        )

        self.root.after(
            delay,
            self.check_weather_warning
        )


    def check_weather_warning(self):

        if not self.scheduler_running:
            return

        if SPEAKING:

            self.root.after(
                3000,
                self.check_weather_warning
            )

            return

        def worker():

            warning = (
                get_weather_warning_with_forecast()
            )

            if warning:

                def show_warning():

                    if SPEAKING:
                        return

                    was_listening = self.listening
                    self.stop_listening()

                    self.log(
                        f"Wetterwarnung: {warning}"
                    )

                    speak_mbrola(
                        warning,
                        self.voice,
                        self.speed,
                        self.pitch,
                        self.volume
                    )

                    self.root.after(
                        1500,
                        self.resume_listening_after_speech,
                        200,
                        was_listening
                    )

                self.root.after(
                    0,
                    show_warning
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

        self.schedule_weather_warning()


    # ========================================================
    # PROGRAMME VERWALTEN
    # ========================================================

    def open_program_manager(self):

        win = tk.Toplevel(
            self.root
        )

        win.title(
            "Programme verwalten"
        )

        win.geometry(
            "500x380"
        )

        win.configure(
            bg=current_theme["bg"]
        )

        ttk.Label(
            win,
            text="Gespeicherte Programme:"
        ).pack(
            pady=5
        )

        listbox = tk.Listbox(
            win,
            height=8,
            bg=current_theme["bg2"],
            fg=current_theme["fg"]
        )

        listbox.pack(
            fill=tk.X,
            padx=10
        )

        def reload_program_list():

            listbox.delete(
                0,
                tk.END
            )

            for name, path in self.programs.items():

                listbox.insert(
                    tk.END,
                    f"{name} → {path}"
                )

        reload_program_list()

        ttk.Label(
            win,
            text="Name:"
        ).pack(
            pady=5
        )

        name_entry = ttk.Entry(
            win,
            width=40
        )

        name_entry.pack()

        ttk.Label(
            win,
            text="Pfad:"
        ).pack(
            pady=5
        )

        path_entry = ttk.Entry(
            win,
            width=40
        )

        path_entry.pack()

        add_context_menu(
            name_entry
        )

        add_context_menu(
            path_entry
        )

        def on_select(event):

            sel = listbox.curselection()

            if not sel:
                return

            item = listbox.get(
                sel[0]
            )

            try:

                name, path = item.split(
                    " → ",
                    1
                )

            except ValueError:
                return

            name_entry.delete(
                0,
                tk.END
            )

            name_entry.insert(
                0,
                name
            )

            path_entry.delete(
                0,
                tk.END
            )

            path_entry.insert(
                0,
                path
            )

        listbox.bind(
            "<<ListboxSelect>>",
            on_select
        )

        def save_prog():

            name = (
                name_entry
                .get()
                .strip()
                .lower()
            )

            path = (
                path_entry
                .get()
                .strip()
            )

            if not name or not path:

                messagebox.showwarning(
                    "Fehler",
                    "Name und Pfad dürfen nicht leer sein."
                )

                return

            self.programs[name] = path

            self.save_all_settings()

            reload_program_list()

            messagebox.showinfo(
                "Gespeichert",
                f"{name} → {path}"
            )

        def delete_prog():

            name = (
                name_entry
                .get()
                .strip()
                .lower()
            )

            if name in self.programs:

                del self.programs[name]

                self.save_all_settings()

                reload_program_list()

                name_entry.delete(
                    0,
                    tk.END
                )

                path_entry.delete(
                    0,
                    tk.END
                )

                messagebox.showinfo(
                    "Gelöscht",
                    f"{name} wurde entfernt."
                )

            else:

                messagebox.showwarning(
                    "Fehler",
                    "Programm nicht gefunden."
                )

        btn_frame = ttk.Frame(
            win
        )

        btn_frame.pack(
            pady=10
        )

        ttk.Button(
            btn_frame,
            text="Speichern / Aktualisieren",
            command=save_prog
        ).pack(
            side=tk.LEFT,
            padx=10
        )

        ttk.Button(
            btn_frame,
            text="Löschen",
            command=delete_prog
        ).pack(
            side=tk.LEFT,
            padx=10
        )



    # ========================================================
    # EINHEITLICHE SEITENANSICHT
    # ========================================================

    def _show_page(self, title, subtitle=""):
        """Zeigt eine Seite im Hauptfenster an; kein Toplevel."""
        self.page_frame.place(x=232, y=0, relwidth=1, relheight=1, width=-232)
        self.page_frame.lift()
        for child in self.page_frame.winfo_children():
            child.destroy()

        th = current_theme
        header = tk.Frame(self.page_frame, bg=th["bg2"])
        header.pack(fill=tk.X, padx=18, pady=(18, 10))
        tk.Label(header, text=title, font=("TkDefaultFont", 18, "bold"),
                 bg=th["bg2"], fg=th["fg"]).pack(anchor=tk.W, padx=18, pady=(14, 2))
        if subtitle:
            tk.Label(header, text=subtitle, font=("TkDefaultFont", 9),
                     bg=th["bg2"], fg=th["border"]).pack(anchor=tk.W, padx=18, pady=(0, 14))

        content = tk.Frame(self.page_frame, bg=th["bg"])
        content.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 18))
        return content

    def _page_button(self, parent, text, command):
        th = current_theme
        return tk.Button(parent, text=text, command=command, relief="flat", bd=0,
                         cursor="hand2", padx=16, pady=9, bg=th["accent"], fg=th["fg"],
                         activebackground=th["hover"], activeforeground=th["fg"])

    def show_dashboard(self):
        self.page_frame.place_forget()
        self.dashboard_panel.pack_forget()
        self.qa_panel.pack_forget()
        self.dashboard_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.qa_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.status_label.config(text="● BEREIT", fg=current_theme["green"])

    def show_qa_editor(self):
        self.page_frame.place_forget()
        self.dashboard_panel.pack_forget()
        self.qa_panel.pack_forget()
        self.qa_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.status_label.config(text="● FRAGEN & ANTWORTEN", fg=current_theme["fg"])
        self.qa_search_entry.focus_set()
        self.log("Fragen & Antworten geöffnet.")

    def show_music_page(self):
        content = self._show_page("Musik", "Lokale Musik abspielen und Musikordner verwalten")
        th = current_theme
        card = tk.Frame(content, bg=th["bg2"])
        card.pack(fill=tk.X, pady=4)
        tk.Label(card, text="Musikordner", font=("TkDefaultFont", 11, "bold"),
                 bg=th["bg2"], fg=th["fg"]).pack(anchor=tk.W, padx=18, pady=(16, 5))
        path_var = tk.StringVar(value=load_music_path())
        entry = ttk.Entry(card, textvariable=path_var)
        entry.pack(fill=tk.X, padx=18, pady=6)
        add_context_menu(entry)
        row = tk.Frame(card, bg=th["bg2"])
        row.pack(fill=tk.X, padx=14, pady=(4, 16))
        self._page_button(row, "Ordner auswählen", lambda: self._select_music_folder(path_var)).pack(side=tk.LEFT, padx=4)
        self._page_button(row, "Musik starten", lambda: play_local_music()).pack(side=tk.LEFT, padx=4)
        self._page_button(row, "Titel suchen", lambda: self._play_music_search(path_var)).pack(side=tk.LEFT, padx=4)
        self.status_label.config(text="● MUSIK", fg=th["fg"])

    def _select_music_folder(self, var):
        path = filedialog.askdirectory(title="Musikordner auswählen")
        if path:
            save_music_path(path)
            var.set(path)
            self.log(f"Neuer Musikordner: {path}")

    def _play_music_search(self, path_var):
        # Ein kleines Suchfeld innerhalb der Musikseite statt eines neuen Fensters.
        win = tk.Toplevel(self.root)  # wird sofort als temporäres Eingabefenster vermieden
        win.withdraw()
        win.destroy()
        # Die Suche erfolgt über eine einfache Eingabe im Hauptfenster.
        content = self.page_frame.winfo_children()[-1]
        search = getattr(self, "music_search_entry", None)
        if search is None or not search.winfo_exists():
            search = ttk.Entry(content)
            search.pack(fill=tk.X, padx=18, pady=8)
            self.music_search_entry = search
            add_context_menu(search)
            search.focus_set()
            return
        play_local_music(search.get().strip())

    def show_backup_page(self):
        content = self._show_page("Backup", "Sicherungen der Datenbank verwalten")
        th = current_theme
        card = tk.Frame(content, bg=th["bg2"])
        card.pack(fill=tk.X, pady=4)
        tk.Label(card, text="Backup-System", font=("TkDefaultFont", 11, "bold"),
                 bg=th["bg2"], fg=th["fg"]).pack(anchor=tk.W, padx=18, pady=(16, 10))
        name_row = tk.Frame(card, bg=th["bg2"]); name_row.pack(fill=tk.X, padx=18, pady=5)
        tk.Label(name_row, text="Backup-Name:", bg=th["bg2"], fg=th["fg"]).pack(side=tk.LEFT)
        ttk.Entry(name_row, textvariable=self.backup_name, width=35).pack(side=tk.LEFT, padx=10)
        self.auto_backup_enabled.set(self.auto_backup_enabled.get())
        ttk.Checkbutton(card, text="Automatische Backups aktiv", variable=self.auto_backup_enabled,
                        command=self.toggle_auto_backup).pack(anchor=tk.W, padx=18, pady=8)
        row = tk.Frame(card, bg=th["bg2"]); row.pack(fill=tk.X, padx=14, pady=(5, 10))
        self._page_button(row, "Backup jetzt erstellen", self.run_backup_now).pack(side=tk.LEFT, padx=4)
        self._page_button(row, "Backup wiederherstellen", self.restore_backup).pack(side=tk.LEFT, padx=4)
        self._page_button(row, "Backup-Ordner öffnen", self.open_backup_folder).pack(side=tk.LEFT, padx=4)

        tk.Label(card, text="Vorhandene Backups:", bg=th["bg2"], fg=th["fg"]).pack(anchor=tk.W, padx=18, pady=(4, 4))
        self.backup_listbox = tk.Listbox(
            card, height=8, relief="flat", bd=0,
            bg=th["bg"], fg=th["fg"],
            selectbackground=th["hover"], highlightthickness=0
        )
        self.backup_listbox.pack(fill=tk.X, padx=18, pady=(0, 16))
        self.refresh_backup_list()
        self.status_label.config(text="● BACKUP", fg=th["fg"])

    def show_settings_page(self):
        content = self._show_page("Einstellungen", "Allgemeine Einstellungen des Sprachassistenten")
        th = current_theme
        for title, value, command in [
            ("Audio / Stimme", f"Stimme: {self.voice} · {self.speed} WPM · Tonhöhe {self.pitch} · Lautstärke {self.volume}", self.open_audio_settings),
            ("Sound-Treiber", f"Aktuell: {self.sound_driver}", self.change_sound_driver),
            ("Musik Pfad", load_music_path(), self.show_music_page),
            ("Backup-Namen", f"Aktuell: {self.backup_name.get()}", self.show_backup_page),
        ]:
            card = tk.Frame(content, bg=th["bg2"]); card.pack(fill=tk.X, pady=5)
            tk.Label(card, text=title, font=("TkDefaultFont", 11, "bold"), bg=th["bg2"], fg=th["fg"]).pack(anchor=tk.W, padx=18, pady=(12, 2))
            tk.Label(card, text=value, bg=th["bg2"], fg=th["border"], wraplength=800, justify=tk.LEFT).pack(anchor=tk.W, padx=18, pady=2)
            self._page_button(card, "Öffnen", command).pack(anchor=tk.W, padx=14, pady=(5, 12))
        self.status_label.config(text="● EINSTELLUNGEN", fg=th["fg"])

    def open_help_window(self):
        content = self._show_page("Anleitung", "Bedienung und Funktionen")
        th = current_theme
        text = tk.Text(content, wrap="word", relief="flat", bd=0,
                       bg=th["bg2"], fg=th["fg"], insertbackground=th["fg"], padx=18, pady=18)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, HELP_TEXT)
        text.config(state="disabled")
        self.status_label.config(text="● HILFE", fg=th["fg"])

    def change_music_path(self):
        self.show_music_page()

    def run_backup_now(self):
        result = backup_database(self.backup_name.get())
        self.log("Backup erfolgreich erstellt." if result else "Backup konnte nicht erstellt werden.")
        if result:
            messagebox.showinfo("Backup", "Backup wurde erfolgreich erstellt.")
        else:
            messagebox.showwarning("Backup", "Backup konnte nicht erstellt werden.")

    def change_backup_name(self):
        self.show_backup_page()

    def refresh_backup_list(self):
        """Aktualisiert die Liste der vorhandenen Datenbank-Backups."""
        lb = getattr(self, "backup_listbox", None)
        if lb is None or not lb.winfo_exists():
            return
        lb.delete(0, tk.END)
        backup_dir = "backups"
        if not os.path.isdir(backup_dir):
            return
        backups = sorted(
            (f for f in os.listdir(backup_dir) if f.lower().endswith(".db")),
            reverse=True
        )
        for name in backups:
            lb.insert(tk.END, name)

    def restore_backup(self):
        """Stellt ein ausgewähltes Backup zuverlässig wieder her.

        Vor der Wiederherstellung wird der aktuelle Stand gesichert.
        Das ausgewählte Backup wird vorher geprüft und in eine temporäre
        Datei kopiert, damit es auch dann verfügbar bleibt, wenn die
        Backup-Rotation beim Sicherheits-Backup alte Dateien entfernt.
        """
        import tempfile

        backup_dir = os.path.abspath("backups")
        db_file = os.path.abspath(DB_FILE)
        lb = getattr(self, "backup_listbox", None)

        if lb is None or not lb.winfo_exists():
            messagebox.showwarning("Backup", "Bitte zuerst die Backup-Seite öffnen.")
            return

        selection = lb.curselection()
        if not selection:
            messagebox.showwarning(
                "Backup wiederherstellen",
                "Bitte zuerst ein Backup auswählen."
            )
            return

        filename = lb.get(selection[0])
        backup_file = os.path.abspath(os.path.join(backup_dir, filename))

        # Nur echte Dateien direkt im Backup-Ordner zulassen.
        if (
            os.path.dirname(os.path.realpath(backup_file))
            != os.path.realpath(backup_dir)
            or not filename.lower().endswith(".db")
        ):
            messagebox.showerror("Fehler", "Ungültige Backup-Datei.")
            return

        if not os.path.isfile(backup_file):
            messagebox.showerror(
                "Fehler",
                "Das ausgewählte Backup existiert nicht mehr.\n"
            )
            self.refresh_backup_list()
            return

        # Backup vor dem Überschreiben prüfen. Dadurch wird verhindert,
        # dass eine leere/defekte SQLite-Datei als Wiederherstellung gilt.
        try:
            conn = sqlite3.connect(backup_file)
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name='qa'"
                )
                if cur.fetchone() is None:
                    raise ValueError("Die Tabelle 'qa' fehlt im Backup.")

                cur.execute("SELECT COUNT(*) FROM qa")
                backup_count = int(cur.fetchone()[0])
            finally:
                conn.close()
        except Exception as e:
            messagebox.showerror(
                "Ungültiges Backup",
                f"Das Backup konnte nicht gelesen werden:\n{e}"
            )
            return

        if not messagebox.askyesno(
            "Backup wiederherstellen",
            f"Soll dieses Backup wirklich wiederhergestellt werden?\n\n"
            f"{filename}\n"
            f"Enthaltene Fragen: {backup_count}\n\n"
            "Vorher wird automatisch ein Sicherheits-Backup des aktuellen "
            "Standes erstellt."
        ):
            return

        temp_backup = None
        try:
            # Das gewählte Backup zuerst sichern. So kann die Backup-Rotation
            # es nicht löschen, wenn anschließend das Sicherheits-Backup
            # erstellt wird.
            fd, temp_backup = tempfile.mkstemp(
                prefix="restore_",
                suffix=".db",
                dir=backup_dir
            )
            os.close(fd)
            shutil.copy2(backup_file, temp_backup)

            safety_backup = backup_database(
                f"vor_restore_{self.backup_name.get()}"
            )
            if not safety_backup:
                raise RuntimeError(
                    "Der aktuelle Datenbankstand konnte nicht gesichert werden."
                )

            # Vorhandene DB ersetzen. Unter Windows/Linux ist dies robuster
            # als ein einfaches Überschreiben einer möglicherweise geöffneten DB.
            shutil.copy2(temp_backup, db_file)

            # Sicherstellen, dass die wiederhergestellte DB tatsächlich die
            # erwartete Anzahl Datensätze enthält.
            conn = sqlite3.connect(db_file)
            try:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM qa")
                restored_count = int(cur.fetchone()[0])
            finally:
                conn.close()

            if restored_count != backup_count:
                raise RuntimeError(
                    f"Prüfung fehlgeschlagen: erwartet {backup_count}, "
                    f"gefunden {restored_count} Fragen."
                )

            # Datenbank erneut einlesen und beide Oberflächen aktualisieren.
            self.qa_items = get_all_qa()
            if hasattr(self, "qa_listbox") and self.qa_listbox.winfo_exists():
                self.refresh_qa_list()

            self.refresh_backup_list()
            self.log(
                f"Backup wiederhergestellt: {filename} "
                f"({restored_count} Fragen)"
            )

            messagebox.showinfo(
                "Backup wiederhergestellt",
                f"Das Backup wurde erfolgreich wiederhergestellt.\n\n"
                f"{filename}\n"
                f"{restored_count} Fragen/Antworten wurden geladen."
            )

        except Exception as e:
            messagebox.showerror(
                "Wiederherstellung fehlgeschlagen",
                f"Das Backup konnte nicht wiederhergestellt werden:\n{e}"
            )
        finally:
            if temp_backup:
                try:
                    os.remove(temp_backup)
                except OSError:
                    pass

    def change_sound_driver(self):
        content = self._show_page("Sound-Treiber", "Audio-Ausgabe für VLC auswählen")
        th = current_theme
        var = tk.StringVar(value=load_sound_driver())
        card = tk.Frame(content, bg=th["bg2"]); card.pack(fill=tk.X, pady=4)
        tk.Label(card, text="Sound-Treiber", font=("TkDefaultFont", 11, "bold"), bg=th["bg2"], fg=th["fg"]).pack(anchor=tk.W, padx=18, pady=(16, 8))
        for driver in ["pulse", "alsa", "sdl", "oss", "jack", "portaudio"]:
            ttk.Radiobutton(card, text=driver, value=driver, variable=var).pack(anchor=tk.W, padx=24, pady=2)
        def save_driver():
            driver = var.get(); save_sound_driver(driver); self.sound_driver = driver; self.save_all_settings(); restart_audio_system(driver)
            self.log(f"Sound-Treiber gesetzt auf: {driver}")
        self._page_button(card, "Speichern", save_driver).pack(anchor=tk.W, padx=14, pady=16)
        self.status_label.config(text="● SOUND-TREIBER", fg=th["fg"])

    def open_audio_settings(self):
        content = self._show_page("Audio / Stimme", "Stimme, Geschwindigkeit, Tonhöhe und Lautstärke")
        th = current_theme
        card = tk.Frame(content, bg=th["bg2"]); card.pack(fill=tk.X, pady=4)
        vars_ = {"voice": tk.StringVar(value=self.voice), "speed": tk.IntVar(value=self.speed), "pitch": tk.IntVar(value=self.pitch), "volume": tk.IntVar(value=self.volume)}
        ttk.Label(card, text="Stimme (MBROLA):").grid(row=0, column=0, sticky=tk.W, padx=18, pady=10)
        ttk.Combobox(card, textvariable=vars_["voice"], state="readonly", values=[f"mb-de{i}" for i in range(1,9)]).grid(row=0,column=1,sticky=tk.W,pady=10)
        for row, key, label, lo, hi in [(1,"speed","Geschwindigkeit",80,260),(2,"pitch","Tonhöhe",0,99),(3,"volume","Lautstärke",50,200)]:
            ttk.Label(card,text=label).grid(row=row,column=0,sticky=tk.W,padx=18,pady=8)
            ttk.Spinbox(card,from_=lo,to=hi,textvariable=vars_[key],width=8).grid(row=row,column=1,sticky=tk.W,pady=8)
        def test(): speak_mbrola("Dies ist ein Test der aktuellen Stimme.", vars_["voice"].get(), vars_["speed"].get(), vars_["pitch"].get(), vars_["volume"].get())
        def save():
            try:
                self.voice=vars_["voice"].get(); self.speed=int(vars_["speed"].get()); self.pitch=int(vars_["pitch"].get()); self.volume=int(vars_["volume"].get())
            except ValueError:
                messagebox.showwarning("Fehler","Bitte gültige Zahlen eingeben."); return
            self.save_all_settings(); self.log("Audio-Einstellungen gespeichert.")
        row = tk.Frame(card,bg=th["bg2"]); row.grid(row=4,column=0,columnspan=2,sticky=tk.W,padx=14,pady=16)
        self._page_button(row,"Test",test).pack(side=tk.LEFT,padx=4); self._page_button(row,"Speichern",save).pack(side=tk.LEFT,padx=4)
        self.status_label.config(text="● AUDIO / STIMME", fg=th["fg"])

    def open_program_manager(self):
        content = self._show_page("Programme", "Programme verwalten, speichern und starten")
        th = current_theme
        top = tk.Frame(content,bg=th["bg2"]); top.pack(fill=tk.BOTH,expand=True)
        listbox=tk.Listbox(top, relief="flat",bd=0,bg=th["bg"],fg=th["fg"],selectbackground=th["hover"],highlightthickness=0)
        listbox.pack(side=tk.LEFT,fill=tk.BOTH,expand=True,padx=(14,7),pady=14)
        edit=tk.Frame(top,bg=th["bg2"]); edit.pack(side=tk.RIGHT,fill=tk.Y,padx=14,pady=14)
        name=ttk.Entry(edit,width=36); path=ttk.Entry(edit,width=36)
        ttk.Label(edit,text="Name:").pack(anchor=tk.W,pady=(8,3)); name.pack(fill=tk.X,pady=3)
        ttk.Label(edit,text="Pfad:").pack(anchor=tk.W,pady=(10,3)); path.pack(fill=tk.X,pady=3)
        add_context_menu(name); add_context_menu(path)
        def reload_():
            listbox.delete(0,tk.END)
            for n,p in self.programs.items(): listbox.insert(tk.END,f"{n} → {p}")
        def select(_=None):
            sel=listbox.curselection()
            if not sel:return
            try:n,p=listbox.get(sel[0]).split(" → ",1)
            except ValueError:return
            name.delete(0,tk.END); name.insert(0,n); path.delete(0,tk.END); path.insert(0,p)
        listbox.bind("<<ListboxSelect>>",select)
        def save():
            n=name.get().strip().lower(); p=path.get().strip()
            if not n or not p: messagebox.showwarning("Fehler","Name und Pfad dürfen nicht leer sein."); return
            self.programs[n]=p; self.save_all_settings(); reload_(); self.log(f"Programm gespeichert: {n}")
        def delete():
            n=name.get().strip().lower()
            if n in self.programs: del self.programs[n]; self.save_all_settings(); reload_(); name.delete(0,tk.END); path.delete(0,tk.END)
            else: messagebox.showwarning("Fehler","Programm nicht gefunden.")
        def start():
            p=path.get().strip()
            if p: open_program(p)
        for txt,cmd in [("Speichern",save),("Löschen",delete),("Starten",start)]: self._page_button(edit,txt,cmd).pack(anchor=tk.W,pady=5)
        reload_(); self.status_label.config(text="● PROGRAMME", fg=th["fg"])

# ============================================================
# BACKUP-FUNKTION
# ============================================================

def backup_database(custom_name=None):

    db_path = DB_FILE
    backup_dir = "backups"

    if not os.path.exists(db_path):

        print(
            "Keine Datenbank zum Sichern gefunden."
        )

        return False

    try:

        os.makedirs(
            backup_dir,
            exist_ok=True
        )

        timestamp = (
            datetime.datetime.now()
            .strftime("%Y-%m-%d_%H-%M-%S")
        )

        name = (
            custom_name
            if custom_name
            else "assistant"
        )

        # Problematische Zeichen entfernen.
        safe_name = "".join(
            c
            for c in name
            if c.isalnum()
            or c in ("-", "_")
        )

        if not safe_name:
            safe_name = "assistant"

        backup_file = os.path.join(
            backup_dir,
            f"{safe_name}_{timestamp}.db"
        )

        shutil.copy2(
            db_path,
            backup_file
        )

        # Nur DB-Dateien berücksichtigen.
        backups = sorted(
            [
                f
                for f in os.listdir(backup_dir)
                if f.endswith(".db")
            ]
        )

        # Maximal 10 Backups behalten.
        while len(backups) > 10:

            oldest = backups.pop(0)

            try:
                os.remove(
                    os.path.join(
                        backup_dir,
                        oldest
                    )
                )

            except Exception as e:

                print(
                    "Altes Backup konnte nicht gelöscht werden:",
                    e
                )

        print(
            f"Backup erstellt: {backup_file}"
        )

        return True

    except Exception as e:

        print(
            "Backup Fehler:",
            e
        )

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    init_db()

    root = tk.Tk()

    app = AssistantApp(
        root
    )

    root.mainloop()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()

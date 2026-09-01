# Sprachassistent v5.1

Deutschsprachiger Sprachassistent von Goldisoft.

## Enthalten

- `Sprachassistent.py` – aktuelle Programmversion
- `Sprachassistent_Anleitung_v5.1.pdf` – vollständige Anleitung
- `README.md` – Projektübersicht
- `CHANGELOG.md` – Änderungen
- `LICENSE` – MIT-Lizenz
- `.gitignore`

## Installation und Abhängigkeiten

Für die aktuelle Programmversion werden folgende externen Python-Pakete benötigt:

```text
requests
SpeechRecognition
RapidFuzz
opencv-python
Pillow
```

Installation aller Abhängigkeiten mit:

```bash
pip install -r requirements.txt
```

Module wie `tkinter`, `sqlite3`, `json`, `threading` und weitere Standardmodule gehören zu Python und werden deshalb nicht in `requirements.txt` aufgeführt.

## Manuelle Websuche

Der Assistent unterstützt den Sprachbefehl **„Websuche starten“**.

Ablauf:

1. „Websuche starten“
2. Der Assistent fragt: „Was möchtest du suchen?“
3. Die nächste gesprochene Eingabe wird als vollständige Suchfrage verwendet.
4. Wenn ein Satz die Frage vollständig beantwortet, wird nur dieser Satz ausgegeben.
5. Falls mehr Erklärung nötig ist, können bis zu drei passende Sätze ausgegeben werden.
6. Die Antwort kann anschließend gespeichert werden.

Die automatische Websuche bleibt getrennt davon bestehen.

**Version 5.1 – By Goldisoft 2026**

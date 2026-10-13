# Changelog

## Version 5.3
- GitHub-Paket und Dokumentation auf Version 5.3 aktualisiert.
- Versionsanzeige im Programm auf 5.3 aktualisiert.
- Dauerhafte, benutzerbezogene Speicherorte für Datenbank, Erinnerungen und Einstellungen beibehalten und dokumentiert.
- Persönliche Daten bleiben getrennt von den installierten Programmdateien.
- Temporäre Python-Bytecode-Dateien aus dem GitHub-Paket entfernt.
- Keine beabsichtigten Änderungen an den übrigen Funktionen.

## Version 5.2
- Windows-Sound-/Sprachausgabe ergänzt: Unter Windows wird die native `System.Speech`-Sprachausgabe über PowerShell verwendet.
- Neuer Sound-Treiber **windows** in der Treiberauswahl.
- Linux verwendet weiterhin die vorhandene `espeak-ng`-Ausgabe.
- Manuelle Websuche über „Websuche starten“ dokumentiert.
- Benutzerdatenbank und Erinnerungen werden unter `~/.local/share/Sprachassistent/` gespeichert.
- Einstellungen werden unter `~/.config/Sprachassistent/` gespeichert.
- Vorhandene Dateien aus dem bisherigen Startverzeichnis werden übernommen, sofern am neuen Speicherort noch keine entsprechende Datei vorhanden ist.

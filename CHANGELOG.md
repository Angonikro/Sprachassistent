# Changelog

## 5.3.2 – Alle installierten MBROLA-Module auswählbar
- In „Audio / Stimme“ gibt es jetzt ein Kontrollkästchen „Alle installierten MBROLA-Module anzeigen“.
- Ist es aktiviert, werden alle unter `/usr/share/mbrola` erkannten installierten Sprachdatenbanken zur Auswahl angeboten – unabhängig davon, ob sie Deutsch, Englisch oder eine andere Sprache enthalten.
- Ist es deaktiviert, bleibt die bisherige Auswahl aus deutschen und installierten englischen Stimmen bestehen.
- Die ausgewählte Stimme bleibt erhalten, wenn sie in der jeweiligen Auswahlliste vorhanden ist.
- Installierte englische Stimmen (en*/us*) werden automatisch in der Auswahlliste angezeigt.
- Die ausgewählte englische Stimme wird beim Sprechen nicht mehr durch mb-en1 überschrieben.
- README erklärt die optionale Installation weiterer Stimmen.
- Die tatsächlich verwendete Audio-/Stimme-Seite bietet jetzt mb-en1 zusätzlich zu mb-de1 bis mb-de8 an.
- Englischer Testtext wird bei ausgewählter englischer Programmsprache verwendet.
- `mb-en1` zur Stimmenauswahl in Audio / Stimme hinzugefügt.
- Deutsche Stimmen `mb-de1` bis `mb-de8` bleiben erhalten.
- Testansage und Speicherbestätigung folgen der gewählten Programmsprache.
- Die integrierte Hilfe besitzt jetzt eine vollständige englische Fassung mit denselben 34 Themenbereichen wie die deutsche Anleitung.
- Die Hilfe öffnet abhängig von der gespeicherten Sprache automatisch die deutsche oder englische Anleitung.
- Weitere Dialoge und Statusmeldungen werden im englischen Modus übersetzt.
- Weitere Beschriftungen und Dialogtexte für Audio, Backup, Termine, Gesichtserkennung und Fragen & Antworten ergänzt.
- Neu geöffnete Fenster und Meldungsdialoge werden im englischen Modus ebenfalls übersetzt.
- Dynamische Dashboard-Texte werden regelmäßig nachübersetzt.
- Zeit-, Fragen-, Assistent- und Gesprächsbeschriftungen ergänzt.
- Gesprächsstatus und Wetteranzeige im englischen Modus nachübersetzt.
- Englische Beschriftungen für Hauptnavigation, Dashboard, Seiten und Menüs ergänzt.
- Übersetzung wird nach Seitenwechsel erneut angewendet; Wechsel zurück auf Deutsch stellt Originaltexte wieder her.
- Spracheinstellung Deutsch / English in der Seitenleiste ergänzt und dauerhaft in der Benutzerkonfiguration gespeichert.
- Google-Spracherkennung verwendet je nach Auswahl `de-DE` oder `en-US`.
- Englische Sprachausgabe verwendet `en-us`; deutsche MBROLA-Stimmen bleiben im deutschen Modus erhalten.
- Englische Standard-Sprachbefehle werden auf die bestehenden Befehlsroutinen abgebildet.
- Englische PDF-Anleitung ergänzt.

## Version 5.3.1
- Versionsnummer in der Anwendung, README und Paketmetadaten auf 5.3.1 angehoben.
- Abhängigkeiten python3-pyaudio und mbrola hinzugefügt, für Spracherkennung und Mikrofoneingabe bleiben vollständig dokumentiert und im DEB berücksichtigt.
- Keine funktionalen Änderungen gegenüber Version 5.3.

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
## 5.3.2 – English MBROLA voice
- English speech output now uses the British English MBROLA voice `mb-en1`.
- The Debian package installs `mbrola-en1` automatically.
- README installation commands now include `mbrola-en1`.

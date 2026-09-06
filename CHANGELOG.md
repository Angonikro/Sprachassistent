## v5.2 Windows-Sound-Fix
- PDF-Anleitung auf v5.2 aktualisiert, inklusive Windows-/Linux-Installation und Windows-Sound-Hinweisen.
- Windows als auswählbarer Sound-Treiber ergänzt.
- Windows-Sprachausgabe bleibt über die native Windows-Speech-Ausgabe.
- VLC verwendet bei ausgewähltem Windows-Treiber die Windows-Audioausgabe.
- Linux-Soundtreiber und übrige Funktionen bleiben unverändert.

# Changelog

## Version 5.2

- Windows-Sound-/Sprachausgabe ergänzt: Unter Windows wird die native `System.Speech`-Sprachausgabe über PowerShell verwendet.
- Neuer Sound-Treiber **windows** in der Treiberauswahl.
- Linux verwendet weiterhin die vorhandene `espeak-ng`-Ausgabe.
- Lautstärke und Sprechgeschwindigkeit werden auch unter Windows aus den bestehenden Einstellungen übernommen.
- Keine Änderung an den übrigen Assistent-Funktionen.

## Version 5.2

- Bestehende Sprachassistent-Funktionen beibehalten.
- Manuelle Websuche über „Websuche starten“ dokumentiert.
- Hilfe und README um die manuelle Websuche ergänzt.
- Abhängigkeiten in `requirements.txt` dokumentiert.
- Plattformhinweis zu `fcntl` ergänzt.

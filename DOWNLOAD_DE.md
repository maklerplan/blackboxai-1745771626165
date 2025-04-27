# PDF-Vergleichstool - Download-Anleitung

## Option 1: Direkt-Download (Einfachste Methode)

1. Besuchen Sie die Projekt-Website:
   - Öffnen Sie [https://github.com/yourusername/pdf-comparison-tool](https://github.com/yourusername/pdf-comparison-tool)

2. Klicken Sie auf den grünen "Code" Button
   - Wählen Sie "Download ZIP"
   - Speichern Sie die ZIP-Datei auf Ihrem Computer

3. Entpacken der ZIP-Datei:
   - Rechtsklick auf die heruntergeladene ZIP-Datei
   - "Alle extrahieren..." oder "Hier entpacken" wählen
   - Wählen Sie einen Zielordner (z.B. "Dokumente")

## Option 2: Mit Git (Für Entwickler)

Wenn Sie Git installiert haben:
```bash
git clone https://github.com/yourusername/pdf-comparison-tool.git
cd pdf-comparison-tool
```

## Nach dem Download

1. Öffnen Sie den entpackten Ordner

2. Windows:
   - Doppelklick auf `setup.bat`
   ODER
   - Öffnen Sie die Kommandozeile im Ordner:
   ```bash
   setup.bat
   ```

3. Linux/Mac:
   - Öffnen Sie das Terminal im Ordner:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. Starten Sie das Tool:
   ```bash
   python src/main.py
   ```

## Systemanforderungen

- Windows 10/11 oder Linux/Mac
- Python 3.8 oder höher
- 500 MB freier Speicherplatz
- 4 GB RAM empfohlen

## Hilfe beim Download

Bei Problemen:

1. Download funktioniert nicht:
   - Prüfen Sie Ihre Internetverbindung
   - Versuchen Sie einen anderen Browser
   - Laden Sie die ZIP-Datei direkt herunter

2. ZIP lässt sich nicht entpacken:
   - Prüfen Sie, ob Sie genug Speicherplatz haben
   - Nutzen Sie 7-Zip oder WinRAR zum Entpacken
   - Wählen Sie einen Pfad ohne Sonderzeichen

3. Setup funktioniert nicht:
   - Stellen Sie sicher, dass Python installiert ist
   - Öffnen Sie eine neue Kommandozeile
   - Führen Sie das Setup als Administrator aus

## Nächste Schritte

Nach erfolgreichem Download und Setup:

1. Erstellen Sie Testordner:
```bash
mkdir angebote
mkdir rechnungen
```

2. Generieren Sie Test-PDFs:
```bash
python tools/generate_test_pdfs.py
```

3. Starten Sie das Tool:
```bash
python src/main.py
```

Detaillierte Installationsanweisungen finden Sie in der INSTALLATION_DE.md.

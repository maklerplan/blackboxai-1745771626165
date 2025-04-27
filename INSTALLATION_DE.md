# PDF-Vergleichstool - Installationsanleitung

## 1. Projekt herunterladen

### Option A: Mit Git
```bash
# Klonen Sie das Repository
git clone https://github.com/yourusername/pdf-comparison-tool.git

# Wechseln Sie in das Projektverzeichnis
cd pdf-comparison-tool
```

### Option B: Als ZIP-Datei
1. Laden Sie das Projekt als ZIP-Datei herunter
2. Entpacken Sie die ZIP-Datei
3. Öffnen Sie einen Terminal/Kommandozeile im entpackten Ordner

## 2. Python installieren (falls noch nicht vorhanden)

1. Besuchen Sie [python.org](https://www.python.org/downloads/)
2. Laden Sie Python 3.8 oder höher herunter
3. Führen Sie den Installer aus
4. Aktivieren Sie die Option "Add Python to PATH" während der Installation

## 3. Tool installieren

### Unter Windows:
```bash
# Führen Sie das Setup-Skript aus
setup.bat
```

### Unter Linux/Mac:
```bash
# Machen Sie das Setup-Skript ausführbar
chmod +x setup.sh

# Führen Sie das Setup-Skript aus
./setup.sh
```

## 4. Tool testen

```bash
# Generieren Sie Test-PDFs
python tools/generate_test_pdfs.py

# Führen Sie den Schnelltest aus
python quick_test.py
```

## 5. Eigene PDFs vergleichen

1. Erstellen Sie zwei Ordner für Ihre PDFs:
```bash
mkdir angebote
mkdir rechnungen
```

2. Kopieren Sie Ihre PDFs in die entsprechenden Ordner:
- Angebote in den `angebote` Ordner
- Rechnungen in den `rechnungen` Ordner

3. Starten Sie das Tool:
```bash
# Mit grafischer Oberfläche
python src/main.py

# ODER mit Ordnerüberwachung
python src/main.py --monitor
```

## Fehlerbehebung

### Python wird nicht erkannt
- Überprüfen Sie, ob Python im PATH ist
- Öffnen Sie eine neue Kommandozeile nach der Installation
- Versuchen Sie `python3` statt `python`

### Abhängigkeiten können nicht installiert werden
```bash
# Aktualisieren Sie pip
python -m pip install --upgrade pip

# Installieren Sie die Abhängigkeiten manuell
pip install -r requirements.txt
```

### Berechtigungsfehler
- Unter Linux/Mac: Führen Sie die Befehle mit `sudo` aus
- Unter Windows: Führen Sie die Kommandozeile als Administrator aus

## Hilfe & Support

Bei Problemen:
1. Prüfen Sie die Logs im `logs` Ordner
2. Führen Sie den Setup-Test aus:
```bash
python test_setup.py
```
3. Schauen Sie in die TESTING.md für weitere Testmöglichkeiten

## Ordnerstruktur

```
pdf-comparison-tool/
├── angebote/           # Ihre Angebots-PDFs hier ablegen
├── rechnungen/         # Ihre Rechnungs-PDFs hier ablegen
├── src/                # Quellcode des Tools
├── tools/              # Hilfsskripte
├── tests/              # Testfälle
└── config/             # Konfigurationsdateien
```

## Konfiguration

Die Konfigurationsdatei `config/settings.yaml` können Sie nach Ihren Bedürfnissen anpassen:
- Überwachte Ordner
- Aktualisierungsintervall
- PDF-Verarbeitungseinstellungen
- Benachrichtigungseinstellungen

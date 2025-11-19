# Setup-Anleitung: Ollama Spam Guard

Schritt-für-Schritt-Anleitung zur Ersteinrichtung des lokalen Spam-Filters.

---

## Voraussetzungen

### System
- **Python**: Version 3.8 oder höher
- **Ollama**: Installiert und lauffähig
- **Betriebssystem**: macOS, Linux oder Windows (WSL)

### IMAP-Zugang
- E-Mail-Account mit aktiviertem IMAP
- IMAP-Server-Adresse und Port
- Login-Daten (bei Gmail: App-Passwort erforderlich!)

---

## Installation

### 1. Repository klonen / herunterladen

```bash
git clone <repository-url> ollama-spam-guard
cd ollama-spam-guard
```

Oder ZIP herunterladen und entpacken.

---

### 2. Python-Dependencies installieren

```bash
pip install -r requirements.txt
```

**Installierte Pakete**:
- `python-dotenv` - Lädt .env Dateien
- `requests` - HTTP-Requests an Ollama
- `tqdm` - Progress-Bar
- `pyyaml` - YAML-Parser für accounts.yaml

**Bei Problemen**:
```bash
# Mit virtuellem Environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# oder
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

---

### 3. Ollama einrichten

#### Ollama installieren
```bash
# macOS (Homebrew)
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download von https://ollama.ai/download
```

#### Ollama starten
```bash
ollama serve
```

Läuft standardmäßig auf `http://localhost:11434`

**Wichtig**: Ollama muss während der Spam-Filterung laufen!
- Starte `ollama serve` in einem separaten Terminal
- Oder starte als Hintergrund-Dienst (siehe unten)

**Ollama als Dienst (optional)**:
```bash
# macOS (läuft automatisch nach Installation)
brew services start ollama

# Linux (systemd)
sudo systemctl enable ollama
sudo systemctl start ollama
```

#### LLM-Modell herunterladen
```bash
# Empfohlenes Modell (14B Parameter, ~9GB)
ollama pull qwen2.5:14b-instruct

# Alternativ: Kleineres Modell für schnellere Tests
ollama pull qwen2.5:7b

# Alternative: Spezialisiertes Spam-Modell
ollama pull pravitor/spam-detect
```


## Modellauswahl

Die Wahl des richtigen Modells hängt von deiner Hardware und deinen Anforderungen ab:

### Für schwache Systeme (bis 8GB RAM)
| Modell | Größe | Geschwindigkeit | Genauigkeit | Besonderheiten |
|--------|-------|-----------------|-------------|----------------|
| qwen2.5:1.5b | ~1GB | ⚡⚡⚡ Sehr schnell | ⭐⭐⭐ Gut | Mehrsprachig optimiert |
| rosemarla/qwen3-classify | ~1.2GB | ⚡⚡⚡ Sehr schnell | ⭐⭐⭐ Gut | Spezialisiert für Spam-Erkennung |
| deepseek-r1:1.5b | ~1.1GB | ⚡⚡⚡ Sehr schnell | ⭐⭐ OK | Nur für Englisch/Chinesisch empfohlen |

### Für mittlere Systeme (8-16GB RAM)
| Modell | Größe | Geschwindigkeit | Genauigkeit | Besonderheiten |
|--------|-------|-----------------|-------------|----------------|
| **qwen2.5:7b** | ~5GB | ⚡⚡ Schnell | ⭐⭐⭐⭐ Sehr gut | **✅ Empfohlen für deutsche E-Mails** |
| pravitor/spam-detect | ~4GB | ⚡⚡ Schnell | ⭐⭐⭐ Gut | Deutsche Trainingsdaten vorhanden |
| deepseek-r1:7b | ~4.7GB | ⚡⚡ Schnell | ⭐⭐⭐ Gut | Begrenzt für deutsche Texte |
| deepseek-r1:8b | ~5.2GB | ⚡⚡ Schnell | ⭐⭐⭐ Gut | Neueste Version (0528) |

### Für starke Systeme (16GB+ RAM)
| Modell | Größe | Geschwindigkeit | Genauigkeit | Besonderheiten |
|--------|-------|-----------------|-------------|----------------|
| **qwen2.5:14b-instruct** | ~9GB | ⚡ Mittel | ⭐⭐⭐⭐⭐ Exzellent | **✅ Top-Wahl für deutsche Business-E-Mails** |
| deepseek-r1:14b | ~9GB | ⚡ Mittel | ⭐⭐⭐⭐ Sehr gut | Starkes Reasoning, Sprachbeschränkungen |
| deepseek-r1:32b | ~20GB | 🐌 Langsam | ⭐⭐⭐⭐⭐ Exzellent | Für High-End-Systeme |

**💡 Empfehlung für deutsche E-Mails**: Die **Qwen2.5-Modelle** sind die erste Wahl, da sie explizit für über 29 Sprachen (inkl. Deutsch) trainiert wurden. DeepSeek-R1 ist primär für Englisch/Chinesisch optimiert und kann bei deutschen Texten zu Sprachvermischungen neigen.

**Modell installieren**:
```bash
# Beispiel: Mittleres System
ollama pull qwen2.5:7b

# Beispiel: Starkes System
ollama pull qwen2.5:14b-instruct
```

--- 4. Konfigurationsdateien erstellen

#### .env erstellen
```bash
cp .env.example .env
```

**Bearbeite `.env`**:
```bash
# LLM-Modell (das du mit ollama pull geladen hast)
SPAM_MODEL=qwen2.5:14b-instruct

# Filter-Modus
FILTER_MODE=count  # Oder "days" für zeitbasiert
LIMIT=20           # Für erste Tests: niedrigen Wert wählen!

# Pfade (Standard-Werte sind meist OK)
ACCOUNTS_FILE=accounts.yaml
LOG_PATH=~/spam_filter.log
```

#### accounts.yaml erstellen
```bash
cp accounts.yaml.example accounts.yaml
```

**Bearbeite `accounts.yaml`**:
```yaml
accounts:
  - name: "Mein Hauptaccount"
    user: "deine@email.de"
    password: "dein-passwort"
    server: "imap.gmx.net"      # Server deines Providers
    port: 993                    # Meist 993 für SSL
    spam_folder: "Spamverdacht" # Provider-spezifisch!
    enabled: true                # WICHTIG: auf true setzen!
```

**Provider-spezifische Server**:

| Provider | IMAP-Server | Port | Spam-Ordner | Besonderheiten |
|----------|-------------|------|-------------|----------------|
| **GMX** | `imap.gmx.net` | 993 | `Spamverdacht` | IMAP muss in Einstellungen aktiviert sein |
| **Gmail** | `imap.gmail.com` | 993 | `[Gmail]/Spam` | **App-Passwort erforderlich!** (siehe unten) |
| **Outlook/Hotmail** | `outlook.office365.com` | 993 | `Junk` | Nicht `imap.hotmail.com` verwenden |
| **Web.de** | `imap.web.de` | 993 | `Spamverdacht` | Wie GMX |
| **All-Inkl/KAS** | `w0xxxxx.kasserver.com` | 993 | `Spam` | Deine Server-Nummer einsetzen |
| **HostEurope** | `imap.hosteurope.de` | 993 | `Spam` | - |
| **1&1/IONOS** | `imap.ionos.de` | 993 | `Spam` | - |
| **Strato** | `imap.strato.de` | 993 | `Spam` | - |

---

### 5. Gmail App-Passwort erstellen (nur für Gmail)

Gmail erlaubt keine normalen Passwörter für IMAP!

1. Gehe zu [Google Account Security](https://myaccount.google.com/security)
2. Aktiviere **2-Faktor-Authentifizierung** (falls noch nicht aktiv)
3. Gehe zu [App-Passwörter](https://myaccount.google.com/apppasswords)
4. Wähle **Mail** und **Anderes Gerät**
5. Kopiere das generierte Passwort (16 Zeichen ohne Leerzeichen)
6. Trage es in `accounts.yaml` ein:

```yaml
- name: "Gmail"
  user: "max@gmail.com"
  password: "abcdefghijklmnop"  # ← Das App-Passwort
  server: "imap.gmail.com"
  port: 993
  spam_folder: "[Gmail]/Spam"
  enabled: true
```

---

## Erster Testlauf

### 1. Verbindungstest durchführen

**Wichtig**: Teste zuerst alle Verbindungen, bevor du E-Mails verarbeitest!

```bash
python test_connection.py
```

**Was wird getestet?**
1. **Ollama-Verbindung**: Ist Ollama erreichbar auf `http://localhost:11434`?
2. **LLM-Modell**: Ist das konfigurierte Modell installiert (`qwen2.5:14b-instruct`)?
3. **E-Mail-Accounts**: Für jeden Account in `accounts.yaml`:
   - SSL-Verbindung zum IMAP-Server
   - Login mit Benutzername/Passwort
   - INBOX-Zugriff (zeigt Anzahl der Nachrichten)
   - Spam-Ordner existiert und ist zugreifbar

**Erwartete Ausgabe bei Erfolg**:
```
🔍 IMAP Spam-Filter: Verbindungstest
============================================================

============================================================
  Test 1: Ollama-Verbindung
============================================================
✅ Ollama erreichbar: OK
   http://localhost:11434

============================================================
  Test 2: LLM-Modell 'qwen2.5:14b-instruct'
============================================================
✅ Modell 'qwen2.5:14b-instruct' verfügbar: OK

📋 Installierte Modelle (9):
   - qwen2.5:1.5b
   - qwen2.5:7b
   - qwen2.5:14b-instruct
   ...

============================================================
  Test 3: E-Mail-Accounts (1 konfiguriert)
============================================================

📬 Account 1/1: Mein Hauptaccount
   User: deine@email.de
   Server: imap.gmx.net:993
✅ SSL-Verbindung: OK
✅ Login: OK
✅ INBOX: OK
   42 Nachrichten
✅ Spam-Ordner 'Spamverdacht': OK

============================================================
  Zusammenfassung
============================================================
✅ Ollama-Verbindung: OK
✅ LLM-Modell verfügbar: OK
✅ E-Mail-Accounts: OK

============================================================
✅ Alle Tests erfolgreich!
   Du kannst jetzt das Spam-Filter-Script ausführen:
   python src/spam_filter.py
============================================================
```

**Bei Fehlern**:
- Das Script zeigt **konkrete Lösungsvorschläge** für jeden fehlgeschlagenen Test
- Häufige Probleme:
  - **Ollama nicht gestartet**: `ollama serve` ausführen
  - **Modell fehlt**: `ollama pull qwen2.5:14b-instruct`
  - **Gmail Login-Fehler**: App-Passwort statt normalem Passwort verwenden
  - **Spam-Ordner nicht gefunden**: Ordner im E-Mail-Client erstellen oder Namen in `accounts.yaml` anpassen
- Behebe die Probleme und führe `python test_connection.py` erneut aus

---

### 2. Ersten Spam-Filter-Durchlauf starten

**Wichtig**: Starte mit **niedrigem LIMIT** für erste Tests!

Bearbeite `.env`:
```bash
FILTER_MODE=count
LIMIT=5  # Nur 5 E-Mails zum Testen
```

Dann starte das Script:
```bash
python src/spam_filter.py
```

**Erwartete Ausgabe**:
```
==============================================================
🤖 LLM-basierter IMAP Spam-Filter (Multi-Account)
==============================================================
   Modell: qwen2.5:14b-instruct
   Accounts: 1
   Filter: Letzte 5 E-Mails pro Account
   Log: /Users/you/spam_filter.log
==============================================================

🔍 Prüfe Ollama-Verfügbarkeit...
✅ Ollama läuft

────────────────────────────────────────────────────────────
📬 Account 1/1: deine@email.de
   Server: imap.gmx.net
────────────────────────────────────────────────────────────
🔌 Verbinde zu imap.gmx.net:993...
🔐 Login als deine@email.de...
📬 Öffne INBOX...

🔍 Suche letzte 5 E-Mails...
📧 Analysiere 5 E-Mail(s)...

[... Verarbeitung ...]
```

---

## Produktiv-Einrichtung

### 1. Filter-Limit erhöhen

Nach erfolgreichen Tests in `.env`:
```bash
FILTER_MODE=count
LIMIT=50  # Oder höher

# Alternativ: Zeitbasiert
FILTER_MODE=days
DAYS_BACK=7
```

### 2. Weitere Accounts hinzufügen

In `accounts.yaml`:
```yaml
accounts:
  - name: "Hauptaccount"
    # ... bereits konfiguriert
    enabled: true

  - name: "Zweitaccount"
    user: "zweites@mail.de"
    password: "passwort"
    server: "imap.server.de"
    port: 993
    spam_folder: "Spam"
    enabled: true  # ← Aktivieren!
```

### 3. Automatisierung (optional)

#### Cronjob (macOS/Linux)
```bash
crontab -e
```

Füge hinzu (täglich um 6 Uhr):
```cron
0 6 * * * cd /pfad/zum/projekt && /usr/bin/python3 src/spam_filter.py >> ~/spam_filter_cron.log 2>&1
```

#### Launchd (macOS)
Erstelle `~/Library/LaunchAgents/com.user.spam-filter.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.spam-filter</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/pfad/zum/projekt/src/spam_filter.py</string>
    </array>
    <key>StartInterval</key>
    <integer>21600</integer> <!-- 6 Stunden = 21600 Sekunden -->
</dict>
</plist>
```

Aktivieren:
```bash
launchctl load ~/Library/LaunchAgents/com.user.spam-filter.plist
```

---

## Sicherheitshinweise

### Dateiberechtigungen

```bash
# Nur Owner kann lesen/schreiben
chmod 600 accounts.yaml
chmod 600 .env
```

### Backups

```bash
# Verschlüsseltes Backup
gpg -c accounts.yaml
# → Erstellt accounts.yaml.gpg

# Wiederherstellen
gpg accounts.yaml.gpg
```

### Git

`.gitignore` ist bereits konfiguriert:
- ✅ `accounts.yaml` wird NICHT eingecheckt
- ✅ `.env` wird NICHT eingecheckt
- ✅ `*.log` wird NICHT eingecheckt

**Niemals** diese Dateien committen (enthalten Passwörter!)

---

## Nächste Schritte

Nach erfolgreichem Setup:

1. **Produktiv-Betrieb einrichten**:
   - Filter-Limit erhöhen (siehe "Produktiv-Einrichtung" oben)
   - Weitere Accounts in `accounts.yaml` hinzufügen
   - Optional: Automatisierung per Cronjob/Launchd

2. **Weitere Dokumentation**:
   - 📖 [CONFIGURATION.md](CONFIGURATION.md) - Detaillierte Konfigurationsreferenz
   - 🔧 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problemlösungen und häufige Fehler

---

## Checkliste: Setup vollständig?

Gehe diese Schritte durch, um sicherzustellen, dass alles richtig konfiguriert ist:

- [ ] **Python 3.8+** installiert (`python --version`)
- [ ] **Dependencies** installiert (`make install` oder `pip install -r requirements.txt`)
- [ ] **Ollama** läuft (`ollama serve` oder als Dienst)
- [ ] **LLM-Modell** heruntergeladen (`ollama pull qwen2.5:14b-instruct`)
- [ ] **`.env`** erstellt und angepasst (aus `.env.example`)
- [ ] **`accounts.yaml`** erstellt und angepasst (aus `accounts.yaml.example`)
- [ ] Mindestens **ein Account** mit `enabled: true`
- [ ] **Verbindungstest erfolgreich** (`make test` → alle ✅)
- [ ] **Erster Testlauf erfolgreich** (`make run` mit `LIMIT=5`)
- [ ] **Log-Datei** wird erstellt und beschrieben (`~/spam_filter.log`)

✅ **Alles erledigt? Dann bist du bereit für den produktiven Einsatz!**

---

## Praktische Shortcuts (Makefile)

Das Projekt enthält ein Makefile mit praktischen Kurzbefehlen:

```bash
make help       # Alle verfügbaren Befehle anzeigen
make install    # Dependencies installieren
make test       # Verbindungstest (Ollama, LLM, IMAP)
make run        # Spam-Filter starten
make folders    # IMAP-Ordnerstruktur anzeigen
make clean      # Cache-Dateien löschen
make status     # Projekt-Status prüfen
```

**Empfohlener Workflow:**
```bash
# 1. Setup
make install

# 2. Testen
make test

# 3. Ordnerstruktur prüfen (falls Spam-Ordner unklar)
make folders

# 4. Spam-Filter starten
make run
```

---

## Tipps für den produktiven Einsatz

### Starte mit kleinen Schritten
1. **Woche 1**: `LIMIT=10`, täglich manuell ausführen
2. **Woche 2**: `LIMIT=50`, prüfe Spam-Ordner auf False Positives
3. **Ab Woche 3**: `FILTER_MODE=days` mit `DAYS_BACK=1`, per Cronjob automatisieren

### Überwache das Log
```bash
# Letzte 50 Zeilen anzeigen
tail -50 ~/spam_filter.log

# Live-Monitoring
tail -f ~/spam_filter.log
```

### False Positives vermeiden
- Prüfe regelmäßig den Spam-Ordner
- Bei häufigen Fehlern: Modell wechseln oder Prompt anpassen (in `src/spam_filter.py`)
- Wichtige Absender zur Whitelist hinzufügen (erfordert Code-Anpassung)

# Troubleshooting: Häufige Probleme und Lösungen

Lösungen für typische Fehler beim Betrieb des Spam-Filters.

---

## Verbindungsprobleme

### ❌ "Ollama nicht erreichbar!"

**Symptom**:
```
❌ Ollama nicht erreichbar!
   Starte in anderem Terminal: ollama serve
```

**Ursachen & Lösungen**:

1. **Ollama läuft nicht**
   ```bash
   # Starte Ollama
   ollama serve
   ```

2. **Falscher Port/URL**
   ```bash
   # In .env prüfen
   OLLAMA_URL=http://localhost:11434/api/generate
   
   # Ollama-Status testen
   curl http://localhost:11434/api/tags
   ```

3. **Firewall blockiert**
   - Erlaube Localhost-Verbindungen auf Port 11434
   - macOS: Systemeinstellungen → Sicherheit → Firewall

---

### ❌ "IMAP-Fehler: LOGIN failed"

**Symptom**:
```
❌ IMAP-Fehler: LOGIN failed
💡 Mögliche Ursachen:
   - Falsches Passwort
   - IMAP nicht aktiviert
```

**Lösungen nach Provider**:

#### GMX / Web.de
1. **IMAP aktivieren**:
   - Einstellungen → POP3/IMAP → IMAP aktivieren
   
2. **Passwort prüfen**:
   ```yaml
   # In accounts.yaml
   password: "dein-richtiges-passwort"
   ```

#### Gmail
1. **App-Passwort verwenden** (NICHT normales Passwort!):
   - Gehe zu https://myaccount.google.com/apppasswords
   - Erstelle neues App-Passwort
   - Kopiere in `accounts.yaml` (ohne Leerzeichen)
   
2. **2FA aktivieren**:
   - App-Passwörter erfordern aktivierte 2-Faktor-Auth

3. **"Weniger sichere Apps"** (veraltet):
   - Nicht mehr nötig/möglich → Nutze App-Passwörter

#### Outlook/Hotmail
1. **Server prüfen**:
   ```yaml
   server: "outlook.office365.com"  # NICHT imap.hotmail.com
   ```

2. **2FA & App-Passwort**:
   - Bei aktivierter 2FA: App-Passwort erstellen
   - https://account.microsoft.com/security

#### All-Inkl / KAS
1. **IMAP aktivieren**:
   - KAS → E-Mail → Postfächer → IMAP aktivieren
   
2. **Richtiger Server**:
   ```yaml
   server: "w0xxxxx.kasserver.com"  # Deine Server-Nummer!
   ```

---

### ❌ "Verbindungsfehler: [SSL: CERTIFICATE_VERIFY_FAILED]"

**Symptom**:
SSL-Zertifikat wird nicht akzeptiert

**Lösung**:
```bash
# macOS: Install Certificates.command ausführen
/Applications/Python\ 3.x/Install\ Certificates.command

# Oder certifi aktualisieren
pip install --upgrade certifi
```

---

## Konfigurationsprobleme

### ❌ "accounts.yaml nicht gefunden"

**Symptom**:
```
FileNotFoundError: ❌ accounts.yaml nicht gefunden: /pfad/zu/accounts.yaml
```

**Lösung**:
```bash
# Erstelle aus Vorlage
cp accounts.yaml.example accounts.yaml

# Dann anpassen!
```

---

### ❌ "Keine aktiven Accounts gefunden (enabled: true)"

**Symptom**:
```
ValueError: Keine aktiven Accounts in accounts.yaml gefunden (enabled: true)
```

**Lösung**:
In `accounts.yaml` mindestens einen Account aktivieren:
```yaml
accounts:
  - name: "Account 1"
    # ... weitere Felder
    enabled: true  # ← WICHTIG: auf true setzen!
```

---

### ❌ "Fehler beim Parsen von accounts.yaml"

**Symptom**:
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Ursachen**:

1. **Falsche Einrückung** (häufigster Fehler!)
   ```yaml
   # ❌ FALSCH (Tabs oder falsche Spaces)
   accounts:
   - name: "Test"
     user: "test"
   
   # ✅ RICHTIG (2 oder 4 Spaces konsistent)
   accounts:
     - name: "Test"
       user: "test"
   ```

2. **Fehlende Anführungszeichen** bei Sonderzeichen:
   ```yaml
   # ❌ FALSCH
   password: mein:pass:wort
   
   # ✅ RICHTIG
   password: "mein:pass:wort"
   ```

3. **Fehlender Doppelpunkt**:
   ```yaml
   # ❌ FALSCH
   name "Test"
   
   # ✅ RICHTIG
   name: "Test"
   ```

**YAML-Syntax testen**:
```bash
python -c "import yaml; yaml.safe_load(open('accounts.yaml'))"
# Kein Output = OK
# Fehler = Syntax-Problem
```

---

### ❌ "Account 'xyz' fehlen Felder: ['password', 'server']"

**Symptom**:
Pflichtfelder in Account nicht ausgefüllt

**Lösung**:
Prüfe, dass **alle** Felder vorhanden sind:
```yaml
- name: "Account Name"      # ✅ Pflicht
  user: "email@domain.de"   # ✅ Pflicht
  password: "passwort"      # ✅ Pflicht
  server: "imap.server.de"  # ✅ Pflicht
  port: 993                 # ✅ Pflicht
  spam_folder: "Spam"       # ✅ Pflicht
  enabled: true             # ✅ Pflicht
```

---

## E-Mail-Verarbeitungsprobleme

### ❌ "E-Mail-Suche fehlgeschlagen"

**Symptom**:
```
❌ E-Mail-Suche fehlgeschlagen
```

**Ursachen**:

1. **INBOX existiert nicht**:
   - Manche Provider nutzen andere Namen
   - Lösung: Prüfe Ordnerstruktur (Code-Anpassung nötig)

2. **SINCE-Datum ungültig** (bei `FILTER_MODE=days`):
   ```bash
   # Wechsel zu count-Modus zum Testen
   FILTER_MODE=count
   LIMIT=10
   ```

---

### ❌ "Spam-Verschiebung fehlgeschlagen"

**Symptom**:
```
⚠️  Verschiebung fehlgeschlagen: [TRYCREATE] No such mailbox
```

**Lösung**:

1. **Spam-Ordner existiert nicht**:
   - Erstelle Ordner manuell im E-Mail-Client
   - Oder nutze anderen Namen:
   
   ```yaml
   spam_folder: "Junk"  # Statt "Spam"
   ```

2. **Falsche Schreibweise**:
   - GMX: `"Spamverdacht"` (nicht `"Spam"`)
   - Gmail: `"[Gmail]/Spam"` (mit Klammern!)
   - Outlook: `"Junk"` (nicht `"Spam"`)

3. **Groß-/Kleinschreibung** beachten:
   ```yaml
   spam_folder: "Spam"  # ✅
   spam_folder: "spam"  # ❌ (bei manchen Servern)
   ```

---

### ❌ LLM antwortet nicht mit "SPAM" oder "HAM"

**Symptom**:
E-Mails werden alle als HAM klassifiziert, obwohl offensichtlich Spam

**Ursachen & Lösungen**:

1. **Falsches Modell**:
   ```bash
   # In .env - Empfohlene Modelle für deutsche E-Mails
   SPAM_MODEL=qwen2.5:7b              # Guter Kompromiss (5GB)
   SPAM_MODEL=qwen2.5:14b-instruct    # Beste Genauigkeit (9GB)
   
   # Spezialisiertes Spam-Modell (falls verfügbar)
   SPAM_MODEL=pravitor/spam-detect    # Deutsche Trainingsdaten (4GB)
   ```
   
   💡 Siehe [Modellübersicht in SETUP.md](SETUP.md#modellauswahl) für Details

2. **Modell nicht geladen**:
   ```bash
   ollama pull qwen2.5:14b-instruct
   ```

3. **Prompt anpassen** (Code-Änderung):
   - Öffne `src/spam_filter.py`
   - Funktion `detect_spam()` → Prompt optimieren

---

## Performance-Probleme

### 🐌 "Script ist sehr langsam"

**Ursachen & Lösungen**:

1. **Großes Modell**:
   ```bash
   # Schnelleres Modell nutzen
   SPAM_MODEL=qwen2.5:7b  # Statt 14b
   ```

2. **Zu viele E-Mails**:
   ```bash
   # Limit reduzieren
   LIMIT=20  # Statt 50+
   ```

3. **CPU-Last**:
   - Ollama nutzt CPU/GPU intensiv
   - Schließe andere Programme
   - Nutze GPU-beschleunigtes Ollama (CUDA/Metal)

4. **Netzwerk-Timeouts**:
   - Langsame IMAP-Server
   - VPN kann verlangsamen

**Geschwindigkeitsvergleich**:
| Modell | ~Zeit/E-Mail | Empfehlung |
|--------|--------------|------------|
| qwen2.5:1.5b | ~0.5s | ⚡ Schnelle Tests |
| qwen2.5:7b | ~1.5s | ✅ Guter Kompromiss |
| qwen2.5:14b-instruct | ~3s | 🎯 Beste Genauigkeit |

---

## Log-Probleme

### ❌ "Permission denied: ~/spam_filter.log"

**Symptom**:
Log-Datei kann nicht erstellt werden

**Lösung**:
```bash
# Berechtigungen prüfen
ls -la ~/spam_filter.log

# Datei löschen und neu erstellen lassen
rm ~/spam_filter.log

# Oder anderen Pfad nutzen
# In .env:
LOG_PATH=/tmp/spam_filter.log
```

---

### 📄 "Log-Datei zu groß"

**Symptom**:
Log-Datei wächst auf mehrere MB/GB

**Lösung**:
```bash
# Log rotieren
mv ~/spam_filter.log ~/spam_filter.log.old
gzip ~/spam_filter.log.old

# Log truncaten
> ~/spam_filter.log  # Leert Datei

# Automatische Rotation (Linux)
logrotate /etc/logrotate.d/spam-filter
```

---

## Allgemeine Debugging-Tipps

### 0. Verbindungen testen

**Vor dem Debugging**: Nutze das Test-Script!
```bash
python test_connection.py
```

Prüft automatisch:
- ✅ Ollama-Verbindung
- ✅ LLM-Modell verfügbar
- ✅ IMAP-Login für alle Accounts
- ✅ Spam-Ordner vorhanden

### 1. Verbose-Logging aktivieren

In `src/spam_filter.py` ändern:
```python
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,  # Statt INFO
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### 2. Einzelnen Account testen

In `accounts.yaml` alle außer einem deaktivieren:
```yaml
accounts:
  - name: "Test"
    enabled: true   # ← Nur dieser aktiv
  - name: "Account 2"
    enabled: false  # ← Deaktiviert
```

### 3. Python-Fehler analysieren

```bash
# Mit Traceback
python src/spam_filter.py 2>&1 | tee error.log

# Syntax-Check
python -m py_compile src/spam_filter.py
```

### 4. Konfiguration ausgeben

```bash
python -c "
from src.config import *
print('Accounts:', EMAIL_ACCOUNTS)
print('Modell:', SPAM_MODEL)
print('Filter:', FILTER_MODE, LIMIT, DAYS_BACK)
"
```

---

## Bekannte Einschränkungen

### Gmail Quota
- Gmail limitiert IMAP-Zugriffe
- Bei Überschreitung: Warte 24h oder nutze `LIMIT=10`

### Multipart/Alternative E-Mails
- HTML-only E-Mails haben keinen Text-Body
- Script nutzt Fallback auf HTML (begrenzt)

### Nicht-UTF-8 Kodierung
- Exotische Zeichenkodierungen können Probleme machen
- Script nutzt `errors='ignore'` als Fallback

---

## Häufige Fehlermeldungen

| Fehler | Bedeutung | Lösung |
|--------|-----------|--------|
| `AUTHENTICATIONFAILED` | Login fehlgeschlagen | Passwort/Username prüfen |
| `[TRYCREATE]` | Ordner existiert nicht | Spam-Ordner erstellen |
| `ConnectionRefusedError` | Ollama läuft nicht | `ollama serve` starten |
| `ModuleNotFoundError` | Dependency fehlt | `pip install -r requirements.txt` |
| `yaml.scanner.ScannerError` | YAML-Syntax falsch | Einrückung prüfen |

---

## Hilfe erhalten

### 1. Log-Datei prüfen
```bash
tail -50 ~/spam_filter.log
```

### 2. Issue erstellen
- Füge relevante Log-Auszüge bei
- Gib Provider an (GMX, Gmail, etc.)
- **NIEMALS** Passwörter posten!

### 3. Debug-Info sammeln
```bash
# System
python --version
pip list | grep -E "dotenv|requests|tqdm|yaml"

# Ollama
ollama list
curl -s http://localhost:11434/api/tags | python -m json.tool

# Config (OHNE Passwörter!)
cat .env | grep -v PASSWORD
```

---

## Weiterführende Dokumentation

- **Setup & Installation**: [SETUP.md](SETUP.md)
- **Konfiguration**: [CONFIGURATION.md](CONFIGURATION.md)

---

## Benchmark-Probleme

### ❌ "No module named 'pandas'" (oder andere Module)

**Symptom**:
Der Benchmark startet nicht und meldet fehlende Python-Module.

**Lösung**:
Du nutzt wahrscheinlich nicht das virtuelle Environment.
1.  Führe `make install` aus, um alle Abhängigkeiten zu installieren.
2.  Starte den Benchmark immer mit `make benchmark` (das nutzt automatisch das richtige Environment).

### ❌ "No models found in Ollama"

**Symptom**:
Die Liste der Modelle im Benchmark ist leer oder es erscheint eine Warnung.

**Lösung**:
1.  Stelle sicher, dass Ollama läuft (`ollama serve`).
2.  Prüfe, ob du Modelle heruntergeladen hast:
    ```bash
    ollama list
    ```
3.  Falls leer, lade ein Modell:
    ```bash
    ollama pull qwen2.5:14b-instruct
    ```

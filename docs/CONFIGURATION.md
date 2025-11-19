# Konfigurationsübersicht

## Dateien

### 1. `accounts.yaml` - E-Mail-Accounts
**Zweck**: Konfiguration aller E-Mail-Konten  
**Format**: YAML  
**Versionierung**: ❌ NICHT in Git (enthält Passwörter!)  

**Beispiel**:
```yaml
accounts:
  - name: "Hauptaccount"
    user: "max@gmx.de"
    password: "geheim123"
    server: "imap.gmx.net"
    port: 993
    spam_folder: "Spamverdacht"
    enabled: true  # true = aktiv, false = deaktiviert
```

**Pflichtfelder**:
- `name`: Beschreibender Name (frei wählbar)
- `user`: E-Mail-Adresse oder Username
- `password`: IMAP-Passwort (bei Gmail: App-Passwort!)
- `server`: IMAP-Server (z.B. `imap.gmx.net`)
- `port`: IMAP-Port (meist `993` für SSL)
- `spam_folder`: Name des Spam-Ordners auf dem Server
- `enabled`: `true` oder `false`

---

### 2. `.env` - Script-Einstellungen
**Zweck**: Globale Konfiguration des Spam-Filters  
**Format**: Key=Value  
**Versionierung**: ❌ NICHT in Git  

**Beispiel**:
```bash
# LLM-Konfiguration
OLLAMA_URL=http://localhost:11434/api/generate
SPAM_MODEL=qwen2.5:14b-instruct

# Filter-Modus
FILTER_MODE=count  # "count" oder "days"
LIMIT=50           # bei MODE=count
DAYS_BACK=7        # bei MODE=days

# Pfade
ACCOUNTS_FILE=accounts.yaml
LOG_PATH=~/spam_filter.log
```

**Alle Optionen**:

| Variable | Werte | Beschreibung |
|----------|-------|--------------|
| `OLLAMA_URL` | URL | Ollama API Endpoint |
| `SPAM_MODEL` | Modellname | Zu nutzendes LLM (z.B. `qwen2.5:14b-instruct`) |
| `FILTER_MODE` | `count`/`days` | Filtermodus |
| `LIMIT` | Zahl | Anzahl E-Mails (bei `count`) |
| `DAYS_BACK` | Zahl | Tage zurück (bei `days`) |
| `ACCOUNTS_FILE` | Pfad | Pfad zu accounts.yaml |
| `LOG_PATH` | Pfad | Log-Datei |

---

### 3. Template-Dateien (mit `.example`)

#### `accounts.yaml.example`
**Zweck**: Vorlage für `accounts.yaml`  
**Versionierung**: ✅ IN Git (ohne echte Passwörter)  

**Verwendung**:
```bash
cp accounts.yaml.example accounts.yaml
# Dann accounts.yaml anpassen
```

#### `.env.example`
**Zweck**: Vorlage für `.env`  
**Versionierung**: ✅ IN Git  

**Verwendung**:
```bash
cp .env.example .env
# Dann .env anpassen
```

---

## Konfigurationshierarchie

```
┌─────────────────────────────────────┐
│         accounts.yaml               │
│  ┌─────────────────────────────┐   │
│  │ Account 1 (enabled: true)   │   │ ← Wird verarbeitet
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Account 2 (enabled: false)  │   │ ← Wird übersprungen
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Account 3 (enabled: true)   │   │ ← Wird verarbeitet
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
                 ↓
        Script lädt Config
                 ↓
┌─────────────────────────────────────┐
│              .env                   │
│  • FILTER_MODE = count              │ ← Gilt für ALLE Accounts
│  • LIMIT = 50                       │
│  • SPAM_MODEL = qwen2.5:14b-instruct│
└─────────────────────────────────────┘
```

**Pro Account**: Server, User, Password, Spam-Ordner  
**Global**: Filter-Modus, LLM-Modell, Log-Pfad

---

## Typische Konfigurationen

### Setup 1: Ein Account, letzte 20 E-Mails
**accounts.yaml**:
```yaml
accounts:
  - name: "Hauptaccount"
    user: "max@gmx.de"
    # ... weitere Felder
    enabled: true
```

**.env**:
```bash
FILTER_MODE=count
LIMIT=20
```

---

### Setup 2: Drei Accounts, letzte 7 Tage
**accounts.yaml**:
```yaml
accounts:
  - name: "GMX"
    # ...
    enabled: true
  - name: "Gmail"
    # ...
    enabled: true
  - name: "Outlook"
    # ...
    enabled: true
```

**.env**:
```bash
FILTER_MODE=days
DAYS_BACK=7
```

---

### Setup 3: Fünf Accounts, nur zwei aktiv
**accounts.yaml**:
```yaml
accounts:
  - name: "Wichtig 1"
    enabled: true     # ← wird verarbeitet
  - name: "Wichtig 2"
    enabled: true     # ← wird verarbeitet
  - name: "Urlaub"
    enabled: false    # ← deaktiviert
  - name: "Alt"
    enabled: false    # ← deaktiviert
  - name: "Test"
    enabled: false    # ← deaktiviert
```

---

## Best Practices

### ✅ DO
- Nutze `enabled: false` statt Accounts zu löschen
- Gib Accounts sprechende Namen (z.B. "Arbeit", "Privat")
- Sichere `accounts.yaml` verschlüsselt
- Teste neue Accounts mit `LIMIT=5` erst

### ❌ DON'T
- Niemals `accounts.yaml` oder `.env` in Git committen
- Keine Klartext-Passwörter in Kommentare schreiben
- Nicht mehrere `accounts.yaml` Dateien anlegen

---

## Validierung

### Config testen ohne E-Mails abzurufen:
```bash
python -c "from src.config import EMAIL_ACCOUNTS; print(f'{len(EMAIL_ACCOUNTS)} aktive Accounts'); [print(f'  - {a[\"name\"]}') for a in EMAIL_ACCOUNTS]"
```

### YAML-Syntax prüfen:
```bash
python -c "import yaml; yaml.safe_load(open('accounts.yaml'))"
```

Kein Output = ✅ Syntax OK  
Fehler = ❌ Syntax-Problem (meist Einrückung)

---

## Sicherheit

### accounts.yaml Berechtigungen
```bash
# Nur Owner kann lesen/schreiben
chmod 600 accounts.yaml
```

### Verschlüsseltes Backup
```bash
# Mit GPG verschlüsseln
gpg -c accounts.yaml
# Erstellt: accounts.yaml.gpg (verschlüsselt)
```

### Umgebungsvariablen (Alternative)
Falls du Passwörter nicht in Dateien speichern willst, kannst du sie auch als Umgebungsvariablen übergeben (erfordert Code-Anpassung).

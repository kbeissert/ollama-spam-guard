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
| **`USE_LISTS`** | **`true`/`false`** | **Aktiviert Blacklist/Whitelist-System** |
| **`LIST_UPDATE_INTERVAL`** | **Zahl** | **Update-Intervall für externe Listen (Stunden)** |
| **`WHITELIST_FILE`** | **Pfad** | **Pfad zur lokalen Whitelist** |
| **`BLACKLIST_FILE`** | **Pfad** | **Pfad zur lokalen Blacklist** |
| **`LISTS_CACHE_DIR`** | **Pfad** | **Cache-Verzeichnis für externe Listen** |
| **`FORCE_LIST_UPDATE`** | **`true`/`false`** | **Erzwingt Listen-Update beim Start** |

---

## Blacklist/Whitelist-System

### Übersicht

Das Blacklist/Whitelist-System bietet einen **Hard Filter** vor der LLM-Analyse:

**Priorität (von höchster zu niedrigster)**:
1. **Whitelist** → E-Mail wird IMMER als HAM (kein Spam) behandelt
2. **Blacklist** → E-Mail wird IMMER als SPAM behandelt  
3. **LLM-Analyse** → Nur wenn nicht in Listen gefunden

### Aktivierung

**.env**:
```bash
# Blacklist/Whitelist aktivieren
USE_LISTS=true

# Update-Intervall für externe Listen (Standard: 24 Stunden)
LIST_UPDATE_INTERVAL=24

# Lokale Listen (relativ zum Projekt-Root)
WHITELIST_FILE=data/lists/whitelist.txt
BLACKLIST_FILE=data/lists/blacklist.txt

# Cache-Verzeichnis für externe Listen
LISTS_CACHE_DIR=data/lists

# Erzwinge Update beim Start (ignoriert Cache)
FORCE_LIST_UPDATE=false
```

### Lokale Listen bearbeiten

#### Whitelist (`data/lists/whitelist.txt`)
```bash
# Vertrauenswürdige Absender (werden NIE als Spam markiert)

# Komplette E-Mail-Adressen
admin@example.com
newsletter@company.de

# Ganze Domains (alle E-Mails von dieser Domain)
trusted-company.com
partner-domain.de
```

#### Blacklist (`data/lists/blacklist.txt`)
```bash
# Bekannte Spam-Absender (werden IMMER als Spam markiert)

# Komplette E-Mail-Adressen
spam@badsite.com
phishing@scam.net

# Ganze Domains
known-spam-domain.xyz
scammer.ru
```

### Externe Blacklists

Automatisch geladen werden (wenn `USE_LISTS=true`):

| Quelle | Typ | Beschreibung | Update-Intervall |
|--------|-----|--------------|------------------|
| **Spamhaus DROP** | IP | Don't Route Or Peer List | Konfigurierbar |
| **Blocklist.de** | IP | Umfassende IP-Blacklist | Konfigurierbar |

**Cache-Speicherort**: `data/lists/` (z.B. `spamhaus_drop.txt`, `blocklist_de.txt`)

### Funktionsweise

```
┌─────────────────────────────────────────────────────┐
│              Eingehende E-Mail                      │
│         (Absender: unknown@example.com)             │
└─────────────────────────────────────────────────────┘
                        ↓
         ┌──────────────────────────────┐
         │   1. WHITELIST CHECK          │
         │   Ist Absender/Domain in      │
         │   whitelist.txt?              │
         └──────────────────────────────┘
                  ↓ JA                ↓ NEIN
         ✅ HAM (kein Spam)            ↓
         └─ FERTIG              ┌──────────────────────────────┐
                                │   2. BLACKLIST CHECK          │
                                │   Ist Absender/Domain in      │
                                │   blacklist.txt oder externe  │
                                │   Listen?                     │
                                └──────────────────────────────┘
                                     ↓ JA                ↓ NEIN
                            🚫 SPAM                      ↓
                            └─ FERTIG           ┌──────────────────────────────┐
                                                │   3. LLM-ANALYSE              │
                                                │   qwen2.5:14b-instruct        │
                                                │   analysiert E-Mail           │
                                                └──────────────────────────────┘
                                                         ↓
                                                   ✅ HAM / 🚫 SPAM
```

### Listen verwalten

#### Listen manuell aktualisieren
```bash
# ListManager im Test-Modus starten
python src/list_manager.py
```

#### Listen erzwingen beim Start
```bash
# .env setzen
FORCE_LIST_UPDATE=true
```

#### Cache löschen (komplettes Neu-Download)
```bash
rm -rf data/lists/external/*.txt data/lists/external/metadata.json
```

### Statistiken anzeigen

```python
from src.list_manager import get_list_manager

manager = get_list_manager()
stats = manager.get_stats()

print(f"Whitelist: {stats['whitelist']['total']} Einträge")
print(f"Blacklist: {stats['blacklist']['total']} Einträge")
print(f"Cache: {stats['cache']['directory']}")
```

### Best Practices

#### ✅ DO
- Füge vertrauenswürdige Newsletter zur Whitelist hinzu
- Pflege die Blacklist mit wiederholten Spam-Absendern
- Nutze Domains statt einzelner E-Mails (flexibler)
- Prüfe regelmäßig die Listen auf Duplikate
- Aktiviere `FORCE_LIST_UPDATE=true` nach längerer Inaktivität

#### ❌ DON'T
- Niemals fremde Domains blind zur Whitelist hinzufügen
- Nicht zu viele Einträge in lokalen Listen (Performance)
- Cache nicht manuell editieren (wird überschrieben)
- Externe Listen nicht direkt bearbeiten

### Troubleshooting

#### Listen werden nicht geladen
```bash
# Prüfe Logs
tail -f ~/spam_filter.log | grep -i "list"

# Prüfe Konfiguration
python -c "from src.config import USE_LISTS, LISTS_CACHE_DIR; print(f'USE_LISTS={USE_LISTS}, CACHE={LISTS_CACHE_DIR}')"
```

#### Externe Listen Download fehlgeschlagen
- Cache wird verwendet (falls vorhanden)
- Fehler wird geloggt, Script läuft weiter
- Manueller Download möglich: `python src/list_manager.py`

#### E-Mail trotz Whitelist als Spam markiert
- Prüfe exakte Schreibweise (Groß-/Kleinschreibung wird ignoriert)
- Prüfe Domain-Extraktion: `@domain.com` muss als `domain.com` in Liste sein
- Prüfe Logs für `"Hard Filter"` Einträge

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

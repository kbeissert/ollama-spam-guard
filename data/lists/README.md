# Whitelist/Blacklist Verzeichnis-Struktur

## 📁 Verzeichnisstruktur

```
data/lists/
├── whitelist.txt               # DEINE Whitelist (persönlich, nicht in Git)
├── blacklist.txt               # DEINE Blacklist (persönlich, nicht in Git)
├── blacklist_sources.yaml      # DEINE Provider-Konfiguration (persönlich, nicht in Git)
├── whitelist.txt.example       # Template für Whitelist (in Git)
├── blacklist.txt.example       # Template für Blacklist (in Git)
├── blacklist_sources.yaml.example  # Template für Provider (in Git)
├── README.md                   # Diese Datei (in Git)
└── external/                   # Cache für externe Listen (nicht in Git)
    ├── spamhaus_drop.txt       # Automatisch geladen
    ├── blocklist_de.txt        # Automatisch geladen
    ├── metadata.json           # Update-Zeitstempel
    └── ...                     # Weitere aktivierte Listen
```

## 🎯 Trennung

### User-Listen (data/lists/)
**Deine persönlichen Listen bleiben hier:**
- ✅ Übersichtlich und leicht zu finden
- ✅ Getrennt vom automatischen Cache
- ✅ In Git ignoriert (`.gitignore`)
- ✅ Werden NIEMALS automatisch überschrieben

### Externe Listen (data/lists/external/)
**Automatisch verwalteter Cache:**
- 🌐 Externe Blacklists (Spamhaus, Blocklist.de, etc.)
- 🔄 Wird automatisch aktualisiert (alle 24h)
- 🗑️ Kann bedenkenlos gelöscht werden (wird neu erstellt)
- ❌ Komplett in Git ignoriert
- 📊 metadata.json für Update-Tracking

## ⚙️ Einrichtung

**Erste Schritte:**
```bash
# Kopiere die Beispieldateien in data/lists/
cp data/lists/whitelist.txt.example data/lists/whitelist.txt
cp data/lists/blacklist.txt.example data/lists/blacklist.txt
cp data/lists/blacklist_sources.yaml.example data/lists/blacklist_sources.yaml

# Bearbeite deine Listen
nano data/lists/whitelist.txt
nano data/lists/blacklist.txt

# Aktiviere/deaktiviere externe Blacklist-Provider
nano data/lists/blacklist_sources.yaml

# Das external/ Verzeichnis wird automatisch erstellt!
```

## 📝 Provider-Konfiguration (blacklist_sources.yaml)

**Externe Blacklist-Provider verwalten:**

```yaml
# Quelle aktivieren (enabled: true)
spamhaus_drop:
  url: "https://www.spamhaus.org/drop/drop.txt"
  type: "ip_cidr"
  description: "Spamhaus DROP List"
  enabled: true

# Quelle deaktivieren (enabled: false)
abuse_ch_urlhaus:
  url: "https://urlhaus.abuse.ch/downloads/text/"
  type: "domain"
  description: "Abuse.ch URLhaus"
  enabled: false

# Eigene Quelle hinzufügen
meine_liste:
  url: "https://example.com/spam-list.txt"
  type: "domain"
  description: "Meine Spam-Liste"
  enabled: true
```

**Vorteile:**
- ✅ Keine Python-Dateien bearbeiten
- ✅ Einfaches YAML-Format
- ✅ Quellen per `enabled: true/false` aktivieren
- ✅ Eigene Quellen einfach hinzufügen
- ✅ Syntax-Fehler fallen sofort auf

## 📁 Dateien

### Templates (in Git, nicht ändern!)
- **whitelist.txt.example**: Vorlage für Whitelist
- **blacklist.txt.example**: Vorlage für Blacklist

### User-spezifisch (NICHT in Git!)
- **whitelist.txt**: Deine vertrauenswürdigen E-Mails/Domains (werden NIE als Spam markiert)
- **blacklist.txt**: Deine Spam-Adressen/Domains (werden IMMER als Spam markiert)

### Automatisch generiert (NICHT in Git!)
- **spamhaus_drop.txt**: Externe Blacklist von Spamhaus (automatisch geladen)
- **blocklist_de.txt**: Externe Blacklist von Blocklist.de (automatisch geladen)
- **metadata.json**: Cache-Metadaten für externe Listen

## 📝 Format

Beide Dateien verwenden **einfaches Textformat (.txt)**:

**Warum .txt?**
- ✅ **Universell**: Auf allen Systemen lesbar (Windows, macOS, Linux)
- ✅ **Einfach**: Mit jedem Texteditor bearbeitbar (nano, vim, VS Code, Notepad++)
- ✅ **Kompatibel**: Standard für Listen-Dateien (hosts-Dateien, robots.txt, etc.)
- ✅ **Versionierbar**: Git-freundlich (Zeilen-basierte Diffs)
- ✅ **Performance**: Schnell zu parsen, keine komplexe Struktur nötig
- ✅ **Transparent**: Jeder kann sofort sehen, was drin steht

**Syntax:**
- Eine E-Mail-Adresse oder Domain pro Zeile
- Zeilen beginnend mit `#` sind Kommentare
- Leerzeilen werden ignoriert

## 💡 Beispiele

### E-Mail-Adresse (exakte Übereinstimmung)
```
admin@example.com
support@company.de
```

### Domain (alle E-Mails von dieser Domain)
```
trusted-company.com
known-spam-domain.xyz
```

## 🌐 Externe Blacklists

Zusätzlich zu den lokalen Listen werden automatisch externe Spam-Blacklists heruntergeladen:

- **Spamhaus DROP**: IP-basierte Blacklist
- **Blocklist.de**: Umfassende IP-Blacklist

Diese externen Listen werden im **`external/` Unterverzeichnis** gespeichert und regelmäßig aktualisiert (Standard: alle 24 Stunden).

## 📊 Cache-Verzeichnis (external/)

**Speicherort:** `data/lists/external/`

Externe Listen werden hier gecacht:
- Dateiname: `<quelle>.txt` (z.B. `spamhaus_drop.txt`)
- Metadaten: `metadata.json` (enthält Update-Zeitstempel)

**Automatische Verwaltung:**
- ✅ Wird beim ersten Start automatisch erstellt
- ✅ Wird bei Löschung automatisch neu angelegt
- ✅ Listen werden automatisch heruntergeladen
- ✅ Kein manueller Eingriff nötig

## ⏱️ Update-Intervall

Das Update-Intervall kann in der `.env` Datei konfiguriert werden:
```bash
LIST_UPDATE_INTERVAL=24  # Stunden
```

## 🔒 Sicherheit & Git

**Wichtig:**
- ✅ `whitelist.txt` und `blacklist.txt` sind in `.gitignore` → Bleiben privat
- ✅ Nur die `.example` Dateien werden in Git versioniert
- ✅ `external/` Verzeichnis komplett ignoriert → Keine Cache-Dateien in Git
- ✅ Deine persönlichen Listen bleiben lokal und privat
- ✅ README.md und .gitkeep sind die einzigen Git-Dateien hier

**Git-Status:**
```bash
# In Git (öffentlich):
data/lists/whitelist.txt.example
data/lists/blacklist.txt.example
data/lists/README.md
data/lists/external/.gitkeep

# NICHT in Git (privat):
data/lists/whitelist.txt
data/lists/blacklist.txt
data/lists/external/*  (alle Cache-Dateien)
```

## 🧹 Cache löschen/neu aufbauen

```bash
# Nur externe Listen Cache löschen (deine Listen bleiben!)
rm -rf data/lists/external/

# Beim nächsten Start wird alles neu heruntergeladen
make run

# Oder nur Metadaten löschen (erzwingt Update)
rm data/lists/external/metadata.json
```

**Keine Sorge:** Deine `whitelist.txt` und `blacklist.txt` bleiben immer erhalten!

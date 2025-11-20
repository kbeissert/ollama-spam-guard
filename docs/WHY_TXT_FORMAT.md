# Warum verwenden wir .txt für White-/Blacklists?

## Begründung für Textformat (.txt)

### ✅ Vorteile

1. **Universelle Kompatibilität**
   - Funktioniert auf allen Betriebssystemen (Windows, macOS, Linux)
   - Keine Abhängigkeiten von speziellen Bibliotheken
   - Mit jedem Texteditor bearbeitbar

2. **Einfachheit**
   - Klare, menschenlesbare Struktur
   - Keine komplexe Syntax wie JSON, YAML oder XML
   - Ein Eintrag pro Zeile = maximale Übersichtlichkeit

3. **Performance**
   - Sehr schnelles Parsing (einfaches Zeilen-basiertes Lesen)
   - Minimaler Speicher-Overhead
   - Effizientes Laden großer Listen (tausende Einträge)

4. **Git-Freundlichkeit**
   - Exzellente Diff-Darstellung (Zeile für Zeile)
   - Einfache Merge-Konflikte
   - Klare Historie von Änderungen

5. **Standard in der Industrie**
   - `hosts` Dateien (Linux/macOS/Windows)
   - `robots.txt` (Web)
   - Viele Spam-Listen im Internet verwenden .txt
   - Ad-Blocker Listen (z.B. Pi-hole)

6. **Sicherheit**
   - Kein Code-Execution möglich (im Gegensatz zu Python/Shell-Scripts)
   - Keine Injection-Risiken wie bei SQL oder Scripting-Formaten
   - Transparent: Jeder kann sofort sehen, was drin steht

### ❌ Warum NICHT andere Formate?

**JSON/YAML:**
- ❌ Overhead bei einfachen Listen (Struktur > Inhalt)
- ❌ Fehleranfälliger (Syntax-Fehler bei Kommas, Einrückung)
- ❌ Für Menschen schwerer zu bearbeiten bei langen Listen

**CSV:**
- ❌ Keine Kommentare möglich
- ❌ Verwirrt durch Sonderzeichen in E-Mails
- ❌ Overhead durch Spalten-Struktur (wir haben nur 1 Spalte)

**SQLite/Datenbank:**
- ❌ Benötigt Tools zum Bearbeiten
- ❌ Nicht einfach mit Git versionierbar
- ❌ Overhead für kleine bis mittlere Listen
- ❌ Komplexität ohne echten Mehrwert

**Excel/Spreadsheets:**
- ❌ Proprietäres Format
- ❌ Nicht Git-kompatibel
- ❌ Benötigt spezielle Software
- ❌ Binärformat statt Text

## 📋 Beispiel-Vergleich

### .txt (gewählt) ✅
```txt
# Kommentar
admin@example.com
company.com
```

**Vorteile:** 3 Zeilen, sofort verständlich, überall editierbar

### JSON ❌
```json
{
  "whitelist": [
    "admin@example.com",
    "company.com"
  ]
}
```

**Nachteile:** 6 Zeilen, Syntax-Overhead, keine Kommentare

### YAML ❌
```yaml
whitelist:
  - admin@example.com
  - company.com
```

**Nachteile:** Einrückung kritisch, mehr Zeilen, Parsing-Overhead

## 🎯 Fazit

Das .txt-Format ist für White-/Blacklists die **beste Wahl**, weil:
- Maximale Einfachheit und Klarheit
- Universell kompatibel und editierbar
- Industriestandard für Listen
- Optimal für Git
- Beste Performance

Für komplexere Konfigurationen (wie `accounts.yaml`) verwenden wir YAML, aber für einfache Listen ist Plain Text unschlagbar.

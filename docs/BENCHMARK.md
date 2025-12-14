# 📊 Benchmark-Dokumentation

Der **Ollama Spam Guard** enthält ein integriertes Benchmark-Tool. Damit kannst du testen, wie gut verschiedene LLM-Modelle (z.B. `ministral`, `qwen`, `mistral`) Spam erkennen, wie schnell sie sind und welches für deinen Anwendungsfall am besten geeignet ist.

---

## 🚀 Schnellstart

Stelle sicher, dass Ollama läuft (`ollama serve`).

### Interaktiver Modus (Empfohlen)
Wähle das Modell bequem aus einer Liste deiner installierten Modelle aus:
```bash
make benchmark
```

### Quick-Test
Testet nur 5 E-Mails (sehr schnell), um zu prüfen, ob alles funktioniert:
```bash
make benchmark-quick
```

---

## 📂 Ergebnisse

Alle Ergebnisse werden im Ordner `benchmark/` im Hauptverzeichnis gespeichert.

| Datei | Beschreibung |
|-------|--------------|
| **`model_scores.csv`** | 🏆 **Leaderboard**. Rangliste aller getesteten Modelle. Enthält Score, Genauigkeit, Geschwindigkeit, Token-Effizienz und Badges. |
| **`recommendation.txt`** | 💡 **Empfehlung**. Eine automatisch generierte Zusammenfassung mit dem Gewinner-Modell und wichtigen Insights. |
| **`detailed_results.csv`** | 📝 **Details**. Protokoll jeder einzelnen Entscheidung. Hilfreich, um "False Positives" (fälschlich als Spam erkannte Mails) zu analysieren. |
| **`test_emails.csv`** | 📧 **Test-Daten**. Die 30 E-Mails (inkl. schwieriger Fälle), die für den Test verwendet werden. |

---

## 🧠 Intelligente Features

### Automatische Reasoning-Erkennung
Das Tool erkennt automatisch Modelle mit Reasoning-Fähigkeiten (z.B. `qwen3`) und testet diese in zwei Modi:
*   **Thinking: ON**: Mit aktiviertem Chain-of-Thought (Reasoning).
*   **Thinking: OFF**: Im Standard-Modus.
*   **Erkenntnis**: Unsere Tests zeigen oft, dass Reasoning für Spam-Erkennung kontraproduktiv ist (langsamer und teils ungenauer).

### Bewertungssystem (Badges)
Das Tool vergibt automatisch Auszeichnungen:
*   🏆 **Allround**: Bester gewichteter Gesamtscore (90% Genauigkeit / 10% Speed).
*   🎯 **Präzision**: Höchste Erkennungsrate.
*   ⚡ **Speed**: Schnellstes Modell mit akzeptabler Genauigkeit (>80%).

### Optimierungen
Für Modelle wie **Ministral** wendet der Benchmark automatisch Optimierungen an (z.B. spezifische System-Prompts), um den Token-Verbrauch massiv zu senken und die Präzision bei unbekannten Absendern zu sichern.

---

## 💡 Strategie zur Modellwahl

### Warum kleinere Modelle oft gewinnen

1.  **Vermeidung von "Overthinking"**: Spam-Erkennung ist eine vergleichsweise simple Klassifikationsaufgabe. Riesige Modelle neigen dazu, einfache Anweisungen zu "zerdenken".
2.  **Geschwindigkeit ist kritisch**: Wenn dein Postfach 100+ E-Mails am Tag empfängt, macht es einen riesigen Unterschied, ob eine Analyse 0,5 Sekunden oder 2 Sekunden dauert.
3.  **Ressourcen-Effizienz**: Ein 8B-Modell benötigt ca. 5-6 GB RAM, während ein 14B-Modell oft 9 GB+ belegt.

### Aktuelle Empfehlung (Dez 2025)

**Ministral 3 14B** hat sich als Benchmark-Sieger etabliert:
*   Exzellente Präzision (auch bei schwierigen Fällen).
*   Hohe Effizienz dank optimierter Prompts.
*   Gute Geschwindigkeit.

---

## 🧮 Score-Berechnung

Der "Final Score" (0-100) setzt sich aus zwei Faktoren zusammen:

1.  **Genauigkeit (90%)**: Wie viele E-Mails wurden korrekt klassifiziert? (Dominanter Faktor)
2.  **Geschwindigkeit (10%)**: Tokens per Second (TPS).

---

## 🛠️ Experten-Modus (CLI)

Du kannst das Benchmark-Skript auch direkt mit Parametern aufrufen. Nutze dafür das Python aus dem virtuellen Environment:

```bash
# Bestimmtes Modell testen
.venv/bin/python scripts/benchmark/spam_benchmark.py --model ministral-3:14b

# Eigene Test-Daten verwenden
.venv/bin/python scripts/benchmark/spam_benchmark.py --input meine_emails.csv

# Output-Ordner ändern
.venv/bin/python scripts/benchmark/spam_benchmark.py --output mein_benchmark_ordner/
```

---

## ⚠️ Voraussetzungen

1.  **Ollama**: Muss lokal installiert sein und laufen.
2.  **Modelle**: Du musst die Modelle, die du testen willst, vorher heruntergeladen haben (`ollama pull <modellname>`).
3.  **Python-Environment**: Muss installiert sein (`make install`).

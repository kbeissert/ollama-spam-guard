# 📊 Benchmark Ergebnisse

In diesem Ordner werden die Ergebnisse deiner Spam-Detection Benchmarks gespeichert.

## ⚠️ Voraussetzungen

Damit der Benchmark funktioniert, benötigst du eine **lokale Installation von Ollama**.

1.  **Ollama installieren:** [ollama.com](https://ollama.com)
2.  **Ollama starten:** Stelle sicher, dass der Ollama-Server läuft (meistens im Hintergrund oder via `ollama serve`).
3.  **Modelle laden:** Du musst mindestens ein Modell heruntergeladen haben, z.B.:
    ```bash
    ollama pull qwen2.5:14b-instruct
    ```

## Dateien

*   **`model_scores.csv`**: 🏆 **Leaderboard**. Eine Rangliste aller getesteten Modelle, sortiert nach ihrem Score (Genauigkeit + Geschwindigkeit + Effizienz).
*   **`recommendation.txt`**: 💡 **Empfehlung**. Eine textuelle Zusammenfassung mit dem Gewinner-Modell und Insights.
*   **`detailed_results.csv`**: 📝 **Details**. Jede einzelne Entscheidung des Modells für jede Test-E-Mail.
*   **`test_emails.csv`**: 📧 **Test-Daten**. Die E-Mails, die für den Test verwendet wurden. Du kannst diese Datei bearbeiten, um eigene Testfälle hinzuzufügen.
*   **`*.log`**: Protokolle der einzelnen Durchläufe.

## Wie starte ich einen Benchmark?

Du musst keine Skripte direkt ausführen. Nutze einfach diese Befehle im Hauptverzeichnis:

### 1. Interaktiver Modus (Empfohlen)
Wähle das Modell bequem aus einer Liste aus:
```bash
make benchmark
```

### 2. Quick-Test
Testet nur 5 E-Mails mit einem Standard-Modell (schnell):
```bash
make benchmark-quick
```

### 3. Experten-Modus (CLI)
Wenn du spezifische Parameter brauchst, kannst du das Skript auch direkt aufrufen (nutze das virtuelle Environment):
```bash
.venv/bin/python scripts/benchmark/spam_benchmark.py --model qwen2.5:14b-instruct
```

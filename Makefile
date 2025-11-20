# ============================================
# Ollama Spam Guard - Makefile
# ============================================
# Einfache Kurzbefehle zum Starten der Scripts
#
# Verwendung:
#   make test      - Verbindungstest
#   make run       - Spam-Filter starten
#   make folders   - Ordnerstruktur anzeigen
#   make help      - Hilfe anzeigen

.PHONY: help test run folders install clean

# Standard-Target (wird bei 'make' ohne Parameter aufgerufen)
help:
	@echo "╔════════════════════════════════════════════╗"
	@echo "║    Ollama Spam Guard - Verfügbare Befehle ║"
	@echo "╚════════════════════════════════════════════╝"
	@echo ""
	@echo "  make test       - Verbindungstest (Ollama, LLM, IMAP)"
	@echo "  make run        - Spam-Filter starten"
	@echo "  make unspam     - Whitelist-E-Mails aus Spam wiederherstellen"
	@echo "  make folders    - IMAP-Ordnerstruktur anzeigen"
	@echo ""
	@echo "  make install    - Python-Dependencies installieren"
	@echo "  make clean      - Cache-Dateien löschen"
	@echo ""
	@echo "  make help       - Diese Hilfe anzeigen"
	@echo ""

# Verbindungstest ausführen
test:
	@echo "🔍 Starte Verbindungstest..."
	@python test_connection.py

# Spam-Filter starten
run:
	@echo "🛡️  Starte Spam-Filter..."
	@python src/spam_filter.py

# E-Mails von Whitelist-Absendern aus Spam-Ordner wiederherstellen
unspam:
	@echo "♻️  Starte Unspam..."
	@python unspam.py

# E-Mails wiederherstellen (automatisch, ohne Nachfrage)
unspam-auto:
	@echo "♻️  Starte Unspam (automatisch)..."
	@python unspam.py --auto

# E-Mails nur anzeigen (Dry-Run)
unspam-dry:
	@echo "♻️  Starte Unspam (Dry-Run)..."
	@python unspam.py --dry-run

# IMAP-Ordnerstruktur anzeigen
folders:
	@echo "📁 Zeige IMAP-Ordnerstruktur..."
	@python list_folders.py

# Alle Ordner anzeigen (inkl. System-Ordner)
folders-all:
	@echo "📁 Zeige ALLE IMAP-Ordner..."
	@python list_folders.py --all

# Dependencies installieren
install:
	@echo "📦 Installiere Python-Dependencies..."
	@pip install -r requirements.txt
	@echo "✅ Installation abgeschlossen!"

# Cache-Dateien löschen
clean:
	@echo "🧹 Lösche Cache-Dateien..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@echo "✅ Cache gelöscht!"

# Projekt-Status anzeigen
status:
	@echo "📊 Projekt-Status:"
	@echo ""
	@echo "Python-Version:"
	@python --version
	@echo ""
	@echo "Installierte Pakete:"
	@pip list | grep -E "python-dotenv|requests|tqdm|pyyaml" || echo "  Keine gefunden - führe 'make install' aus"
	@echo ""
	@echo "Git-Status:"
	@git status -s || echo "  Kein Git-Repository"
	@echo ""
	@echo "Konfiguration:"
	@test -f .env && echo "  ✅ .env vorhanden" || echo "  ❌ .env fehlt"
	@test -f accounts.yaml && echo "  ✅ accounts.yaml vorhanden" || echo "  ❌ accounts.yaml fehlt"

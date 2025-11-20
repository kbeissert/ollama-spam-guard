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

.PHONY: help test run folders install clean unspam unspam-auto unspam-dry \
        whitelist-show whitelist-add whitelist-remove \
        blacklist-show blacklist-add blacklist-remove

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
	@echo "  Listen verwalten:"
	@echo "  make whitelist-show              - Whitelist anzeigen"
	@echo "  make whitelist-add ENTRY=<mail>  - Zur Whitelist hinzufügen"
	@echo "  make blacklist-show              - Blacklist anzeigen"
	@echo "  make blacklist-add ENTRY=<mail>  - Zur Blacklist hinzufügen"
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

# ============================================
# Listen-Verwaltung
# ============================================

# Whitelist anzeigen
whitelist-show:
	@python manage_lists.py whitelist show

# Zur Whitelist hinzufügen
# Usage: make whitelist-add ENTRY=email@example.com
whitelist-add:
ifndef ENTRY
	@echo "❌ Fehler: ENTRY nicht angegeben"
	@echo "Usage: make whitelist-add ENTRY=email@example.com"
	@exit 1
endif
	@python manage_lists.py whitelist add "$(ENTRY)"

# Von Whitelist entfernen
# Usage: make whitelist-remove ENTRY=email@example.com
whitelist-remove:
ifndef ENTRY
	@echo "❌ Fehler: ENTRY nicht angegeben"
	@echo "Usage: make whitelist-remove ENTRY=email@example.com"
	@exit 1
endif
	@python manage_lists.py whitelist remove "$(ENTRY)"

# Blacklist anzeigen
blacklist-show:
	@python manage_lists.py blacklist show

# Zur Blacklist hinzufügen
# Usage: make blacklist-add ENTRY=spam@example.com
blacklist-add:
ifndef ENTRY
	@echo "❌ Fehler: ENTRY nicht angegeben"
	@echo "Usage: make blacklist-add ENTRY=spam@example.com"
	@exit 1
endif
	@python manage_lists.py blacklist add "$(ENTRY)"

# Von Blacklist entfernen
# Usage: make blacklist-remove ENTRY=spam@example.com
blacklist-remove:
ifndef ENTRY
	@echo "❌ Fehler: ENTRY nicht angegeben"
	@echo "Usage: make blacklist-remove ENTRY=spam@example.com"
	@exit 1
endif
	@python manage_lists.py blacklist remove "$(ENTRY)"

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

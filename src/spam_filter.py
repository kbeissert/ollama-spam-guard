#!/usr/bin/env python3
"""
Ollama Spam Guard - IMAP Spam Filter mit lokalem LLM (qwen2.5:14b-instruct via Ollama)
Automatische E-Mail-Filterung für All-Inkl KAS-Server

Autor: Generiert mit Continue + Perplexity
Datum: 2025-11-19
"""

import imaplib
import email
import email.header
import email.utils
import requests
from dotenv import load_dotenv
from tqdm import tqdm
import os
import logging
from typing import Tuple, Dict
from datetime import datetime, timedelta

# ============================================
# Konfiguration laden
# ============================================

load_dotenv()

from config import (
    EMAIL_ACCOUNTS, OLLAMA_URL, SPAM_MODEL, FILTER_MODE, LIMIT, DAYS_BACK, LOG_PATH
)

# Logging-Setup
log_path = LOG_PATH
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============================================
# IMAP-Funktionen
# ============================================

def connect_imap(account: Dict[str, str]) -> imaplib.IMAP4_SSL:
    """
    Verbindet zum IMAP-Server und öffnet INBOX.
    
    Args:
        account: Account-Konfiguration (user, password, server, port)
    
    Returns:
        IMAP4_SSL: Verbundenes Mail-Objekt
        
    Raises:
        imaplib.IMAP4.error: Bei Login- oder Verbindungsfehlern
    """
    try:
        print(f"🔌 Verbinde zu {account['server']}:{account['port']}...")
        mail = imaplib.IMAP4_SSL(account['server'], account['port'])
        
        print(f"🔐 Login als {account['user']}...")
        mail.login(account['user'], account['password'])
        
        print("📬 Öffne INBOX...")
        mail.select('INBOX')
        
        logging.info(f"Erfolgreich verbunden mit {account['server']} ({account['user']})")
        return mail
        
    except imaplib.IMAP4.error as e:
        print(f"\n❌ IMAP-Fehler: {e}")
        print("\n💡 Mögliche Ursachen:")
        print("   - Falsches Passwort")
        print("   - IMAP nicht aktiviert")
        print(f"   - Falscher Server ({account['server']})")
        logging.error(f"IMAP-Fehler für {account['user']}: {e}", exc_info=True)
        raise
    except Exception as e:
        print(f"\n❌ Verbindungsfehler: {e}")
        logging.error(f"Verbindungsfehler zu {account['server']}:{account['port']}", exc_info=True)
        raise

# ============================================
# Spam-Detection mit LLM
# ============================================

def detect_spam(sender: str, subject: str, body: str) -> Tuple[bool, str]:
    """
    Analysiert E-Mail mit qwen2.5:14b-instruct LLM via Ollama.
    
    Args:
        sender: Absender-E-Mail
        subject: E-Mail-Betreff
        body: E-Mail-Body (Preview, max 500 Zeichen)
        
    Returns:
        Tuple[bool, str]: (is_spam, reason)
    """
    prompt = f"""Analysiere diese E-Mail auf Spam-Indikatoren.

Von: {sender}
Betreff: {subject}
Inhalt: {body[:500]}

Antworte nur mit "SPAM" oder "HAM".
"""
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                'model': SPAM_MODEL,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,  # Deterministisch
                    'num_predict': 50    # Kurze Antwort
                }
            },
            timeout=30
        )
        response.raise_for_status()
        
        # Parse Ollama JSON-Response
        result_json = response.json()
        result_text = result_json["response"].strip().upper()
        
        # Bestimme Spam-Status
        is_spam = "SPAM" in result_text[:20]  # Erste 20 Zeichen prüfen
        
        return is_spam, result_text
        
    except requests.Timeout:
        logging.warning("LLM-Request timeout, behandle als HAM")
        return False, "LLM Timeout (als HAM behandelt)"
    except requests.ConnectionError:
        logging.error("Ollama nicht erreichbar - ist 'ollama serve' aktiv?")
        print("\n⚠️  Ollama nicht erreichbar!")
        print("   Starte in anderem Terminal: ollama serve")
        return False, "Ollama offline (als HAM behandelt)"
    except Exception as e:
        logging.error(f"LLM-Fehler: {e}", exc_info=True)
        return False, f"Fehler: {str(e)}"

# ============================================
# E-Mail-Verarbeitung
# ============================================

def decode_header_safe(header_value: str) -> str:
    """
    Dekodiert E-Mail-Header sicher (mit Fallback).
    
    Args:
        header_value: Roh-Header-Wert
        
    Returns:
        str: Dekodierter String
    """
    if not header_value:
        return "Kein Wert"
    
    try:
        decoded_parts = email.header.decode_header(header_value)
        decoded_str = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_str += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_str += str(part)
        
        return decoded_str
    except Exception as e:
        logging.warning(f"Header-Dekodierung fehlgeschlagen: {e}")
        return str(header_value)

def extract_body_preview(msg: email.message.Message) -> str:
    """
    Extrahiert Body-Vorschau aus E-Mail (max 500 Zeichen).
    
    Args:
        msg: E-Mail-Message-Objekt
        
    Returns:
        str: Body-Preview (text/plain bevorzugt)
    """
    body = ""
    
    try:
        if msg.is_multipart():
            # Durchsuche Teile nach text/plain
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')[:500]
                        break
        else:
            # Einfache Nachricht
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')[:500]
    except Exception as e:
        logging.warning(f"Body-Extraktion fehlgeschlagen: {e}")
        body = "[Body konnte nicht dekodiert werden]"
    
    return body if body else "[Leerer Body]"

def process_inbox(account: Dict[str, str]) -> Dict[str, int]:
    """
    Hauptfunktion: Verarbeitet INBOX und filtert Spam.
    
    Args:
        account: Account-Konfiguration
    
    Returns:
        Dict mit Statistiken: {'spam': int, 'ham': int}
    """
    try:
        mail = connect_imap(account)
    except Exception as e:
        logging.error(f"Verbindung zu {account['user']} fehlgeschlagen: {e}")
        print(f"\n⚠️  Überspringe Account {account['user']} (Verbindung fehlgeschlagen)\n")
        return {'spam': 0, 'ham': 0, 'error': True}
    
    stats = {'spam': 0, 'ham': 0, 'error': False}
    
    try:
        # Suche E-Mails basierend auf Filter-Modus
        if FILTER_MODE == 'days':
            # Berechne Datum für IMAP-Suche
            since_date = datetime.now() - timedelta(days=DAYS_BACK)
            date_str = since_date.strftime('%d-%b-%Y')  # Format: "19-Nov-2025"
            
            print(f"\n🔍 Suche E-Mails seit {date_str} (letzte {DAYS_BACK} Tage)...")
            status, data = mail.search(None, f'(SINCE {date_str})')
            
            if status != 'OK':
                logging.error("IMAP SEARCH fehlgeschlagen")
                print("❌ E-Mail-Suche fehlgeschlagen")
                return stats
            
            email_ids = data[0].split()
            
        else:  # FILTER_MODE == 'count'
            print(f"\n🔍 Suche letzte {LIMIT} E-Mails...")
            status, data = mail.search(None, 'ALL')
            
            if status != 'OK':
                logging.error("IMAP SEARCH fehlgeschlagen")
                print("❌ E-Mail-Suche fehlgeschlagen")
                return stats
            
            email_ids = data[0].split()
            
            # Limit anwenden (neueste E-Mails = höchste IDs)
            email_ids = email_ids[-LIMIT:] if len(email_ids) > LIMIT else email_ids
        
        if not email_ids:
            if FILTER_MODE == 'days':
                print(f"✅ Keine E-Mails in den letzten {DAYS_BACK} Tagen gefunden!")
            else:
                print("✅ Keine E-Mails gefunden!")
            return stats
        
        print(f"📧 Analysiere {len(email_ids)} E-Mail(s)...\n")
        
        # Verarbeite E-Mails mit Progress-Bar
        for email_id in tqdm(email_ids, desc="Verarbeite E-Mails", unit="mail"):
            try:
                # Hole E-Mail
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    logging.error(f"Fetch fehlgeschlagen für ID {email_id}")
                    continue
                
                # Parse E-Mail
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Extrahiere Metadaten
                sender = email.utils.parseaddr(msg.get('From', ''))[1] or "Unbekannt"
                subject = decode_header_safe(msg.get('Subject', 'Kein Betreff'))
                body_preview = extract_body_preview(msg)
                
                # Ausgabe
                print(f"\n📧 Von: {sender}")
                print(f"   Betreff: {subject[:60]}{'...' if len(subject) > 60 else ''}")
                
                # LLM-Analyse
                is_spam, reason = detect_spam(sender, subject, body_preview)
                
                if is_spam:
                    print(f"   ❌ SPAM: {reason[:100]}")
                    
                    # Verschiebe zu Spam-Ordner
                    try:
                        mail.copy(email_id, account['spam_folder'])
                        mail.store(email_id, '+FLAGS', '\\Deleted')
                        logging.info(f"SPAM verschoben: {subject} von {sender} ({account['user']})")
                    except Exception as e:
                        logging.error(f"Spam-Verschiebung fehlgeschlagen: {e}")
                        print(f"   ⚠️  Verschiebung fehlgeschlagen: {e}")
                    
                    stats['spam'] += 1
                else:
                    print(f"   ✅ HAM: {reason[:100]}")
                    
                    # Markiere als gelesen
                    mail.store(email_id, '+FLAGS', '\\Seen')
                    logging.info(f"HAM behalten: {subject} ({account['user']})")
                    
                    stats['ham'] += 1
                    
            except Exception as e:
                logging.error(f"Fehler bei E-Mail ID {email_id}: {e}", exc_info=True)
                print(f"\n⚠️  Fehler bei dieser E-Mail: {e}")
                continue
        
        return stats
        
    finally:
        # Cleanup
        try:
            print("\n🧹 Räume auf...")
            mail.expunge()  # Lösche markierte E-Mails
            mail.logout()
            print("✅ IMAP-Verbindung geschlossen")
        except Exception as e:
            logging.error(f"Logout fehlgeschlagen: {e}", exc_info=True)

# ============================================
# Main Entry Point
# ============================================

def main():
    """Hauptfunktion des Spam-Filters mit Multi-Account Support."""
    
    print("\n" + "="*60)
    print("🤖 LLM-basierter IMAP Spam-Filter (Multi-Account)")
    print("="*60)
    print(f"   Modell: {SPAM_MODEL}")
    print(f"   Accounts: {len(EMAIL_ACCOUNTS)}")
    
    if FILTER_MODE == 'days':
        print(f"   Filter: Letzte {DAYS_BACK} Tage")
    else:
        print(f"   Filter: Letzte {LIMIT} E-Mails pro Account")
    
    print(f"   Log: {log_path}")
    print("="*60 + "\n")
    
    try:
        # Prüfe Ollama-Verfügbarkeit
        print("🔍 Prüfe Ollama-Verfügbarkeit...")
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                print("✅ Ollama läuft\n")
            else:
                print("⚠️  Ollama antwortet nicht wie erwartet\n")
        except requests.ConnectionError:
            print("❌ Ollama nicht erreichbar!")
            print("   Starte in anderem Terminal: ollama serve")
            print("   (Oder als Dienst: brew services start ollama)")
            print("   Details: docs/SETUP.md → Abschnitt 'Ollama einrichten'")
            print("\n⏹️  Script wird abgebrochen - keine E-Mails verarbeitet.\n")
            logging.error("Ollama nicht erreichbar - Script abgebrochen")
            return
        
        # Gesamtstatistik
        total_stats = {'spam': 0, 'ham': 0, 'accounts_processed': 0, 'accounts_failed': 0}
        
        # Verarbeite alle Accounts
        for idx, account in enumerate(EMAIL_ACCOUNTS, 1):
            print("\n" + "─"*60)
            print(f"📬 Account {idx}/{len(EMAIL_ACCOUNTS)}: {account['user']}")
            print(f"   Server: {account['server']}")
            print("─"*60)
            
            # Verarbeite Account
            stats = process_inbox(account)
            
            if stats.get('error', False):
                total_stats['accounts_failed'] += 1
                continue
            
            # Aktualisiere Gesamtstatistik
            total_stats['spam'] += stats['spam']
            total_stats['ham'] += stats['ham']
            total_stats['accounts_processed'] += 1
            
            # Account-Statistik
            account_total = stats['spam'] + stats['ham']
            if account_total > 0:
                spam_rate = (stats['spam'] / account_total) * 100
                print(f"\n   📊 {account['user']}: {account_total} E-Mails ({stats['spam']} SPAM, {stats['ham']} HAM, {spam_rate:.1f}% Spam-Rate)")
        
        # Finale Gesamtstatistik
        total = total_stats['spam'] + total_stats['ham']
        print("\n" + "="*60)
        print("📊 Gesamtzusammenfassung")
        print("="*60)
        print(f"   Accounts verarbeitet: {total_stats['accounts_processed']}/{len(EMAIL_ACCOUNTS)}")
        
        if total_stats['accounts_failed'] > 0:
            print(f"   ⚠️  Accounts fehlgeschlagen: {total_stats['accounts_failed']}")
        
        print(f"   Gesamt analysiert: {total} E-Mails")
        print(f"   ❌ Als SPAM erkannt: {total_stats['spam']}")
        print(f"   ✅ Als HAM erkannt: {total_stats['ham']}")
        
        if total > 0:
            spam_rate = (total_stats['spam'] / total) * 100
            print(f"   📈 Gesamt-Spam-Rate: {spam_rate:.1f}%")
        
        print(f"\n   📄 Details: {log_path}")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Abbruch durch Benutzer")
        logging.info("Manueller Abbruch durch Benutzer")
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        logging.error(f"Unerwarteter Fehler: {e}", exc_info=True)
        print(f"\n💡 Details in: {log_path}")

if __name__ == "__main__":
    main()

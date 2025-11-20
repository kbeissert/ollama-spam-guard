#!/usr/bin/env python3
"""
Unspam - Stellt fälschlich als Spam markierte E-Mails wieder her

Durchsucht Spam-Ordner nach E-Mails von Absendern auf der Whitelist
und verschiebt diese zurück in den Posteingang.

Usage:
    python unspam.py                    # Interaktiv: zeigt Vorschau
    python unspam.py --auto             # Automatisch: ohne Nachfrage
    python unspam.py --dry-run          # Nur anzeigen, nichts verschieben

Autor: Ollama Spam Guard
Datum: 2025-11-20
"""

import os
import sys
import imaplib
import email
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from dotenv import load_dotenv

# Füge src/ zum Python-Path hinzu
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import EMAIL_ACCOUNTS, LOG_PATH
from list_manager import get_list_manager
from spam_filter import decode_header_safe

# Logging
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def connect_imap(account: Dict[str, str]) -> imaplib.IMAP4_SSL:
    """
    Verbindet zum IMAP-Server.
    
    Args:
        account: Account-Konfiguration
        
    Returns:
        IMAP4_SSL: Verbundenes Mail-Objekt
    """
    mail = imaplib.IMAP4_SSL(account['server'], account['port'])
    mail.login(account['user'], account['password'])
    return mail

def find_whitelisted_spam(account: Dict[str, str], dry_run: bool = False) -> List[Dict]:
    """
    Durchsucht Spam-Ordner nach E-Mails von Whitelist-Absendern.
    
    Args:
        account: Account-Konfiguration
        dry_run: Nur prüfen, nichts verschieben
        
    Returns:
        List[Dict]: Gefundene E-Mails mit Metadaten
    """
    found_emails = []
    
    try:
        print(f"\n🔌 Verbinde zu {account['server']}...")
        mail = connect_imap(account)
        
        # Wähle Spam-Ordner
        print(f"📁 Öffne Spam-Ordner '{account['spam_folder']}'...")
        status, _ = mail.select(account['spam_folder'])
        
        if status != 'OK':
            print(f"⚠️  Spam-Ordner '{account['spam_folder']}' nicht gefunden!")
            logging.warning(f"Spam-Ordner nicht gefunden: {account['spam_folder']} ({account['user']})")
            return found_emails
        
        # Suche alle E-Mails im Spam-Ordner
        print("🔍 Durchsuche Spam-Ordner...")
        status, data = mail.search(None, 'ALL')
        
        if status != 'OK':
            print("❌ Suche fehlgeschlagen")
            return found_emails
        
        email_ids = data[0].split()
        
        if not email_ids:
            print("✅ Spam-Ordner ist leer")
            return found_emails
        
        print(f"📧 Prüfe {len(email_ids)} E-Mail(s) gegen Whitelist...\n")
        
        # Lade ListManager für Whitelist-Check
        list_manager = get_list_manager()
        
        # Prüfe jede E-Mail
        for email_id in email_ids:
            try:
                # Hole E-Mail
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue
                
                # Parse E-Mail
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Extrahiere Absender
                sender = email.utils.parseaddr(msg.get('From', ''))[1] or "Unbekannt"
                subject = decode_header_safe(msg.get('Subject', 'Kein Betreff'))
                date = msg.get('Date', 'Unbekanntes Datum')
                
                # Prüfe gegen Whitelist
                is_spam, reason = list_manager.check_email(sender)
                
                # is_spam = False bedeutet: auf Whitelist!
                if is_spam is False:
                    print(f"✅ Gefunden: {sender}")
                    print(f"   Betreff: {subject[:60]}{'...' if len(subject) > 60 else ''}")
                    print(f"   Grund: {reason}")
                    
                    found_emails.append({
                        'id': email_id,
                        'sender': sender,
                        'subject': subject,
                        'date': date,
                        'reason': reason
                    })
                
            except Exception as e:
                logging.error(f"Fehler beim Prüfen von E-Mail ID {email_id}: {e}")
                continue
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        logging.error(f"Fehler bei find_whitelisted_spam ({account['user']}): {e}", exc_info=True)
    
    return found_emails

def restore_emails(account: Dict[str, str], emails: List[Dict]) -> int:
    """
    Verschiebt E-Mails zurück in den Posteingang.
    
    Args:
        account: Account-Konfiguration
        emails: Liste von E-Mails zum Wiederherstellen
        
    Returns:
        int: Anzahl wiederhergestellter E-Mails
    """
    if not emails:
        return 0
    
    restored_count = 0
    
    try:
        print(f"\n🔄 Stelle {len(emails)} E-Mail(s) wieder her...\n")
        mail = connect_imap(account)
        
        # Wähle Spam-Ordner
        mail.select(account['spam_folder'])
        
        for email_data in emails:
            try:
                email_id = email_data['id']
                
                # Kopiere zurück in INBOX
                status, _ = mail.copy(email_id, 'INBOX')
                
                if status == 'OK':
                    # Lösche aus Spam-Ordner
                    mail.store(email_id, '+FLAGS', '\\Deleted')
                    
                    print(f"✅ Wiederhergestellt: {email_data['sender']}")
                    print(f"   Betreff: {email_data['subject'][:60]}{'...' if len(email_data['subject']) > 60 else ''}")
                    
                    logging.info(f"E-Mail wiederhergestellt: {email_data['subject']} von {email_data['sender']} ({account['user']})")
                    restored_count += 1
                else:
                    print(f"⚠️  Fehler bei: {email_data['sender']}")
                    
            except Exception as e:
                print(f"❌ Fehler bei {email_data['sender']}: {e}")
                logging.error(f"Fehler beim Wiederherstellen: {e}")
        
        # Cleanup
        mail.expunge()
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        logging.error(f"Fehler bei restore_emails ({account['user']}): {e}", exc_info=True)
    
    return restored_count

def main():
    """Hauptfunktion des Unspam-Tools."""
    
    parser = argparse.ArgumentParser(
        description='Stellt fälschlich als Spam markierte E-Mails wieder her'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Automatisch wiederherstellen ohne Nachfrage'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Nur anzeigen, nichts verschieben'
    )
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("♻️  Unspam - E-Mail Wiederherstellung")
    print("="*60)
    print(f"   Accounts: {len(EMAIL_ACCOUNTS)}")
    
    if args.dry_run:
        print("   Modus: DRY RUN (keine Änderungen)")
    elif args.auto:
        print("   Modus: AUTOMATISCH")
    else:
        print("   Modus: INTERAKTIV")
    
    print("="*60)
    
    total_found = 0
    total_restored = 0
    
    for idx, account in enumerate(EMAIL_ACCOUNTS, 1):
        print(f"\n{'─'*60}")
        print(f"📬 Account {idx}/{len(EMAIL_ACCOUNTS)}: {account['name']}")
        print(f"   Server: {account['server']}")
        print(f"   Spam-Ordner: {account['spam_folder']}")
        print("─"*60)
        
        # Suche E-Mails auf Whitelist
        found = find_whitelisted_spam(account, dry_run=args.dry_run)
        
        if not found:
            print("✅ Keine E-Mails von Whitelist-Absendern im Spam-Ordner\n")
            continue
        
        total_found += len(found)
        
        print(f"\n📊 {len(found)} E-Mail(s) von Whitelist-Absendern gefunden")
        
        # Dry-Run: Nur anzeigen
        if args.dry_run:
            print("ℹ️  DRY RUN - Keine Änderungen vorgenommen\n")
            continue
        
        # Interaktiv: Nachfragen
        if not args.auto:
            print("\n❓ Diese E-Mails in den Posteingang verschieben?")
            response = input("   [J]a / [N]ein / [A]lle Accounts: ").strip().lower()
            
            if response in ['n', 'no', 'nein']:
                print("⏭️  Übersprungen\n")
                continue
            elif response in ['a', 'alle', 'all']:
                args.auto = True  # Rest automatisch
        
        # Wiederherstellen
        restored = restore_emails(account, found)
        total_restored += restored
        
        print(f"\n✅ {restored} von {len(found)} E-Mail(s) wiederhergestellt")
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("📊 ZUSAMMENFASSUNG")
    print("="*60)
    print(f"   Accounts geprüft: {len(EMAIL_ACCOUNTS)}")
    print(f"   E-Mails gefunden: {total_found}")
    
    if args.dry_run:
        print(f"   Wiederhergestellt: 0 (DRY RUN)")
    else:
        print(f"   Wiederhergestellt: {total_restored}")
    
    print("="*60)
    
    if total_restored > 0:
        print("\n✅ E-Mails erfolgreich wiederhergestellt!")
        print("💡 TIPP: Prüfe deinen Posteingang in deinem E-Mail-Programm\n")
    elif total_found > 0 and args.dry_run:
        print("\n💡 Führe ohne --dry-run aus um E-Mails wiederherzustellen\n")
    else:
        print("\n✅ Nichts zu tun - alles in Ordnung!\n")

if __name__ == "__main__":
    main()

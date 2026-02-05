#!/usr/bin/env python3
"""
TempMail Interactive v3.0
Single-file temporary email service with interactive menu

Features:
- Auto-generate email on startup
- Auto-copy email/code/link to clipboard
- Wait for verification codes, links, or any email
- Session history with re-login support
- Real-time waiting animation
"""

import requests
import time
import json
import random
import string
import re
import sys
import os
import itertools
import threading
from datetime import datetime

# ============================================================================
#                           CLIPBOARD SUPPORT
# ============================================================================

def copy_to_clipboard(text):
    """Copy text to clipboard (cross-platform)"""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        # Fallback for Windows without pyperclip
        try:
            import subprocess
            process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            return True
        except:
            return False
    except:
        return False

# ============================================================================
#                           HISTORY MANAGER
# ============================================================================

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tempmail_history.json')

def load_history():
    """Load email history from file"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"sessions": []}

def save_history(history):
    """Save email history to file"""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"⚠️  Could not save history: {e}")

def add_to_history(email, password, codes=None, links=None):
    """Add or update email in history"""
    history = load_history()
    
    # Check if email already exists
    for session in history['sessions']:
        if session['email'] == email:
            session['last_used'] = datetime.now().isoformat()
            if codes:
                session.setdefault('codes_received', []).extend(codes)
            if links:
                session.setdefault('links_received', []).extend(links)
            save_history(history)
            return
    
    # Add new session
    history['sessions'].append({
        'email': email,
        'password': password,
        'created_at': datetime.now().isoformat(),
        'last_used': datetime.now().isoformat(),
        'codes_received': codes or [],
        'links_received': links or []
    })
    save_history(history)

# ============================================================================
#                           TEMPMAIL SERVICE
# ============================================================================

class TempMailService:
    def __init__(self):
        self.base_url = 'https://api.mail.tm'
        self.session = requests.Session()
        self.current_email = None
        self.current_password = None
        self.auth_token = None
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_available_domains(self):
        """Get list of available email domains"""
        try:
            response = self.session.get(f"{self.base_url}/domains", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'hydra:member' in data:
                    domains = data['hydra:member']
                elif isinstance(data, list):
                    domains = data
                else:
                    return []
                return [d.get('domain', d) if isinstance(d, dict) else str(d) for d in domains]
            return []
        except Exception as e:
            print(f"❌ Error getting domains: {e}")
            return []
    
    def generate_email(self):
        """Generate a new temporary email address"""
        try:
            domains = self.get_available_domains()
            if not domains:
                print("❌ No domains available")
                return None
            
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            domain = random.choice(domains)
            email = f"{username}@{domain}"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            
            # Create account
            response = self.session.post(
                f"{self.base_url}/accounts",
                json={"address": email, "password": password},
                timeout=15
            )
            
            if response.status_code == 201:
                # Get auth token
                return self._authenticate(email, password)
            else:
                print(f"❌ Failed to create account: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error generating email: {e}")
            return None
    
    def login(self, email, password):
        """Login to existing email account"""
        return self._authenticate(email, password)
    
    def _authenticate(self, email, password):
        """Authenticate and get token"""
        try:
            token_response = self.session.post(
                f"{self.base_url}/token",
                json={"address": email, "password": password},
                timeout=15
            )
            
            if token_response.status_code == 200:
                token_data = token_response.json()
                self.auth_token = token_data.get('token')
                self.current_email = email
                self.current_password = password
                
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                # Save to history
                add_to_history(email, password)
                
                return {
                    'email': email,
                    'password': password,
                    'status': 'success'
                }
            else:
                print(f"❌ Authentication failed: {token_response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error authenticating: {e}")
            return None
    
    def check_messages(self):
        """Check for messages in current email"""
        if not self.auth_token:
            return []
        
        try:
            response = self.session.get(f"{self.base_url}/messages", timeout=15)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'hydra:member' in data:
                    messages = data['hydra:member']
                elif isinstance(data, list):
                    messages = data
                else:
                    return []
                
                result = []
                for msg in messages:
                    if isinstance(msg, dict):
                        from_info = msg.get('from', {})
                        from_addr = from_info.get('address', '') if isinstance(from_info, dict) else str(from_info)
                        result.append({
                            'id': msg.get('id'),
                            'from': from_addr,
                            'subject': msg.get('subject', ''),
                            'received_at': msg.get('createdAt', ''),
                            'preview': (msg.get('intro', '') or '')[:100]
                        })
                return result
            return []
        except Exception as e:
            print(f"❌ Error checking messages: {e}")
            return []
    
    def get_message_content(self, message_id):
        """Get full message content"""
        if not self.auth_token:
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/messages/{message_id}", timeout=15)
            if response.status_code == 200:
                msg = response.json()
                from_info = msg.get('from', {})
                from_addr = from_info.get('address', '') if isinstance(from_info, dict) else str(from_info)
                
                html_content = msg.get('html', [])
                if isinstance(html_content, str):
                    html_content = [html_content]
                elif not isinstance(html_content, list):
                    html_content = []
                
                return {
                    'id': msg.get('id'),
                    'from': from_addr,
                    'subject': msg.get('subject', ''),
                    'html_content': html_content,
                    'text_content': msg.get('text', ''),
                    'received_at': msg.get('createdAt', '')
                }
            return None
        except Exception as e:
            print(f"❌ Error getting message: {e}")
            return None
    
    def extract_verification_code(self, content):
        """Extract verification code from message"""
        if not content:
            return None
        
        text = content.get('text_content', '')
        if not text:
            return None
        
        patterns = [
            r'(?:verification|verify|code|otp|pin)[:\s]+([A-Z0-9]{4,8})',
            r'(?:code|otp|pin)\s*(?:is|:)\s*([A-Z0-9]{4,8})',
            r'\b([0-9]{4,6})\b',
            r'\b([A-Z0-9]{6})\b',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        return None
    
    def extract_verification_links(self, content):
        """Extract verification links from message"""
        if not content:
            return []
        
        all_content = content.get('text_content', '')
        for html_part in content.get('html_content', []):
            if isinstance(html_part, str):
                all_content += " " + html_part
        
        patterns = [
            r'https?://[^\s<>"{}|\\^`\[\]]+(?:verify|confirm|activate|validation|auth)[^\s<>"{}|\\^`\[\]]*',
            r'https?://[^\s<>"{}|\\^`\[\]]*(?:token|code|key)=[^\s<>"{}|\\^`\[\]]+',
        ]
        
        links = []
        for pattern in patterns:
            matches = re.findall(pattern, all_content, re.IGNORECASE)
            links.extend(matches)
        return list(set(links))
    
    def extract_all_links(self, content):
        """Extract all links from message"""
        if not content:
            return []
        
        all_content = content.get('text_content', '')
        for html_part in content.get('html_content', []):
            if isinstance(html_part, str):
                all_content += " " + html_part
        
        pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        links = re.findall(pattern, all_content, re.IGNORECASE)
        return list(set(links))

# ============================================================================
#                           SPINNER / ANIMATION
# ============================================================================

class Spinner:
    def __init__(self, message="Waiting"):
        self.message = message
        self.running = False
        self.start_time = None
        self.thread = None
    
    def spin(self):
        spinner_chars = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        while self.running:
            elapsed = int(time.time() - self.start_time)
            sys.stdout.write(f'\r{next(spinner_chars)} {self.message}... [{elapsed}s elapsed]   ')
            sys.stdout.flush()
            time.sleep(0.1)
    
    def start(self):
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()
    
    def stop(self, clear=True):
        self.running = False
        if self.thread:
            self.thread.join()
        if clear:
            sys.stdout.write('\r' + ' ' * 60 + '\r')
            sys.stdout.flush()

# ============================================================================
#                           WAIT FUNCTIONS
# ============================================================================

def wait_for_verification(service, wait_type='any', timeout=60):
    """Wait for verification code/link with spinner"""
    spinner = Spinner(f"Waiting for {wait_type}")
    spinner.start()
    
    start_time = time.time()
    initial_count = len(service.check_messages())
    
    try:
        while time.time() - start_time < timeout:
            messages = service.check_messages()
            
            for msg in messages:
                content = service.get_message_content(msg['id'])
                if content:
                    code = service.extract_verification_code(content)
                    links = service.extract_verification_links(content)
                    
                    if wait_type == 'code' and code:
                        spinner.stop()
                        return {'type': 'code', 'value': code, 'message': msg}
                    elif wait_type == 'link' and links:
                        spinner.stop()
                        return {'type': 'link', 'value': links[0], 'all_links': links, 'message': msg}
                    elif wait_type == 'any':
                        if code:
                            spinner.stop()
                            return {'type': 'code', 'value': code, 'message': msg}
                        if links:
                            spinner.stop()
                            return {'type': 'link', 'value': links[0], 'all_links': links, 'message': msg}
                    elif wait_type == 'email' and len(messages) > initial_count:
                        spinner.stop()
                        return {'type': 'email', 'content': content, 'message': msg}
            
            time.sleep(2)
    finally:
        spinner.stop()
    
    return None

# ============================================================================
#                           MENU FUNCTIONS
# ============================================================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(email=None):
    """Print application header"""
    print("\n" + "═" * 60)
    print("            📧 TEMPMAIL INTERACTIVE v3.0")
    print("═" * 60)
    if email:
        print(f"\n📬 Current Email: {email}")
    print()

def print_menu():
    """Print main menu"""
    print("─" * 60)
    print("                    MAIN MENU")
    print("─" * 60)
    print("  [1] 🔄 Generate New Email")
    print("  [2] 📂 Load Previous Email (from history)")
    print("  [3] ⏳ Wait for Verification Code")
    print("  [4] 🔗 Wait for Verification Link")
    print("  [5] 🎯 Wait for Any Verification")
    print("  [6] 📬 Wait for Any New Email")
    print("  [7] 📋 Check All Messages")
    print("  [8] 📖 Read Specific Message")
    print("  [9] 📊 Service Status")
    print("  [0] ❌ Exit")
    print("─" * 60)

def get_timeout():
    """Get timeout from user with default"""
    try:
        user_input = input("⏱️  Timeout in seconds [60]: ").strip()
        if not user_input:
            return 60
        return int(user_input)
    except:
        return 60

def show_history_menu(service):
    """Show history selection menu"""
    history = load_history()
    sessions = history.get('sessions', [])
    
    if not sessions:
        print("\n📭 No saved emails in history.")
        input("\nPress Enter to continue...")
        return False
    
    print("\n" + "─" * 60)
    print("              📂 SAVED EMAILS (History)")
    print("─" * 60)
    
    for i, session in enumerate(sessions[-10:], 1):  # Show last 10
        created = session.get('created_at', 'Unknown')[:16].replace('T', ' ')
        print(f"  [{i}] {session['email']}")
        print(f"      Created: {created}")
    print("  [0] ← Back to Main Menu")
    print("─" * 60)
    
    try:
        choice = int(input("\nSelect email to load [0-{}]: ".format(len(sessions[-10:]))))
        if choice == 0:
            return False
        if 1 <= choice <= len(sessions[-10:]):
            selected = sessions[-10:][choice - 1]
            print(f"\n🔄 Logging in to {selected['email']}...")
            result = service.login(selected['email'], selected['password'])
            if result:
                print(f"✅ Logged in successfully!")
                if copy_to_clipboard(selected['email']):
                    print("📋 Email copied to clipboard!")
                return True
            else:
                print("❌ Failed to login. Account may have expired.")
                return False
    except:
        pass
    return False

# ============================================================================
#                           MAIN APPLICATION
# ============================================================================

def main():
    clear_screen()
    print_header()
    
    service = TempMailService()
    
    # Auto-generate email on startup
    print("🔄 Generating temporary email...")
    result = service.generate_email()
    
    if not result:
        print("❌ Failed to generate email. Check your internet connection.")
        input("\nPress Enter to exit...")
        return
    
    print(f"✅ Email generated: {result['email']}")
    if copy_to_clipboard(result['email']):
        print("📋 Email copied to clipboard!")
    
    input("\nPress Enter to continue to menu...")
    
    # Main loop
    while True:
        clear_screen()
        print_header(service.current_email)
        print_menu()
        
        try:
            choice = input("\nEnter choice [0-9]: ").strip()
            
            if choice == '0':
                print("\n👋 Goodbye!")
                break
            
            elif choice == '1':  # Generate New Email
                print("\n🔄 Generating new email...")
                result = service.generate_email()
                if result:
                    print(f"✅ New email: {result['email']}")
                    if copy_to_clipboard(result['email']):
                        print("📋 Email copied to clipboard!")
                else:
                    print("❌ Failed to generate email")
                input("\nPress Enter to continue...")
            
            elif choice == '2':  # Load from history
                show_history_menu(service)
            
            elif choice == '3':  # Wait for Code
                if not service.current_email:
                    print("❌ No active email. Generate or load one first.")
                else:
                    timeout = get_timeout()
                    print(f"\n⏳ Waiting for verification code (max {timeout}s)...\n")
                    result = wait_for_verification(service, 'code', timeout)
                    if result:
                        print(f"\n✅ Code received: {result['value']}")
                        if copy_to_clipboard(result['value']):
                            print("📋 Code copied to clipboard!")
                        add_to_history(service.current_email, service.current_password, codes=[result['value']])
                    else:
                        print("\n❌ No code received within timeout")
                input("\nPress Enter to continue...")
            
            elif choice == '4':  # Wait for Link
                if not service.current_email:
                    print("❌ No active email. Generate or load one first.")
                else:
                    timeout = get_timeout()
                    print(f"\n🔗 Waiting for verification link (max {timeout}s)...\n")
                    result = wait_for_verification(service, 'link', timeout)
                    if result:
                        print(f"\n✅ Link received: {result['value']}")
                        if copy_to_clipboard(result['value']):
                            print("📋 Link copied to clipboard!")
                        add_to_history(service.current_email, service.current_password, links=[result['value']])
                    else:
                        print("\n❌ No link received within timeout")
                input("\nPress Enter to continue...")
            
            elif choice == '5':  # Wait for Any
                if not service.current_email:
                    print("❌ No active email. Generate or load one first.")
                else:
                    timeout = get_timeout()
                    print(f"\n🎯 Waiting for any verification (max {timeout}s)...\n")
                    result = wait_for_verification(service, 'any', timeout)
                    if result:
                        print(f"\n✅ {result['type'].upper()} received: {result['value']}")
                        if copy_to_clipboard(result['value']):
                            print(f"📋 {result['type'].capitalize()} copied to clipboard!")
                        if result['type'] == 'code':
                            add_to_history(service.current_email, service.current_password, codes=[result['value']])
                        else:
                            add_to_history(service.current_email, service.current_password, links=[result['value']])
                    else:
                        print("\n❌ No verification received within timeout")
                input("\nPress Enter to continue...")
            
            elif choice == '6':  # Wait for Email
                if not service.current_email:
                    print("❌ No active email. Generate or load one first.")
                else:
                    timeout = get_timeout()
                    print(f"\n📬 Waiting for new email (max {timeout}s)...\n")
                    result = wait_for_verification(service, 'email', timeout)
                    if result:
                        print(f"\n✅ New email received!")
                        print(f"   From: {result['message'].get('from', 'Unknown')}")
                        print(f"   Subject: {result['message'].get('subject', 'No subject')}")
                    else:
                        print("\n❌ No new email received within timeout")
                input("\nPress Enter to continue...")
            
            elif choice == '7':  # Check Messages
                if not service.current_email:
                    print("❌ No active email.")
                else:
                    messages = service.check_messages()
                    print(f"\n📋 Messages for {service.current_email}:")
                    print("─" * 50)
                    if messages:
                        for i, msg in enumerate(messages, 1):
                            print(f"\n[{i}] From: {msg['from']}")
                            print(f"    Subject: {msg['subject']}")
                            print(f"    ID: {msg['id']}")
                    else:
                        print("📭 No messages found")
                input("\nPress Enter to continue...")
            
            elif choice == '8':  # Read Message
                if not service.current_email:
                    print("❌ No active email.")
                else:
                    messages = service.check_messages()
                    if not messages:
                        print("📭 No messages to read")
                    else:
                        print("\nAvailable messages:")
                        for i, msg in enumerate(messages, 1):
                            print(f"  [{i}] {msg['subject'][:40] or 'No subject'}")
                        try:
                            idx = int(input("\nSelect message number: ")) - 1
                            if 0 <= idx < len(messages):
                                content = service.get_message_content(messages[idx]['id'])
                                if content:
                                    print(f"\n{'─' * 50}")
                                    print(f"From: {content['from']}")
                                    print(f"Subject: {content['subject']}")
                                    print(f"{'─' * 50}")
                                    print(content.get('text_content', '')[:500])
                                    
                                    # Extract and show code/links
                                    code = service.extract_verification_code(content)
                                    links = service.extract_verification_links(content)
                                    if code:
                                        print(f"\n🔑 Verification Code: {code}")
                                        if copy_to_clipboard(code):
                                            print("📋 Copied!")
                                    if links:
                                        print(f"\n🔗 Verification Links:")
                                        for link in links:
                                            print(f"   {link}")
                        except:
                            pass
                input("\nPress Enter to continue...")
            
            elif choice == '9':  # Status
                print(f"\n📊 Service Status")
                print("─" * 40)
                print(f"Current Email: {service.current_email or 'None'}")
                print(f"Authenticated: {'Yes' if service.auth_token else 'No'}")
                print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                history = load_history()
                print(f"Saved Emails: {len(history.get('sessions', []))}")
                input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\nPress Enter to continue...")

if __name__ == '__main__':
    main()

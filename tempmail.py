#!/usr/bin/env python3
"""
TempMail All-in-One
Simple script that combines CLI and API server functionality
"""

import sys
import json
import threading
import time
from tempmail_service import TempMailService

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def run_interactive_mode():
    """Interactive mode for easy testing"""
    print("🔥 TempMail Interactive Mode")
    print("=" * 40)
    
    service = TempMailService()
    
    while True:
        print("\n📋 What would you like to do?")
        print("1. Generate new email")
        print("2. Check messages")
        print("3. Wait for verification (any type)")
        print("4. Wait for verification code")
        print("5. Wait for verification link")
        print("6. Service status")
        print("7. Exit")
        
        try:
            choice = input("\n👉 Choose (1-7): ").strip()
            
            if choice == '1':
                print("\n🔄 Generating new email...")
                result = service.generate_email()
                if result:
                    print(f"✅ Email: {result['email']}")
                    print(f"🔑 Password: {result['password']}")
                else:
                    print("❌ Failed to generate email")
            
            elif choice == '2':
                if not service.current_email:
                    print("❌ No active email. Generate one first.")
                    continue
                
                print("📧 Checking messages...")
                messages = service.check_messages()
                print(f"📬 Found {len(messages)} messages")
                
                for i, msg in enumerate(messages, 1):
                    print(f"\n📨 Message {i}:")
                    print(f"  From: {msg['from']}")
                    print(f"  Subject: {msg['subject']}")
                    print(f"  Preview: {msg['preview']}")
                    
                    # Ask if user wants full content
                    if input("  View full content? (y/n): ").lower() == 'y':
                        content = service.get_message_content(msg['id'])
                        if content:
                            parsed = service.parse_message_content(content)
                            if parsed['verification_code']:
                                print(f"  🔑 Verification Code: {parsed['verification_code']}")
                            if parsed['verification_links']:
                                print(f"  🔗 Verification Links:")
                                for link in parsed['verification_links']:
                                    print(f"    • {link}")
            
            elif choice == '3':
                if not service.current_email:
                    print("❌ No active email. Generate one first.")
                    continue
                
                timeout = input("⏰ Timeout in seconds (default 60): ").strip()
                timeout = int(timeout) if timeout.isdigit() else 60
                
                print(f"⏳ Waiting for any verification (timeout: {timeout}s)...")
                print("💡 Send a verification email now!")
                
                result = service.wait_for_any_verification(timeout)
                if result:
                    print(f"✅ {result['type'].replace('_', ' ').title()} received!")
                    if result['type'] == 'verification_code':
                        print(f"🔑 Code: {result['code']}")
                    elif result['type'] == 'verification_link':
                        print(f"🔗 Link: {result['primary_link']}")
                else:
                    print("❌ No verification received within timeout")
            
            elif choice == '4':
                if not service.current_email:
                    print("❌ No active email. Generate one first.")
                    continue
                
                timeout = input("⏰ Timeout in seconds (default 60): ").strip()
                timeout = int(timeout) if timeout.isdigit() else 60
                
                print(f"⏳ Waiting for verification code (timeout: {timeout}s)...")
                result = service.wait_for_verification_code(timeout)
                if result:
                    print(f"✅ Code received: {result['code']}")
                else:
                    print("❌ No verification code received")
            
            elif choice == '5':
                if not service.current_email:
                    print("❌ No active email. Generate one first.")
                    continue
                
                timeout = input("⏰ Timeout in seconds (default 60): ").strip()
                timeout = int(timeout) if timeout.isdigit() else 60
                
                print(f"⏳ Waiting for verification link (timeout: {timeout}s)...")
                result = service.wait_for_verification_link(timeout)
                if result:
                    print(f"✅ Link received: {result['primary_link']}")
                else:
                    print("❌ No verification link received")
            
            elif choice == '6':
                status = service.get_status()
                print("📊 Service Status:")
                print_json(status)
            
            elif choice == '7':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please choose 1-7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def quick_test():
    """Quick test function"""
    print("🧪 Quick TempMail Test")
    print("=" * 30)
    
    service = TempMailService()
    
    # Generate email
    print("🔄 Generating email...")
    result = service.generate_email()
    if result:
        print(f"✅ Generated: {result['email']}")
        
        # Check domains
        domains = service.get_available_domains()
        print(f"🌐 Available domains: {len(domains)}")
        
        # Check status
        status = service.get_status()
        print(f"📊 Service ready: {status['authenticated']}")
        
        print("\n💡 Email is ready! You can now:")
        print(f"   • Send emails to: {result['email']}")
        print(f"   • Use interactive mode: python tempmail.py interactive")
        print(f"   • Start API server: python tempmail.py server")
        
    else:
        print("❌ Failed to generate email")

def main():
    if len(sys.argv) < 2:
        print("TempMail All-in-One Tool")
        print("\nUsage:")
        print("  python tempmail.py test         - Quick test")
        print("  python tempmail.py interactive  - Interactive mode")
        print("  python tempmail.py server [port] - Start API server") 
        print("  python tempmail.py generate     - Generate email and exit")
        print("\n💡 Recommended: Start with 'python tempmail.py interactive'")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'test':
        quick_test()
    
    elif command == 'interactive':
        run_interactive_mode()
    
    elif command == 'server':
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 3001
        print(f"🚀 Starting TempMail API server on port {port}...")
        
        # Import and start server
        from api_server import app
        try:
            app.run(host='0.0.0.0', port=port, debug=False)
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
    
    elif command == 'generate':
        service = TempMailService()
        result = service.generate_email()
        if result:
            print(f"Email: {result['email']}")
            print(f"Password: {result['password']}")
        else:
            print("Failed to generate email")
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'python tempmail.py' to see available commands")

if __name__ == '__main__':
    main()
"""
Simple CLI tool for TempMail Service
Command-line interface for easy email operations
"""

import sys
import json
from tempmail_service import TempMailService

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def main():
    if len(sys.argv) < 2:
        print("TempMail CLI Tool v2.0")
        print("\nUsage:")
        print("  python cli.py generate              - Generate new email")
        print("  python cli.py messages              - Check messages")
        print("  python cli.py message <id>          - Get specific message")
        print("  python cli.py wait-code [timeout]   - Wait for verification code")
        print("  python cli.py wait-link [timeout]   - Wait for verification link")
        print("  python cli.py wait-any [timeout]    - Wait for code OR link")
        print("  python cli.py wait-email [timeout]  - Wait for any new email")
        print("  python cli.py status                - Get service status")
        print("  python cli.py domains               - Get available domains")
        print("  python cli.py server [port]         - Start API server (default port 3001)")
        return
    
    service = TempMailService()
    command = sys.argv[1].lower()
    
    if command == 'server':
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 3001
        print(f"🚀 Starting TempMail API server on port {port}...")
        print(f"📡 API will be available at: http://localhost:{port}")
        print(f"📖 API docs at: http://localhost:{port}")
        print("Press Ctrl+C to stop\n")
        
        # Import and run Flask app
        from api_server import app
        app.run(host='0.0.0.0', port=port, debug=False)
        return
    
    if command == 'generate':
        print("🔄 Generating new temporary email...")
        result = service.generate_email()
        if result:
            print("✅ Email generated successfully!")
            print_json(result)
        else:
            print("❌ Failed to generate email")
    
    elif command == 'messages':
        print("📧 Checking messages...")
        if not service.current_email:
            print("❌ No active email. Generate an email first.")
            return
        
        messages = service.check_messages()
        print(f"📬 Found {len(messages)} messages for {service.current_email}")
        if messages:
            print_json(messages)
        else:
            print("📭 No messages found")
    
    elif command == 'message':
        if len(sys.argv) < 3:
            print("❌ Please provide message ID")
            return
        
        message_id = sys.argv[2]
        print(f"📖 Getting message {message_id}...")
        content = service.get_message_content(message_id)
        if content:
            # Parse the content
            parsed = service.parse_message_content(content)
            print("📄 Parsed Content:")
            print_json(parsed)
            print("\n📄 Raw Content:")
            print_json(content)
        else:
            print("❌ Message not found")
    
    elif command == 'wait-code':
        timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        print(f"⏳ Waiting for verification code (timeout: {timeout}s)...")
        
        if not service.current_email:
            print("❌ No active email. Generate an email first.")
            return
        
        result = service.wait_for_verification_code(timeout)
        if result:
            print("✅ Verification code received!")
            print(f"🔑 Code: {result['code']}")
            print_json(result)
        else:
            print("❌ No verification code received within timeout")
    
    elif command == 'wait-link':
        timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        print(f"⏳ Waiting for verification link (timeout: {timeout}s)...")
        
        if not service.current_email:
            print("❌ No active email. Generate an email first.")
            return
        
        result = service.wait_for_verification_link(timeout)
        if result:
            print("✅ Verification link received!")
            print(f"🔗 Primary Link: {result['primary_link']}")
            print(f"🔗 All Links: {', '.join(result['links'])}")
            print_json(result)
        else:
            print("❌ No verification link received within timeout")
    
    elif command == 'wait-any':
        timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        print(f"⏳ Waiting for any verification (code or link) (timeout: {timeout}s)...")
        
        if not service.current_email:
            print("❌ No active email. Generate an email first.")
            return
        
        result = service.wait_for_any_verification(timeout)
        if result:
            print(f"✅ {result['type'].replace('_', ' ').title()} received!")
            if result['type'] == 'verification_code':
                print(f"🔑 Code: {result['code']}")
            elif result['type'] == 'verification_link':
                print(f"🔗 Primary Link: {result['primary_link']}")
            print_json(result)
        else:
            print("❌ No verification received within timeout")
    
    elif command == 'wait-email':
        timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        print(f"⏳ Waiting for new email (timeout: {timeout}s)...")
        
        if not service.current_email:
            print("❌ No active email. Generate an email first.")
            return
        
        result = service.wait_for_new_email(timeout)
        if result:
            print("✅ New email received!")
            parsed = result['parsed_content']
            print(f"📧 From: {parsed['sender']}")
            print(f"📝 Subject: {parsed['subject']}")
            if parsed['verification_code']:
                print(f"🔑 Verification Code: {parsed['verification_code']}")
            if parsed['verification_links']:
                print(f"🔗 Verification Links: {', '.join(parsed['verification_links'])}")
            print_json(result)
        else:
            print("❌ No new email received within timeout")
    
    elif command == 'status':
        print("📊 Service Status:")
        status = service.get_status()
        print_json(status)
    
    elif command == 'domains':
        print("🌐 Available domains:")
        domains = service.get_available_domains()
        for domain in domains:
            print(f"  • {domain}")
        print(f"\nTotal: {len(domains)} domains available")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python cli.py' to see available commands")

if __name__ == '__main__':
    main()
"""
Example usage of TempMail Service
Demonstrates common patterns and use cases
"""

from tempmail_service import TempMailService
import time

def example_basic_usage():
    """Basic email generation and message checking"""
    print("=== Basic Usage Example ===")
    
    service = TempMailService()
    
    # Generate new email
    print("🔄 Generating new email...")
    email_info = service.generate_email()
    if email_info:
        print(f"✅ Generated: {email_info['email']}")
        print(f"🔑 Password: {email_info['password']}")
    else:
        print("❌ Failed to generate email")
        return
    
    # Wait a bit and check messages
    print("\n📧 Checking for messages...")
    time.sleep(2)
    messages = service.check_messages()
    print(f"📬 Found {len(messages)} messages")
    
    for msg in messages:
        print(f"  📨 From: {msg['from']}")
        print(f"  📝 Subject: {msg['subject']}")
        print(f"  🕒 Received: {msg['received_at']}")

def example_verification_code():
    """Wait for verification code example"""
    print("\n=== Verification Code Example ===")
    
    service = TempMailService()
    
    # Generate email
    email_info = service.generate_email()
    if not email_info:
        print("❌ Failed to generate email")
        return
    
    print(f"✅ Email ready: {email_info['email']}")
    print("📧 Now send a verification email to this address...")
    print("⏳ Waiting for verification code (60 seconds)...")
    
    # Wait for verification code
    result = service.wait_for_verification_code(timeout=60)
    if result:
        print(f"🎉 Verification code received: {result['code']}")
        print(f"📩 From message: {result['message']['subject']}")
    else:
        print("❌ No verification code received")

def example_message_inspection():
    """Inspect message content in detail"""
    print("\n=== Message Inspection Example ===")
    
    service = TempMailService()
    
    # Generate email
    email_info = service.generate_email()
    if not email_info:
        return
    
    print(f"✅ Email: {email_info['email']}")
    print("📧 Send some test emails and press Enter...")
    input()
    
    # Get all messages
    messages = service.check_messages()
    for msg in messages:
        print(f"\n📨 Message: {msg['id']}")
        print(f"   From: {msg['from']}")
        print(f"   Subject: {msg['subject']}")
        
        # Get full content
        content = service.get_message_content(msg['id'])
        if content:
            print(f"   Content preview: {content['text_content'][:100]}...")
            
            # Try to extract verification code
            code = service.extract_verification_code(content)
            if code:
                print(f"   🔑 Verification code: {code}")

def example_service_status():
    """Check service status and available domains"""
    print("\n=== Service Status Example ===")
    
    service = TempMailService()
    
    # Check available domains
    domains = service.get_available_domains()
    print(f"🌐 Available domains: {len(domains)}")
    for domain in domains[:5]:  # Show first 5
        print(f"  • {domain}")
    
    # Generate email and check status
    email_info = service.generate_email()
    if email_info:
        status = service.get_status()
        print(f"\n📊 Service Status:")
        print(f"  Current Email: {status['current_email']}")
        print(f"  Authenticated: {status['authenticated']}")
        print(f"  Service Status: {status['service_status']}")

if __name__ == '__main__':
    print("TempMail Service Examples")
    print("=" * 40)
    
    try:
        example_basic_usage()
        example_verification_code()
        example_message_inspection()
        example_service_status()
    except KeyboardInterrupt:
        print("\n\n👋 Examples stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
# TempMail Service 📧

A comprehensive temporary email service using mail.tm API.

---

## 🆕 TempMail Interactive v3.0 (Recommended)

> **Looking for an easier way?** Check out the new single-file interactive version!

```bash
cd TempMailV2
pip install -r requirements.txt
python main.py
```

**Features:**
- ✅ Auto-generate email on startup
- ✅ Auto-copy email/code/link to clipboard
- ✅ Menu-driven interface (no commands to remember)
- ✅ Session history with re-login support
- ✅ Real-time spinner animation

👉 **[Go to TempMailV2](./TempMailV2/README.md)**

---

## Features ✨

- **Generate** temporary email addresses
- **Check** for new messages  
- **Extract** verification codes automatically
- **Extract** verification/confirmation links
- **Extract** all links and email addresses from content
- **Wait** for codes, links, or any new emails with timeout
- **Parse** complete email content with smart extraction
- **RESTful API** and CLI interface

## Quick Start 🚀

### Easy Testing (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Quick test
python tempmail.py test

# Interactive mode (easiest way to test)
python tempmail.py interactive

# All-in-one server + CLI
python tempmail.py server 3001
```

### CLI Usage
```bash
# Generate new email
python cli.py generate

# Wait for any verification (code OR link)
python cli.py wait-any 60

# Start integrated API server
python cli.py server 3001

# Check messages
python cli.py messages
```

## API Endpoints 🔌

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/generate` | Generate new temporary email |
| GET | `/messages` | Get all messages |
| GET | `/message/{id}` | Get message with full parsing |
| POST | `/wait-code` | Wait for verification code |
| POST | `/wait-link` | Wait for verification link |
| POST | `/wait-any` | Wait for code OR link |
| POST | `/wait-email` | Wait for any new email |
| GET | `/status` | Service status |
| GET | `/domains` | Available email domains |

## Enhanced Extraction 🧠

### What Gets Extracted:
- **Verification Codes**: 4-8 digit alphanumeric codes
- **Verification Links**: Confirmation, activation, auth URLs  
- **All Links**: Every HTTP/HTTPS URL in the email
- **Email Addresses**: Any email addresses mentioned
- **Full Parsing**: Complete content analysis

### Smart Pattern Recognition:
```python
# Handles various formats:
"Your verification code is: ABC123"
"Verify your account: https://example.com/verify?token=xyz"
"Click here to activate: https://site.com/activate/12345"
"Code: 123456"
```

## Usage Examples 📝

### Python Integration
```python
from tempmail_service import TempMailService

service = TempMailService()

# Generate email
email_info = service.generate_email()
print(f"New email: {email_info['email']}")

# Wait for any verification (code or link)
result = service.wait_for_any_verification(timeout=60)
if result:
    if result['type'] == 'verification_code':
        print(f"Code: {result['code']}")
    elif result['type'] == 'verification_link':
        print(f"Link: {result['primary_link']}")

# Parse message content
content = service.get_message_content(message_id)
parsed = service.parse_message_content(content)
print("Verification code:", parsed['verification_code'])
print("Verification links:", parsed['verification_links'])
print("All links:", parsed['all_links'])
```

### API Usage
```bash
# Generate email
curl http://localhost:3001/generate

# Wait for any verification
curl -X POST http://localhost:3001/wait-any \
  -H "Content-Type: application/json" \
  -d '{"timeout": 60}'

# Wait for verification link
curl -X POST http://localhost:3001/wait-link \
  -H "Content-Type: application/json" \
  -d '{"timeout": 60}'

# Wait for any new email
curl -X POST http://localhost:3001/wait-email \
  -H "Content-Type: application/json" \
  -d '{"timeout": 60}'
```

## Advanced Features 🚀

### Multi-Type Verification Support:
- **Codes**: `123456`, `ABC123`, `verify: XYZ789`
- **Links**: Activation URLs, confirmation links, auth tokens
- **Smart Detection**: Automatically identifies verification type
- **Flexible Waiting**: Wait for specific type or any verification

### Complete Email Parsing:
- **Sender Information**: From address and name
- **Link Extraction**: All HTTP/HTTPS URLs found
- **Email Extraction**: Any email addresses mentioned
- **Content Preview**: First 200 characters of text
- **Structured Data**: JSON response with all parsed info

## Lightweight & Fast ⚡

- **Minimal dependencies**: Only requests and flask
- **Direct API integration**: No external services
- **Automatic code extraction**: Smart regex patterns
- **Clean API**: Simple JSON responses

Perfect for automation, testing, or integration into larger projects!
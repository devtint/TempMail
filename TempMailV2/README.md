# 📧 TempMail Interactive v3.0

A single-file interactive temporary email service using the [mail.tm](https://mail.tm) API.

## ✨ Features

- **🚀 Auto-generate email on startup** - Ready to use immediately
- **📋 Auto-copy to clipboard** - Email, codes, and links copied automatically
- **⏳ Real-time spinner** - Visual feedback with elapsed time
- **📂 Session history** - Re-login to previous emails
- **🎯 Smart extraction** - Auto-detect verification codes and links
- **⌨️ Menu-driven interface** - Easy numbered menu (0-9)

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

## 📋 Menu Options

| Key | Action |
|-----|--------|
| `1` | 🔄 Generate New Email |
| `2` | 📂 Load Previous Email (from history) |
| `3` | ⏳ Wait for Verification Code |
| `4` | 🔗 Wait for Verification Link |
| `5` | 🎯 Wait for Any Verification (code OR link) |
| `6` | 📬 Wait for Any New Email |
| `7` | 📋 Check All Messages |
| `8` | 📖 Read Specific Message |
| `9` | 📊 Service Status |
| `0` | ❌ Exit |

## 📸 Screenshot

```
════════════════════════════════════════════════════════════
            📧 TEMPMAIL INTERACTIVE v3.0
════════════════════════════════════════════════════════════

📬 Current Email: abc123xyz@domain.com

────────────────────────────────────────────────────────────
                    MAIN MENU
────────────────────────────────────────────────────────────
  [1] 🔄 Generate New Email
  [2] 📂 Load Previous Email (from history)
  [3] ⏳ Wait for Verification Code
  ...
────────────────────────────────────────────────────────────

Enter choice [0-9]: _
```

## 📁 Files

| File | Description |
|------|-------------|
| `main.py` | Single-file application (~520 lines) |
| `requirements.txt` | Dependencies (requests, pyperclip) |
| `.gitignore` | Excludes history file |
| `tempmail_history.json` | Auto-created session history |

## 🔐 Session History

Emails are saved to `tempmail_history.json` for re-login later:

```json
{
  "sessions": [
    {
      "email": "user123@domain.com",
      "password": "auto-generated",
      "created_at": "2026-02-05T16:00:00",
      "codes_received": ["123456"],
      "links_received": []
    }
  ]
}
```

> ⚠️ **Security Note**: This file contains passwords. It's excluded from git via `.gitignore`.

## 🔧 Dependencies

- `requests` - HTTP client for mail.tm API
- `pyperclip` - Cross-platform clipboard support

## 📡 API Used

This project uses the free [mail.tm API](https://docs.mail.tm/):
- No API key required
- 8 QPS rate limit
- Attribution required (link to mail.tm)

## 📜 License

MIT License - Use freely with attribution to mail.tm

#!/usr/bin/env python3
"""
TempMail Web UI
Simple paper-style web interface for TempMail
Run: python web.py
Open: http://localhost:5000
"""

import sys
import os

# Add current directory to path to import from main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, jsonify, request
from main import TempMailService, load_history, add_to_history

app = Flask(__name__)
service = TempMailService()

# ============================================================================
#                           API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_email():
    """Generate new temporary email"""
    result = service.generate_email()
    if result:
        return jsonify({'success': True, 'email': result['email']})
    return jsonify({'success': False, 'error': 'Failed to generate email'}), 500

@app.route('/api/login', methods=['POST'])
def login_email():
    """Login to existing email from history"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password required'}), 400
    
    result = service.login(email, password)
    if result:
        return jsonify({'success': True, 'email': result['email']})
    return jsonify({'success': False, 'error': 'Login failed'}), 401

@app.route('/api/status')
def get_status():
    """Get current status"""
    return jsonify({
        'success': True,
        'email': service.current_email,
        'authenticated': bool(service.auth_token)
    })

@app.route('/api/messages')
def get_messages():
    """Get all messages"""
    if not service.current_email:
        return jsonify({'success': False, 'error': 'No active email'}), 400
    
    messages = service.check_messages()
    return jsonify({'success': True, 'messages': messages})

@app.route('/api/message/<message_id>')
def get_message(message_id):
    """Get specific message content"""
    if not service.current_email:
        return jsonify({'success': False, 'error': 'No active email'}), 400
    
    content = service.get_message_content(message_id)
    if content:
        code = service.extract_verification_code(content)
        links = service.extract_verification_links(content)
        all_links = service.extract_all_links(content)
        
        return jsonify({
            'success': True,
            'content': content,
            'code': code,
            'verification_links': links,
            'all_links': all_links
        })
    return jsonify({'success': False, 'error': 'Message not found'}), 404

@app.route('/api/history')
def get_history():
    """Get email history"""
    history = load_history()
    # Return without passwords for security in UI
    sessions = []
    for s in history.get('sessions', []):
        sessions.append({
            'email': s['email'],
            'password': s['password'],  # Needed for re-login
            'created_at': s.get('created_at', ''),
            'codes_received': s.get('codes_received', []),
            'links_received': s.get('links_received', [])
        })
    return jsonify({'success': True, 'sessions': sessions})

@app.route('/api/wait/<wait_type>', methods=['POST'])
def wait_for(wait_type):
    """Wait for verification (code/link/any/email)"""
    if not service.current_email:
        return jsonify({'success': False, 'error': 'No active email'}), 400
    
    data = request.json or {}
    timeout = data.get('timeout', 60)
    
    # Check messages and look for verification
    messages = service.check_messages()
    
    for msg in messages:
        content = service.get_message_content(msg['id'])
        if content:
            code = service.extract_verification_code(content)
            links = service.extract_verification_links(content)
            
            if wait_type == 'code' and code:
                add_to_history(service.current_email, service.current_password, codes=[code])
                return jsonify({'success': True, 'type': 'code', 'value': code, 'message': msg})
            
            if wait_type == 'link' and links:
                add_to_history(service.current_email, service.current_password, links=links)
                return jsonify({'success': True, 'type': 'link', 'value': links[0], 'all_links': links, 'message': msg})
            
            if wait_type == 'any':
                if code:
                    add_to_history(service.current_email, service.current_password, codes=[code])
                    return jsonify({'success': True, 'type': 'code', 'value': code, 'message': msg})
                if links:
                    add_to_history(service.current_email, service.current_password, links=links)
                    return jsonify({'success': True, 'type': 'link', 'value': links[0], 'all_links': links, 'message': msg})
            
            if wait_type == 'email':
                return jsonify({'success': True, 'type': 'email', 'content': content, 'message': msg})
    
    return jsonify({'success': False, 'found': False, 'message': 'No verification found yet'})

# ============================================================================
#                           MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 50)
    print("  📧 TempMail Web UI")
    print("=" * 50)
    print()
    print("  Open in browser: http://localhost:5000")
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)

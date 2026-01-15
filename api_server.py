"""
Simple TempMail API Server
RESTful API for temporary email operations

Endpoints:
- GET  /generate    - Generate new temporary email
- GET  /messages    - Check for messages
- GET  /message/{id} - Get specific message content  
- GET  /status      - Get service status
- POST /wait-code   - Wait for verification code
"""

from flask import Flask, jsonify, request
from tempmail_service import TempMailService

app = Flask(__name__)
temp_mail = TempMailService()

@app.route('/generate', methods=['GET'])
def generate_email():
    """Generate a new temporary email address"""
    result = temp_mail.generate_email()
    if result:
        return jsonify({
            'success': True,
            'data': result
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to generate email'
        }), 500

@app.route('/messages', methods=['GET'])
def get_messages():
    """Get all messages for current email"""
    if not temp_mail.current_email:
        return jsonify({
            'success': False,
            'error': 'No active email. Generate an email first.'
        }), 400
    
    messages = temp_mail.check_messages()
    return jsonify({
        'success': True,
        'email': temp_mail.current_email,
        'count': len(messages),
        'data': messages
    })

@app.route('/message/<message_id>', methods=['GET'])
def get_message(message_id):
    """Get specific message content with full parsing"""
    if not temp_mail.current_email:
        return jsonify({
            'success': False,
            'error': 'No active email. Generate an email first.'
        }), 400
    
    content = temp_mail.get_message_content(message_id)
    if content:
        # Parse all content
        parsed = temp_mail.parse_message_content(content)
        
        return jsonify({
            'success': True,
            'data': {
                'raw_content': content,
                'parsed_content': parsed
            }
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Message not found'
        }), 404

@app.route('/wait-code', methods=['POST'])
def wait_for_code():
    """Wait for verification code in new messages"""
    if not temp_mail.current_email:
        return jsonify({
            'success': False,
            'error': 'No active email. Generate an email first.'
        }), 400
    
    # Get timeout from request (default 60 seconds)
    timeout = request.json.get('timeout', 60) if request.is_json else 60
    
    result = temp_mail.wait_for_verification_code(timeout)
    if result:
        return jsonify({
            'success': True,
            'data': result
        })
    else:
        return jsonify({
            'success': False,
            'error': 'No verification code received within timeout period'
        }), 408

@app.route('/wait-link', methods=['POST'])
def wait_for_link():
    """Wait for verification link in new messages"""
    if not temp_mail.current_email:
        return jsonify({
            'success': False,
            'error': 'No active email. Generate an email first.'
        }), 400
    
    timeout = request.json.get('timeout', 60) if request.is_json else 60
    
    result = temp_mail.wait_for_verification_link(timeout)
    if result:
        return jsonify({
            'success': True,
            'data': result
        })
    else:
        return jsonify({
            'success': False,
            'error': 'No verification link received within timeout period'
        }), 408

@app.route('/wait-any', methods=['POST'])
def wait_for_any():
    """Wait for any type of verification (code or link)"""
    if not temp_mail.current_email:
        return jsonify({
            'success': False,
            'error': 'No active email. Generate an email first.'
        }), 400
    
    timeout = request.json.get('timeout', 60) if request.is_json else 60
    
    result = temp_mail.wait_for_any_verification(timeout)
    if result:
        return jsonify({
            'success': True,
            'data': result
        })
    else:
        return jsonify({
            'success': False,
            'error': 'No verification received within timeout period'
        }), 408

@app.route('/wait-email', methods=['POST'])
def wait_for_email():
    """Wait for any new email"""
    if not temp_mail.current_email:
        return jsonify({
            'success': False,
            'error': 'No active email. Generate an email first.'
        }), 400
    
    timeout = request.json.get('timeout', 60) if request.is_json else 60
    
    result = temp_mail.wait_for_new_email(timeout)
    if result:
        return jsonify({
            'success': True,
            'data': result
        })
    else:
        return jsonify({
            'success': False,
            'error': 'No new email received within timeout period'
        }), 408

@app.route('/status', methods=['GET'])
def get_status():
    """Get service status"""
    status = temp_mail.get_status()
    return jsonify({
        'success': True,
        'data': status
    })

@app.route('/domains', methods=['GET'])
def get_domains():
    """Get available email domains"""
    domains = temp_mail.get_available_domains()
    return jsonify({
        'success': True,
        'count': len(domains),
        'data': domains
    })

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        'service': 'TempMail API',
        'version': '2.0.0',
        'endpoints': {
            'GET /generate': 'Generate new temporary email',
            'GET /messages': 'Get all messages for current email',
            'GET /message/{id}': 'Get specific message with full parsing',
            'POST /wait-code': 'Wait for verification code (JSON: {"timeout": 60})',
            'POST /wait-link': 'Wait for verification link (JSON: {"timeout": 60})',
            'POST /wait-any': 'Wait for any verification (code or link)',
            'POST /wait-email': 'Wait for any new email',
            'GET /status': 'Get service status',
            'GET /domains': 'Get available email domains'
        },
        'features': {
            'verification_codes': 'Extract 4-8 digit codes automatically',
            'verification_links': 'Extract confirmation/activation links',
            'all_links': 'Extract all HTTP/HTTPS links from emails',
            'email_addresses': 'Extract email addresses from content',
            'full_parsing': 'Complete content analysis and extraction'
        },
        'usage_examples': {
            '1_generate': 'GET /generate - to create email',
            '2_wait_any': 'POST /wait-any - to wait for code OR link',
            '3_wait_specific': 'POST /wait-code or /wait-link - for specific type',
            '4_check_messages': 'GET /messages - to check all messages',
            '5_new_email': 'POST /wait-email - to wait for any new email'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
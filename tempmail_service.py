"""
Lightweight TempMail Service
Simple API for temporary email operations using mail.tm

Features:
- Generate temporary email addresses
- Check for new messages  
- Extract verification codes
- Clean and minimal implementation
"""

import requests
import time
import json
import random
import string
from datetime import datetime

class TempMailService:
    def __init__(self):
        self.base_url = 'https://api.mail.tm'
        self.session = requests.Session()
        self.current_email = None
        self.current_password = None
        self.auth_token = None
        
        # Set headers
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
                # Handle both response formats
                if isinstance(data, dict) and 'data' in data:
                    domains = data['data']
                elif isinstance(data, list):
                    domains = data
                else:
                    return []
                
                return [domain.get('domain', domain) if isinstance(domain, dict) else str(domain) for domain in domains]
            return []
        except Exception as e:
            print(f"Error getting domains: {e}")
            return []
    
    def generate_email(self):
        """Generate a new temporary email address"""
        try:
            # Get available domains
            domains = self.get_available_domains()
            if not domains:
                return None
                
            # Generate random email
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            domain = random.choice(domains)
            email = f"{username}@{domain}"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            
            # Create account
            payload = {
                "address": email,
                "password": password
            }
            
            response = self.session.post(f"{self.base_url}/accounts", json=payload, timeout=15)
            
            if response.status_code == 201:
                # Get auth token
                token_response = self.session.post(f"{self.base_url}/token", json={
                    "address": email,
                    "password": password
                }, timeout=15)
                
                if token_response.status_code == 200:
                    token_data = token_response.json()
                    self.auth_token = token_data.get('token')
                    self.current_email = email
                    self.current_password = password
                    
                    # Update session headers with auth
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })
                    
                    return {
                        'email': email,
                        'password': password,
                        'status': 'success',
                        'created_at': datetime.now().isoformat()
                    }
            
            return None
        except Exception as e:
            print(f"Error generating email: {e}")
            return None
    
    def check_messages(self, timeout=30):
        """Check for new messages in current email"""
        if not self.auth_token or not self.current_email:
            return []
        
        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            response = self.session.get(f"{self.base_url}/messages", headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle both response formats
                if isinstance(data, dict) and 'data' in data:
                    messages = data['data']
                elif isinstance(data, list):
                    messages = data
                else:
                    return []
                
                message_list = []
                for msg in messages:
                    if isinstance(msg, dict):
                        from_info = msg.get('from', {})
                        from_address = from_info.get('address', '') if isinstance(from_info, dict) else str(from_info)
                        
                        message_list.append({
                            'id': msg.get('id'),
                            'from': from_address,
                            'subject': msg.get('subject', ''),
                            'received_at': msg.get('createdAt', ''),
                            'preview': msg.get('intro', '')[:100] if msg.get('intro') else ''
                        })
                
                return message_list
            return []
        except Exception as e:
            print(f"Error checking messages: {e}")
            return []
    
    def get_message_content(self, message_id):
        """Get full content of a specific message"""
        if not self.auth_token:
            return None
        
        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            response = self.session.get(f"{self.base_url}/messages/{message_id}", headers=headers, timeout=15)
            
            if response.status_code == 200:
                msg_data = response.json()
                
                # Handle from field safely
                from_info = msg_data.get('from', {})
                from_address = from_info.get('address', '') if isinstance(from_info, dict) else str(from_info)
                
                # Handle HTML content safely
                html_content = msg_data.get('html', [])
                if isinstance(html_content, str):
                    html_content = [html_content]
                elif not isinstance(html_content, list):
                    html_content = []
                
                return {
                    'id': msg_data.get('id'),
                    'from': from_address,
                    'subject': msg_data.get('subject', ''),
                    'html_content': html_content,
                    'text_content': msg_data.get('text', ''),
                    'received_at': msg_data.get('createdAt', '')
                }
            return None
        except Exception as e:
            print(f"Error getting message content: {e}")
            return None
    
    def extract_verification_code(self, message_content):
        """Extract verification code from message content"""
        import re
        
        if not message_content:
            return None
        
        text = message_content.get('text_content', '')
        if not text:
            return None
        
        # Common verification code patterns
        patterns = [
            r'verification code[:\s]+([A-Z0-9]{4,8})',
            r'verify[:\s]+([A-Z0-9]{4,8})',
            r'code[:\s]+([A-Z0-9]{4,8})',
            r'([A-Z0-9]{6})',  # 6-digit codes
            r'([0-9]{4,6})',   # 4-6 digit numbers
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
    
    def extract_verification_links(self, message_content):
        """Extract verification/confirmation links from message content"""
        import re
        
        if not message_content:
            return []
        
        # Get both HTML and text content
        html_content = message_content.get('html_content', [])
        text_content = message_content.get('text_content', '')
        
        # Combine all content
        all_content = text_content
        if html_content:
            for html_part in html_content:
                if isinstance(html_part, str):
                    all_content += " " + html_part
        
        # Link patterns for verification
        link_patterns = [
            r'https?://[^\s<>"{}|\\^`\[\]]+(?:verify|confirm|activate|validation|auth)[^\s<>"{}|\\^`\[\]]*',
            r'https?://[^\s<>"{}|\\^`\[\]]*(?:verify|confirm|activate|validation|auth)[^\s<>"{}|\\^`\[\]]+',
            r'https?://[^\s<>"{}|\\^`\[\]]+/[^\s<>"{}|\\^`\[\]]*(?:token|code|key)[^\s<>"{}|\\^`\[\]]*',
        ]
        
        links = []
        for pattern in link_patterns:
            matches = re.findall(pattern, all_content, re.IGNORECASE)
            links.extend(matches)
        
        # Remove duplicates and return
        return list(set(links))
    
    def extract_all_links(self, message_content):
        """Extract all links from message content"""
        import re
        
        if not message_content:
            return []
        
        # Get both HTML and text content
        html_content = message_content.get('html_content', [])
        text_content = message_content.get('text_content', '')
        
        # Combine all content
        all_content = text_content
        if html_content:
            for html_part in html_content:
                if isinstance(html_part, str):
                    all_content += " " + html_part
        
        # Extract all HTTP/HTTPS links
        link_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        links = re.findall(link_pattern, all_content, re.IGNORECASE)
        
        return list(set(links))
    
    def extract_email_addresses(self, message_content):
        """Extract email addresses from message content"""
        import re
        
        if not message_content:
            return []
        
        text = message_content.get('text_content', '')
        if not text:
            return []
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        return list(set(emails))
    
    def parse_message_content(self, message_content):
        """Parse message content and extract all useful information"""
        if not message_content:
            return {}
        
        parsed = {
            'verification_code': self.extract_verification_code(message_content),
            'verification_links': self.extract_verification_links(message_content),
            'all_links': self.extract_all_links(message_content),
            'email_addresses': self.extract_email_addresses(message_content),
            'sender': message_content.get('from'),
            'subject': message_content.get('subject'),
            'received_at': message_content.get('received_at'),
            'text_preview': message_content.get('text_content', '')[:200] if message_content.get('text_content') else '',
        }
        
        return parsed
    
    def wait_for_verification_code(self, timeout=60):
        """Wait for verification code in new messages"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.check_messages()
            
            for message in messages:
                content = self.get_message_content(message['id'])
                if content:
                    code = self.extract_verification_code(content)
                    if code:
                        return {
                            'type': 'verification_code',
                            'code': code,
                            'message': content,
                            'found_at': datetime.now().isoformat()
                        }
            
            time.sleep(2)  # Wait 2 seconds before checking again
        
        return None
    
    def wait_for_verification_link(self, timeout=60):
        """Wait for verification/confirmation links in new messages"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.check_messages()
            
            for message in messages:
                content = self.get_message_content(message['id'])
                if content:
                    links = self.extract_verification_links(content)
                    if links:
                        return {
                            'type': 'verification_link',
                            'links': links,
                            'primary_link': links[0],
                            'message': content,
                            'found_at': datetime.now().isoformat()
                        }
            
            time.sleep(2)
        
        return None
    
    def wait_for_any_verification(self, timeout=60):
        """Wait for any type of verification (code or link)"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.check_messages()
            
            for message in messages:
                content = self.get_message_content(message['id'])
                if content:
                    # Parse all content
                    parsed = self.parse_message_content(content)
                    
                    # Check for verification code
                    if parsed['verification_code']:
                        return {
                            'type': 'verification_code',
                            'code': parsed['verification_code'],
                            'parsed_content': parsed,
                            'found_at': datetime.now().isoformat()
                        }
                    
                    # Check for verification links
                    if parsed['verification_links']:
                        return {
                            'type': 'verification_link',
                            'links': parsed['verification_links'],
                            'primary_link': parsed['verification_links'][0],
                            'parsed_content': parsed,
                            'found_at': datetime.now().isoformat()
                        }
            
            time.sleep(2)
        
        return None
    
    def wait_for_new_email(self, timeout=60):
        """Wait for any new email and return full parsed content"""
        start_time = time.time()
        initial_count = len(self.check_messages())
        
        while time.time() - start_time < timeout:
            messages = self.check_messages()
            
            # Check if we have new messages
            if len(messages) > initial_count:
                # Get the latest message
                latest_message = messages[0]  # Most recent first
                content = self.get_message_content(latest_message['id'])
                if content:
                    parsed = self.parse_message_content(content)
                    return {
                        'type': 'new_email',
                        'parsed_content': parsed,
                        'raw_content': content,
                        'found_at': datetime.now().isoformat()
                    }
            
            time.sleep(2)
        
        return None
    
    def get_status(self):
        """Get current service status"""
        return {
            'current_email': self.current_email,
            'authenticated': bool(self.auth_token),
            'service_status': 'active',
            'timestamp': datetime.now().isoformat()
        }
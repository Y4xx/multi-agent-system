"""
Google OAuth 2.0 Service for Gmail API integration.
Handles OAuth flow and Gmail API authentication.
"""

import os
import json
import base64
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)


class GoogleOAuthService:
    """Service for managing Google OAuth and Gmail API."""
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    # Storage file for credentials
    CREDENTIALS_FILE = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data',
        'gmail_credentials.json'
    )
    
    def __init__(self):
        """Initialize the Google OAuth service."""
        self.client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')
        
    def get_authorization_url(self) -> Optional[str]:
        """
        Generate the Google OAuth authorization URL.
        
        Returns:
            Authorization URL or None if credentials not configured
        """
        if not self.client_id or not self.client_secret:
            return None
            
        try:
            # Create flow instance
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            # Generate authorization URL
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            return auth_url
            
        except Exception as e:
            logging.error(f"Error generating authorization URL: {str(e)}")
            return None
    
    def exchange_code_for_tokens(self, code: str) -> Dict:
        """
        Exchange authorization code for access tokens.
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            Dictionary with success status and user email
        """
        if not self.client_id or not self.client_secret:
            return {
                'success': False,
                'message': 'Google OAuth not configured'
            }
            
        try:
            # Create flow instance
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            # Exchange code for credentials
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Get user email from Gmail API
            try:
                service = build('gmail', 'v1', credentials=credentials)
                profile = service.users().getProfile(userId='me').execute()
                user_email = profile.get('emailAddress', '')
            except Exception as e:
                logging.warning(f"Error fetching user profile: {str(e)}")
                user_email = ''
            
            # Save credentials
            self._save_credentials(credentials, user_email)
            
            return {
                'success': True,
                'message': 'Gmail account connected successfully',
                'email': user_email
            }
            
        except Exception as e:
            logging.error(f"Error exchanging code for tokens: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to connect Gmail account'
            }
    
    def _save_credentials(self, credentials: Credentials, user_email: str):
        """
        Save credentials to file with secure permissions.
        
        Args:
            credentials: Google OAuth credentials
            user_email: User's email address
        """
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.CREDENTIALS_FILE), exist_ok=True)
            
            # Prepare credentials data
            creds_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None,
                'user_email': user_email,
                'connected_at': datetime.now().isoformat()
            }
            
            # Save to file with secure permissions
            with open(self.CREDENTIALS_FILE, 'w') as f:
                json.dump(creds_data, f, indent=2)
            
            # Set restrictive permissions (owner read/write only)
            os.chmod(self.CREDENTIALS_FILE, 0o600)
                
        except Exception as e:
            import logging
            logging.error(f"Error saving credentials: {str(e)}")
    
    def get_credentials(self) -> Optional[Credentials]:
        """
        Load saved credentials.
        
        Returns:
            Credentials object or None if not available
        """
        try:
            if not os.path.exists(self.CREDENTIALS_FILE):
                return None
                
            with open(self.CREDENTIALS_FILE, 'r') as f:
                creds_data = json.load(f)
            
            # Create credentials object
            credentials = Credentials(
                token=creds_data.get('token'),
                refresh_token=creds_data.get('refresh_token'),
                token_uri=creds_data.get('token_uri'),
                client_id=creds_data.get('client_id'),
                client_secret=creds_data.get('client_secret'),
                scopes=creds_data.get('scopes')
            )
            
            # Set expiry if available
            if creds_data.get('expiry'):
                credentials.expiry = datetime.fromisoformat(creds_data['expiry'])
            
            return credentials
            
        except Exception as e:
            logging.error(f"Error loading credentials: {str(e)}")
            return None
    
    def get_connection_status(self) -> Dict:
        """
        Check if Gmail is connected and get status.
        
        Returns:
            Dictionary with connection status and details
        """
        try:
            if not os.path.exists(self.CREDENTIALS_FILE):
                return {
                    'connected': False,
                    'message': 'Gmail not connected'
                }
            
            with open(self.CREDENTIALS_FILE, 'r') as f:
                creds_data = json.load(f)
            
            return {
                'connected': True,
                'email': creds_data.get('user_email', ''),
                'connected_at': creds_data.get('connected_at', ''),
                'message': 'Gmail connected successfully'
            }
            
        except Exception as e:
            logging.error(f"Error checking connection status: {str(e)}")
            return {
                'connected': False,
                'message': 'Error checking connection status'
            }
    
    def disconnect(self) -> Dict:
        """
        Disconnect Gmail account by removing saved credentials.
        
        Returns:
            Dictionary with success status
        """
        try:
            if os.path.exists(self.CREDENTIALS_FILE):
                os.remove(self.CREDENTIALS_FILE)
            
            return {
                'success': True,
                'message': 'Gmail account disconnected successfully'
            }
            
        except Exception as e:
            logging.error(f"Error disconnecting: {str(e)}")
            return {
                'success': False,
                'message': 'Error disconnecting Gmail account'
            }
    
    def send_email_via_gmail(
        self,
        recipient_email: str,
        subject: str,
        body: str
    ) -> Dict:
        """
        Send email using Gmail API.
        
        Args:
            recipient_email: Email address of the recipient
            subject: Email subject
            body: Email body (plain text or HTML)
            
        Returns:
            Dictionary with success status and message
        """
        try:
            # Get credentials
            credentials = self.get_credentials()
            if not credentials:
                return {
                    'success': False,
                    'message': 'Gmail not connected. Please connect your Gmail account first.'
                }
            
            # Build Gmail service
            service = build('gmail', 'v1', credentials=credentials)
            
            # Create message
            message = MIMEText(body)
            message['to'] = recipient_email
            message['subject'] = subject
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send message
            result = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'success': True,
                'message': f'Email sent successfully to {recipient_email}',
                'message_id': result.get('id')
            }
            
        except HttpError as e:
            logging.error(f"Gmail API error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to send email via Gmail API'
            }
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            return {
                'success': False,
                'message': 'Error sending email'
            }


# Singleton instance
google_oauth_service = GoogleOAuthService()

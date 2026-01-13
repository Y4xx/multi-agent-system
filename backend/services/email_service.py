import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        
        # Import Gmail service lazily to avoid circular imports
        self._google_oauth_service = None
        
        # Initialize OpenAI client for email content generation
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
            self.model = os.getenv('MODEL_NAME', 'gpt-4o-mini')
        else:
            self.openai_client = None
            self.model = None
    
    @property
    def google_oauth_service(self):
        """Lazy load Google OAuth service to avoid circular imports."""
        if self._google_oauth_service is None:
            from services.google_oauth_service import google_oauth_service
            self._google_oauth_service = google_oauth_service
        return self._google_oauth_service
    
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> dict:
        """
        Send an email to a recipient.
        Prioritizes Gmail API if connected, falls back to SMTP.
        
        Args:
            recipient_email: Email address of the recipient
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            
        Returns:
            Dictionary with success status and message
        """
        try:
            # Try Gmail API first if connected
            gmail_status = self.google_oauth_service.get_connection_status()
            if gmail_status.get('connected'):
                result = self.google_oauth_service.send_email_via_gmail(
                    recipient_email=recipient_email,
                    subject=subject,
                    body=html_body if html_body else body
                )
                if result.get('success'):
                    return result
                # If Gmail API fails, fall through to SMTP
                print(f"Gmail API failed, falling back to SMTP: {result.get('message')}")
            
            # For demo purposes, if credentials are not set, simulate sending
            if not self.sender_email or not self.sender_password:
                return {
                    'success': True,
                    'message': f'Email simulated (no credentials set). Would send to: {recipient_email}',
                    'details': {
                        'to': recipient_email,
                        'subject': subject,
                        'preview': body[:100] + '...' if len(body) > 100 else body
                    }
                }
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = recipient_email
            
            # Add plain text part
            part1 = MIMEText(body, 'plain')
            message.attach(part1)
            
            # Add HTML part if provided
            if html_body:
                part2 = MIMEText(html_body, 'html')
                message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return {
                'success': True,
                'message': f'Email sent successfully to {recipient_email}'
            }
            
        except Exception as e:
            # Log error for debugging
            print(f"Email send error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to send email. Please check your email configuration.'
            }
    
    def send_job_application(
        self,
        recipient_email: str,
        job_title: str,
        company: str,
        applicant_name: str,
        motivation_letter: str,
        cv_text: Optional[str] = None,
        include_ai_attribution: bool = False
    ) -> dict:
        """
        Send a job application email with AI-generated content formatting.
        
        Args:
            recipient_email: Email of the hiring manager/HR
            job_title: Title of the job position
            company: Company name
            applicant_name: Name of the applicant
            motivation_letter: The motivation letter content
            cv_text: Optional CV text
            include_ai_attribution: Whether to include AI attribution in footer (default: False)
            
        Returns:
            Dictionary with success status and message
        """
        subject = f"Application for {job_title} position at {company}"
        
        # Use OpenAI to generate professional email body if available
        if self.openai_client:
            try:
                body = self._generate_email_body_with_ai(
                    job_title, company, applicant_name, motivation_letter
                )
            except Exception as e:
                print(f"Error generating email with OpenAI: {str(e)}")
                # Fallback to simple template
                body = self._generate_simple_email_body(
                    applicant_name, motivation_letter
                )
        else:
            # Fallback to simple template
            body = self._generate_simple_email_body(
                applicant_name, motivation_letter
            )
        
        # Generate HTML version using OpenAI if available
        if self.openai_client:
            try:
                html_body = self._generate_html_email_with_ai(
                    job_title, company, applicant_name, motivation_letter, include_ai_attribution
                )
            except Exception as e:
                print(f"Error generating HTML email with OpenAI: {str(e)}")
                # Fallback to simple HTML template
                html_body = self._generate_simple_html_body(
                    job_title, company, applicant_name, motivation_letter, include_ai_attribution
                )
        else:
            # Fallback to simple HTML template
            html_body = self._generate_simple_html_body(
                job_title, company, applicant_name, motivation_letter, include_ai_attribution
            )
        
        return self.send_email(recipient_email, subject, body, html_body)
    
    def _generate_email_body_with_ai(
        self,
        job_title: str,
        company: str,
        applicant_name: str,
        motivation_letter: str
    ) -> str:
        """Generate professional email body using OpenAI."""
        prompt = f"""Create a professional job application email body for the following:

Job Title: {job_title}
Company: {company}
Applicant Name: {applicant_name}

Motivation Letter Content:
{motivation_letter}

Instructions:
1. Format the email professionally with proper greeting
2. Keep the motivation letter content intact but format it nicely
3. Add a brief professional closing
4. Make it concise and well-structured
5. Plain text format only

Write the complete email body:"""
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional email formatting assistant. You create well-structured, professional job application emails."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=600
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_html_email_with_ai(
        self,
        job_title: str,
        company: str,
        applicant_name: str,
        motivation_letter: str,
        include_ai_attribution: bool
    ) -> str:
        """Generate HTML email using OpenAI."""
        footer_instruction = ""
        if include_ai_attribution:
            footer_instruction = "Include a small footer mentioning this was generated using an AI-powered system."
        
        prompt = f"""Create a professional HTML email for a job application with the following details:

Job Title: {job_title}
Company: {company}
Applicant Name: {applicant_name}

Motivation Letter:
{motivation_letter}

Instructions:
1. Create a beautiful, professional HTML email layout
2. Use modern, clean styling with good typography
3. Include proper header with job title and company
4. Format the motivation letter content nicely
5. Add professional signature section
6. Use a color scheme with blues (#0066cc) for headers
7. Make it responsive and email-client compatible
{footer_instruction}
8. Keep formatting simple and professional

Return only the complete HTML (including <html>, <head>, <body> tags):"""
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert email designer who creates professional, beautiful HTML emails for job applications."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_simple_email_body(
        self,
        applicant_name: str,
        motivation_letter: str
    ) -> str:
        """Generate simple email body as fallback."""
        body = f"""Dear Hiring Manager,

{motivation_letter}

Best regards,
{applicant_name}
"""
        return body
    
    def _generate_simple_html_body(
        self,
        job_title: str,
        company: str,
        applicant_name: str,
        motivation_letter: str,
        include_ai_attribution: bool
    ) -> str:
        """Generate simple HTML email as fallback."""
        footer_content = ""
        if include_ai_attribution:
            footer_content = "<p>This application was generated using an AI-powered job application system.</p>"
        
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial', 'Helvetica', sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        border-bottom: 2px solid #0066cc;
                        padding-bottom: 10px;
                        margin-bottom: 20px;
                    }}
                    .content {{
                        white-space: pre-wrap;
                        margin: 20px 0;
                    }}
                    .signature {{
                        margin-top: 30px;
                        font-weight: 500;
                    }}
                    .footer {{
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2 style="color: #0066cc; margin: 0;">Application for {job_title}</h2>
                    <p style="color: #666; margin: 5px 0 0 0;">{company}</p>
                </div>
                <p>Dear Hiring Manager,</p>
                <div class="content">{motivation_letter}</div>
                <div class="signature">
                    <p>Best regards,<br>{applicant_name}</p>
                </div>
                {f'<div class="footer">{footer_content}</div>' if footer_content else ''}
            </body>
        </html>
        """
        return html_body

# Singleton instance
email_service = EmailService()

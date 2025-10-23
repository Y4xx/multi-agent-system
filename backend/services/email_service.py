import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
    
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> dict:
        """
        Send an email to a recipient.
        
        Args:
            recipient_email: Email address of the recipient
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            
        Returns:
            Dictionary with success status and message
        """
        try:
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
            return {
                'success': False,
                'message': f'Failed to send email: {str(e)}'
            }
    
    def send_job_application(
        self,
        recipient_email: str,
        job_title: str,
        company: str,
        applicant_name: str,
        motivation_letter: str,
        cv_text: Optional[str] = None
    ) -> dict:
        """
        Send a job application email.
        
        Args:
            recipient_email: Email of the hiring manager/HR
            job_title: Title of the job position
            company: Company name
            applicant_name: Name of the applicant
            motivation_letter: The motivation letter content
            cv_text: Optional CV text
            
        Returns:
            Dictionary with success status and message
        """
        subject = f"Application for {job_title} position at {company}"
        
        body = f"""Dear Hiring Manager,

{motivation_letter}

Best regards,
{applicant_name}
"""
        
        html_body = f"""
        <html>
            <body>
                <p>Dear Hiring Manager,</p>
                <div style="white-space: pre-wrap;">{motivation_letter}</div>
                <p>Best regards,<br>{applicant_name}</p>
            </body>
        </html>
        """
        
        return self.send_email(recipient_email, subject, body, html_body)

# Singleton instance
email_service = EmailService()

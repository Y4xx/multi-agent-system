import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
import os
from dotenv import load_dotenv
import openai
from openai import OpenAI
from services.utils import get_mime_type

load_dotenv()

# Get logger (don't configure at module level)
logger = logging.getLogger(__name__)

class EmailService:
    # Email body template constant
    EMAIL_BODY_TEMPLATE = """Madame, Monsieur,

Je vous adresse ma candidature pour le poste de {job_title} au sein de {company}.

Vous trouverez ci-joint mon CV ainsi que ma lettre de motivation détaillant mon parcours et mes motivations pour ce poste.

Je reste à votre disposition pour un entretien afin de discuter de ma candidature.

Cordialement,
{applicant_name}
{applicant_email}
{applicant_phone}"""
    
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
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> dict:
        """
        Send an email to a recipient.
        Prioritizes Gmail API if connected, falls back to SMTP.
        
        Args:
            recipient_email: Email address of the recipient
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            attachments: Optional list of file paths to attach
            
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
                    body=html_body if html_body else body,
                    attachments=attachments
                )
                if result.get('success'):
                    return result
                # If Gmail API fails, fall through to SMTP
                print(f"Gmail API failed, falling back to SMTP: {result.get('message')}")
            
            # For demo purposes, if credentials are not set, simulate sending
            if not self.sender_email or not self.sender_password:
                attachment_info = ""
                attachment_names = []
                if attachments:
                    attachment_names = [os.path.basename(f) for f in attachments]
                    attachment_info = f", Attachments: {', '.join(attachment_names)}"
                return {
                    'success': True,
                    'message': f'Email simulated (no credentials set). Would send to: {recipient_email}{attachment_info}',
                    'details': {
                        'to': recipient_email,
                        'subject': subject,
                        'preview': body[:100] + '...' if len(body) > 100 else body,
                        'attachments': attachment_names
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
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        try:
                            # Get MIME type dynamically
                            mime_type = get_mime_type(file_path)
                            if '/' in mime_type:
                                main_type, sub_type = mime_type.split('/', 1)
                            else:
                                # Fallback to octet-stream if invalid MIME type
                                main_type, sub_type = 'application', 'octet-stream'
                            
                            with open(file_path, 'rb') as f:
                                part = MIMEBase(main_type, sub_type)
                                part.set_payload(f.read())
                                encoders.encode_base64(part)
                                part.add_header(
                                    'Content-Disposition',
                                    f'attachment; filename={os.path.basename(file_path)}'
                                )
                                message.attach(part)
                        except (OSError, IOError) as e:
                            logger.error(f"Error attaching file {file_path}: {str(e)}")
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return {
                'success': True,
                'message': f'Email sent successfully to {recipient_email}'
            }
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to send email. Please check your email configuration.'
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to send email. Please check your email configuration.'
            }
    
    def _generate_ai_subject(
        self,
        job_title: str,
        company: str,
        applicant_name: str
    ) -> str:
        """
        Generate a professional, personalized email subject using AI.
        
        Args:
            job_title: Title of the job position
            company: Company name
            applicant_name: Name of the applicant
            
        Returns:
            Generated subject line
        """
        if not self.openai_client:
            # Fallback to template if OpenAI not available
            return f"Candidature de {applicant_name} pour le poste de {job_title} - {company}"
        
        try:
            prompt = f"""Generate a professional French email subject line for a job application.

Job Title: {job_title}
Company: {company}
Applicant Name: {applicant_name}

Requirements:
- Use the format: "Candidature de [Nom Prénom] pour le poste de [Titre] - [Entreprise]"
- Keep it professional and concise
- Return ONLY the subject line, no quotes or extra text

Subject line:"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional email subject line generator. Generate only the subject line, nothing else."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            subject = response.choices[0].message.content.strip()
            # Remove quotes if present
            subject = subject.strip('"').strip("'")
            return subject
            
        except openai.OpenAIError as e:
            logger.warning(f"OpenAI error generating subject: {str(e)}")
            return f"Candidature de {applicant_name} pour le poste de {job_title} - {company}"
        except Exception as e:
            logger.error(f"Unexpected error generating AI subject: {str(e)}")
            return f"Candidature de {applicant_name} pour le poste de {job_title} - {company}"
    
    def _generate_fallback_email_body(
        self,
        job_title: str,
        company: str,
        applicant_name: str,
        applicant_email: str,
        applicant_phone: str
    ) -> str:
        """Generate fallback email body using template."""
        return self.EMAIL_BODY_TEMPLATE.format(
            job_title=job_title,
            company=company,
            applicant_name=applicant_name,
            applicant_email=applicant_email,
            applicant_phone=applicant_phone if applicant_phone else ''
        )
    
    def _generate_ai_email_body(
        self,
        job_title: str,
        company: str,
        applicant_name: str,
        applicant_email: str,
        applicant_phone: str
    ) -> str:
        """
        Generate a professional French email body using AI.
        
        Args:
            job_title: Title of the job position
            company: Company name
            applicant_name: Name of the applicant
            applicant_email: Email of the applicant
            applicant_phone: Phone number of the applicant
            
        Returns:
            Generated email body in French
        """
        if not self.openai_client:
            # Use template fallback
            return self._generate_fallback_email_body(
                job_title, company, applicant_name, applicant_email, applicant_phone
            )
        
        try:
            prompt = f"""Generate a professional French email body for a job application.

Job Title: {job_title}
Company: {company}
Applicant Name: {applicant_name}
Applicant Email: {applicant_email}
Applicant Phone: {applicant_phone if applicant_phone else 'Not provided'}

Requirements:
1. Professional greeting (Madame, Monsieur,)
2. Brief introduction (1-2 sentences) stating the application for the position
3. Reference to attached documents (CV + lettre de motivation)
4. Call to action (request for interview/meeting)
5. Professional closing (Cordialement,)
6. Signature with name, email, and phone (if provided)
7. Keep it concise (8-10 lines maximum)
8. Professional but warm tone
9. Return ONLY the email body, no subject line

Email body:"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional French email writer. Generate professional, concise job application emails in French."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=400
            )
            
            body = response.choices[0].message.content.strip()
            return body
            
        except openai.OpenAIError as e:
            logger.warning(f"OpenAI error generating email body: {str(e)}")
            return self._generate_fallback_email_body(
                job_title, company, applicant_name, applicant_email, applicant_phone
            )
        except Exception as e:
            logger.error(f"Unexpected error generating AI email body: {str(e)}")
            return self._generate_fallback_email_body(
                job_title, company, applicant_name, applicant_email, applicant_phone
            )
    
    def send_job_application(
        self,
        recipient_email: str,
        job_title: str,
        company: str,
        applicant_name: str,
        motivation_letter: str,
        cv_text: Optional[str] = None,
        include_ai_attribution: bool = False,
        applicant_email: str = "",
        applicant_phone: str = "",
        cv_path: Optional[str] = None,
        motivation_letter_path: Optional[str] = None
    ) -> dict:
        """
        Send a job application email with AI-generated content and PDF attachments.
        
        Args:
            recipient_email: Email of the hiring manager/HR
            job_title: Title of the job position
            company: Company name
            applicant_name: Name of the applicant
            motivation_letter: The motivation letter content
            cv_text: Optional CV text
            include_ai_attribution: Whether to include AI attribution in footer (default: False)
            applicant_email: Email of the applicant
            applicant_phone: Phone of the applicant
            cv_path: Optional path to CV PDF file
            motivation_letter_path: Optional path to motivation letter PDF file
            
        Returns:
            Dictionary with success status and message
        """
        # Generate AI-powered subject line
        subject = self._generate_ai_subject(job_title, company, applicant_name)
        
        # Generate AI-powered email body in French
        body = self._generate_ai_email_body(
            job_title, company, applicant_name, applicant_email, applicant_phone
        )
        
        # Prepare attachments list with validation
        attachments = []
        
        # Validate CV attachment
        if cv_path:
            if os.path.exists(cv_path):
                if os.path.isfile(cv_path) and os.access(cv_path, os.R_OK):
                    attachments.append(cv_path)
                    logger.info(f"CV file attached: {os.path.basename(cv_path)}")
                else:
                    logger.warning(f"CV file exists but is not readable: {cv_path}")
            else:
                logger.warning(f"CV file not found: {cv_path}")
        else:
            logger.warning("No CV path provided for job application")
        
        # Validate motivation letter attachment
        if motivation_letter_path:
            if os.path.exists(motivation_letter_path):
                if os.path.isfile(motivation_letter_path) and os.access(motivation_letter_path, os.R_OK):
                    attachments.append(motivation_letter_path)
                    logger.info(f"Motivation letter attached: {os.path.basename(motivation_letter_path)}")
                else:
                    logger.warning(f"Motivation letter exists but is not readable: {motivation_letter_path}")
            else:
                logger.warning(f"Motivation letter not found: {motivation_letter_path}")
        
        # Verify we have at least one attachment
        if not attachments:
            logger.error("No valid attachments found for job application")
            return {
                'success': False,
                'message': 'Cannot send application: No valid attachments found (CV or motivation letter)'
            }
        
        # Generate HTML version for better formatting
        html_body = self._generate_html_email_for_application(
            body, job_title, company, include_ai_attribution
        )
        
        return self.send_email(recipient_email, subject, body, html_body, attachments)
    
    def _generate_html_email_for_application(
        self,
        body: str,
        job_title: str,
        company: str,
        include_ai_attribution: bool
    ) -> str:
        """
        Generate simple HTML email for application.
        
        Args:
            body: Plain text email body
            job_title: Job title
            company: Company name
            include_ai_attribution: Whether to include AI attribution
            
        Returns:
            HTML email body
        """
        footer_content = ""
        if include_ai_attribution:
            footer_content = "<p style='font-size: 11px; color: #999;'>Cette candidature a été générée avec un système d'IA.</p>"
        
        # Convert line breaks to <br> tags
        html_content = body.replace('\n\n', '<br><br>').replace('\n', '<br>')
        
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
                        margin: 20px 0;
                    }}
                    .footer {{
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2 style="color: #0066cc; margin: 0;">Candidature - {job_title}</h2>
                    <p style="color: #666; margin: 5px 0 0 0;">{company}</p>
                </div>
                <div class="content">
                    {html_content}
                </div>
                {f'<div class="footer">{footer_content}</div>' if footer_content else ''}
            </body>
        </html>
        """
        return html_body
    
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

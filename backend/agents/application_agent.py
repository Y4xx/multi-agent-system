from typing import Dict, List
from services.email_service import email_service
from services.utils import get_job_field

class ApplicationAgent:
    """
    Agent responsible for sending job application emails.
    """
    
    def __init__(self):
        self.name = "Application Agent"
        self.applications_log = []
    
    def send_application(
        self,
        cv_data: Dict,
        job_data: Dict,
        motivation_letter: str
    ) -> Dict:
        """
        Send a job application via email.
        
        Args:
            cv_data: Parsed CV data
            job_data: Job offer data
            motivation_letter: The motivation letter content
            
        Returns:
            Dictionary with application status and details
        """
        applicant_name = cv_data.get('name', 'Applicant')
        applicant_email = cv_data.get('email', '')
        
        # Use format-agnostic field extraction
        recipient_email = get_job_field(job_data, 'application_email')
        job_title = get_job_field(job_data, 'title')
        company = get_job_field(job_data, 'company')
        job_id = job_data.get('id')
        
        if not recipient_email:
            return {
                'success': False,
                'message': 'No application email found for this job offer',
                'job_id': job_id,
                'job_title': job_title
            }
        
        # Send the email
        result = email_service.send_job_application(
            recipient_email=recipient_email,
            job_title=job_title,
            company=company,
            applicant_name=applicant_name,
            motivation_letter=motivation_letter
        )
        
        # Log the application
        application_record = {
            'applicant_name': applicant_name,
            'applicant_email': applicant_email,
            'job_id': job_id,
            'job_title': job_title,
            'company': company,
            'recipient_email': recipient_email,
            'status': 'sent' if result['success'] else 'failed',
            'timestamp': self._get_timestamp(),
            'details': result
        }
        
        self.applications_log.append(application_record)
        
        return {
            'success': result['success'],
            'message': result['message'],
            'job_id': job_id,
            'job_title': job_title,
            'company': company,
            'recipient_email': recipient_email
        }
    
    def send_bulk_applications(
        self,
        cv_data: Dict,
        applications: List[Dict]
    ) -> List[Dict]:
        """
        Send multiple job applications at once.
        
        Args:
            cv_data: Parsed CV data
            applications: List of dicts containing job_data and motivation_letter
            
        Returns:
            List of application results
        """
        results = []
        
        for app in applications:
            job_data = app.get('job_data')
            motivation_letter = app.get('motivation_letter')
            
            if not job_data or not motivation_letter:
                results.append({
                    'success': False,
                    'message': 'Missing job data or motivation letter',
                    'job_id': None
                })
                continue
            
            result = self.send_application(cv_data, job_data, motivation_letter)
            results.append(result)
        
        return results
    
    def get_application_status(self, job_id: int) -> Dict:
        """
        Get the status of a specific application.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Application status dictionary
        """
        for app in reversed(self.applications_log):
            if app.get('job_id') == job_id:
                return app
        
        return {
            'found': False,
            'message': 'No application found for this job ID'
        }
    
    def get_all_applications(self) -> List[Dict]:
        """
        Get all application records.
        
        Returns:
            List of all application records
        """
        return self.applications_log
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

# Singleton instance
application_agent = ApplicationAgent()

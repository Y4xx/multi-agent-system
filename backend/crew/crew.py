"""
CrewAI Crew Setup.
Orchestrates agents and tasks for the job application workflow.
"""

from crewai import Crew, Process
from typing import Dict, List, Optional
from crew.agents import (
    create_cv_analysis_agent,
    create_job_fetcher_agent,
    create_matching_agent,
    create_cover_letter_agent,
    create_application_agent,
    create_coordinator_agent
)
from crew.tasks import (
    create_cv_parsing_task,
    create_job_fetching_task,
    create_matching_task,
    create_cover_letter_task,
    create_application_task
)

# Import legacy services for actual data operations
from agents.cv_analysis_agent import cv_analysis_agent as legacy_cv_agent
from agents.job_fetcher_agent import job_fetcher_agent as legacy_job_agent
from agents.matching_agent import matching_agent as legacy_matching_agent
from services.email_service import email_service


class JobApplicationCrew:
    """
    Main crew for job application workflow.
    Combines CrewAI agents with legacy services for actual operations.
    """
    
    def __init__(self):
        """Initialize the crew with all agents."""
        self.cv_agent = create_cv_analysis_agent()
        self.job_agent = create_job_fetcher_agent()
        self.matching_agent = create_matching_agent()
        self.cover_letter_agent = create_cover_letter_agent()
        self.application_agent = create_application_agent()
        self.coordinator_agent = create_coordinator_agent()
    
    def analyze_cv(self, cv_text: str) -> Dict:
        """
        Analyze CV using legacy service (for reliability).
        
        Args:
            cv_text: CV text content
            
        Returns:
            Parsed CV data
        """
        # Use legacy CV analysis for actual parsing (more reliable)
        cv_data = legacy_cv_agent.analyze_cv(cv_text)
        return cv_data
    
    def analyze_cv_file(self, filepath: str) -> Dict:
        """
        Analyze CV file using legacy service.
        
        Args:
            filepath: Path to CV file
            
        Returns:
            Parsed CV data
        """
        cv_data = legacy_cv_agent.analyze_cv_file(filepath)
        return cv_data
    
    def fetch_jobs(self, job_type: Optional[str] = None, 
                   location: Optional[str] = None,
                   keyword: Optional[str] = None) -> List[Dict]:
        """
        Fetch jobs using legacy service.
        
        Args:
            job_type: Filter by job type
            location: Filter by location
            keyword: Filter by keyword
            
        Returns:
            List of job offers
        """
        if job_type:
            return legacy_job_agent.fetch_jobs_by_type(job_type)
        elif location:
            return legacy_job_agent.fetch_jobs_by_location(location)
        elif keyword:
            return legacy_job_agent.fetch_jobs_by_keyword(keyword)
        else:
            return legacy_job_agent.fetch_all_jobs()
    
    def match_jobs(self, cv_data: Dict, jobs: List[Dict], top_n: int = 10) -> List[Dict]:
        """
        Match jobs with CV using legacy service.
        
        Args:
            cv_data: Parsed CV data
            jobs: List of job offers
            top_n: Number of top matches to return
            
        Returns:
            Ranked job offers with match scores
        """
        return legacy_matching_agent.match_cv_with_jobs(cv_data, jobs, top_n)
    
    def generate_cover_letter(self, cv_data: Dict, job_data: Dict, 
                            custom_message: str = "") -> str:
        """
        Generate cover letter using CrewAI LLM agent.
        
        Args:
            cv_data: Parsed CV data
            job_data: Job offer data
            custom_message: Optional custom message
            
        Returns:
            Generated cover letter in French
        """
        # Create the cover letter task
        task = create_cover_letter_task(
            self.cover_letter_agent,
            cv_data,
            job_data,
            custom_message
        )
        
        # Create a crew for this specific task
        crew = Crew(
            agents=[self.cover_letter_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute and get the result
        result = crew.kickoff()
        
        # Extract the letter from the result
        if hasattr(result, 'raw'):
            return result.raw
        elif isinstance(result, str):
            return result
        else:
            return str(result)
    
    def submit_application(self, cv_data: Dict, job_data: Dict, 
                          motivation_letter: str) -> Dict:
        """
        Submit application using legacy email service.
        
        Args:
            cv_data: Parsed CV data
            job_data: Job offer data
            motivation_letter: The motivation letter
            
        Returns:
            Application submission result
        """
        applicant_name = cv_data.get('name', 'Applicant')
        recipient_email = job_data.get('application_email', '')
        job_title = job_data.get('title', '')
        company = job_data.get('company', '')
        
        if not recipient_email:
            return {
                'success': False,
                'message': 'No application email found for this job offer',
                'job_id': job_data.get('id'),
                'job_title': job_title
            }
        
        # Send the email using legacy service
        result = email_service.send_job_application(
            recipient_email=recipient_email,
            job_title=job_title,
            company=company,
            applicant_name=applicant_name,
            motivation_letter=motivation_letter
        )
        
        return {
            'success': result['success'],
            'message': result['message'],
            'job_id': job_data.get('id'),
            'job_title': job_title,
            'company': company,
            'recipient_email': recipient_email
        }
    
    def get_job_recommendations(self, cv_data: Dict, 
                               job_type: Optional[str] = None,
                               location: Optional[str] = None,
                               top_n: int = 10) -> List[Dict]:
        """
        Get job recommendations for a CV.
        
        Args:
            cv_data: Parsed CV data
            job_type: Optional job type filter
            location: Optional location filter
            top_n: Number of recommendations
            
        Returns:
            List of recommended jobs with match scores
        """
        # Fetch jobs
        jobs = self.fetch_jobs(job_type=job_type, location=location)
        
        # Match and rank
        matched_jobs = self.match_jobs(cv_data, jobs, top_n)
        
        return matched_jobs
    
    def generate_application_package(self, cv_data: Dict, job_id: int,
                                    custom_message: str = "") -> Dict:
        """
        Generate complete application package for a job.
        
        Args:
            cv_data: Parsed CV data
            job_id: ID of the job
            custom_message: Optional custom message
            
        Returns:
            Application package with job data, letter, and match explanation
        """
        # Get job data
        job_data = legacy_job_agent.get_job_by_id(job_id)
        
        if not job_data:
            return {
                'success': False,
                'message': f'Job with ID {job_id} not found'
            }
        
        # Generate motivation letter using CrewAI
        motivation_letter = self.generate_cover_letter(
            cv_data, job_data, custom_message
        )
        
        # Get match explanation
        match_explanation = legacy_matching_agent.explain_match(cv_data, job_data)
        
        return {
            'success': True,
            'job_data': job_data,
            'motivation_letter': motivation_letter,
            'match_explanation': match_explanation
        }


# Singleton instance
job_application_crew = JobApplicationCrew()

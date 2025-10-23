from typing import Dict, List, Optional
from agents.cv_analysis_agent import cv_analysis_agent
from agents.job_fetcher_agent import job_fetcher_agent
from agents.matching_agent import matching_agent
from agents.motivation_agent import motivation_agent
from agents.application_agent import application_agent

class CoordinatorAgent:
    """
    Coordinator agent that orchestrates the workflow between all other agents.
    """
    
    def __init__(self):
        self.name = "Coordinator Agent"
        self.cv_analysis = cv_analysis_agent
        self.job_fetcher = job_fetcher_agent
        self.matching = matching_agent
        self.motivation = motivation_agent
        self.application = application_agent
    
    def process_cv_upload(self, cv_content: str) -> Dict:
        """
        Process a CV upload and return parsed data.
        
        Args:
            cv_content: Raw CV text content
            
        Returns:
            Parsed CV data
        """
        return self.cv_analysis.analyze_cv(cv_content)
    
    def process_cv_file(self, cv_filepath: str) -> Dict:
        """
        Process a CV file and return parsed data.
        
        Args:
            cv_filepath: Path to CV file
            
        Returns:
            Parsed CV data
        """
        return self.cv_analysis.analyze_cv_file(cv_filepath)
    
    def get_job_recommendations(
        self,
        cv_data: Dict,
        job_type: Optional[str] = None,
        location: Optional[str] = None,
        top_n: int = 10
    ) -> List[Dict]:
        """
        Get job recommendations based on CV.
        
        Args:
            cv_data: Parsed CV data
            job_type: Optional filter for job type
            location: Optional filter for location
            top_n: Number of recommendations to return
            
        Returns:
            List of recommended jobs with match scores
        """
        # Fetch jobs based on filters
        if job_type:
            jobs = self.job_fetcher.fetch_jobs_by_type(job_type)
        elif location:
            jobs = self.job_fetcher.fetch_jobs_by_location(location)
        else:
            jobs = self.job_fetcher.fetch_all_jobs()
        
        # Match and rank jobs
        matched_jobs = self.matching.match_cv_with_jobs(cv_data, jobs, top_n)
        
        return matched_jobs
    
    def generate_application_package(
        self,
        cv_data: Dict,
        job_id: int,
        custom_message: str = ""
    ) -> Dict:
        """
        Generate a complete application package for a specific job.
        
        Args:
            cv_data: Parsed CV data
            job_id: ID of the job to apply for
            custom_message: Optional custom message for the motivation letter
            
        Returns:
            Dictionary containing job data, motivation letter, and match explanation
        """
        # Get job data
        job_data = self.job_fetcher.get_job_by_id(job_id)
        
        if not job_data:
            return {
                'success': False,
                'message': f'Job with ID {job_id} not found'
            }
        
        # Generate motivation letter
        motivation_letter = self.motivation.generate_motivation_letter(
            cv_data, job_data, custom_message
        )
        
        # Get match explanation
        match_explanation = self.matching.explain_match(cv_data, job_data)
        
        return {
            'success': True,
            'job_data': job_data,
            'motivation_letter': motivation_letter,
            'match_explanation': match_explanation
        }
    
    def submit_application(
        self,
        cv_data: Dict,
        job_id: int,
        motivation_letter: str
    ) -> Dict:
        """
        Submit a job application.
        
        Args:
            cv_data: Parsed CV data
            job_id: ID of the job to apply for
            motivation_letter: The motivation letter to send
            
        Returns:
            Application submission result
        """
        # Get job data
        job_data = self.job_fetcher.get_job_by_id(job_id)
        
        if not job_data:
            return {
                'success': False,
                'message': f'Job with ID {job_id} not found'
            }
        
        # Send application
        result = self.application.send_application(cv_data, job_data, motivation_letter)
        
        return result
    
    def process_full_workflow(
        self,
        cv_filepath: str,
        job_preferences: Dict = None,
        auto_apply: bool = False
    ) -> Dict:
        """
        Process the complete workflow from CV upload to job recommendations.
        
        Args:
            cv_filepath: Path to CV file
            job_preferences: Optional dictionary with job preferences (type, location, etc.)
            auto_apply: Whether to automatically apply to top matches
            
        Returns:
            Complete workflow results
        """
        if job_preferences is None:
            job_preferences = {}
        
        # Step 1: Parse CV
        cv_data = self.process_cv_file(cv_filepath)
        
        # Step 2: Get job recommendations
        job_type = job_preferences.get('type')
        location = job_preferences.get('location')
        top_n = job_preferences.get('top_n', 10)
        
        recommended_jobs = self.get_job_recommendations(
            cv_data, job_type, location, top_n
        )
        
        # Step 3: Optionally auto-apply to top matches
        applications = []
        if auto_apply and recommended_jobs:
            top_matches = recommended_jobs[:3]  # Apply to top 3
            
            for job in top_matches:
                # Generate motivation letter
                motivation_letter = self.motivation.generate_motivation_letter(
                    cv_data, job
                )
                
                # Send application
                result = self.application.send_application(
                    cv_data, job, motivation_letter
                )
                
                applications.append(result)
        
        return {
            'cv_data': cv_data,
            'recommended_jobs': recommended_jobs,
            'applications': applications if auto_apply else []
        }

# Singleton instance
coordinator_agent = CoordinatorAgent()

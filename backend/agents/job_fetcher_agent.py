import json
import os
from typing import List, Dict, Optional

class JobFetcherAgent:
    """
    Agent responsible for fetching job offers from various sources.
    """
    
    def __init__(self):
        self.name = "Job Fetcher Agent"
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    def fetch_all_jobs(self) -> List[Dict]:
        """
        Fetch all available job offers.
        
        Returns:
            List of job offer dictionaries
        """
        job_offers_path = os.path.join(self.data_dir, 'job_offers.json')
        
        try:
            with open(job_offers_path, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
            return jobs
        except Exception as e:
            print(f"Error loading job offers: {str(e)}")
            return []
    
    def fetch_jobs_by_type(self, job_type: str) -> List[Dict]:
        """
        Fetch jobs filtered by type (Full-time, Internship, etc.).
        
        Args:
            job_type: Type of job to filter by
            
        Returns:
            List of filtered job offers
        """
        all_jobs = self.fetch_all_jobs()
        return [job for job in all_jobs if job.get('type', '').lower() == job_type.lower()]
    
    def fetch_jobs_by_location(self, location: str) -> List[Dict]:
        """
        Fetch jobs filtered by location.
        
        Args:
            location: Location to filter by
            
        Returns:
            List of filtered job offers
        """
        all_jobs = self.fetch_all_jobs()
        return [job for job in all_jobs if location.lower() in job.get('location', '').lower()]
    
    def fetch_jobs_by_keyword(self, keyword: str) -> List[Dict]:
        """
        Fetch jobs that match a keyword in title or description.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching job offers
        """
        all_jobs = self.fetch_all_jobs()
        keyword_lower = keyword.lower()
        
        matching_jobs = []
        for job in all_jobs:
            title = job.get('title', '').lower()
            description = job.get('description', '').lower()
            requirements = ' '.join(job.get('requirements', [])).lower()
            
            if keyword_lower in title or keyword_lower in description or keyword_lower in requirements:
                matching_jobs.append(job)
        
        return matching_jobs
    
    def get_job_by_id(self, job_id: int) -> Optional[Dict]:
        """
        Get a specific job by ID.
        
        Args:
            job_id: ID of the job to retrieve
            
        Returns:
            Job offer dictionary or None if not found
        """
        all_jobs = self.fetch_all_jobs()
        for job in all_jobs:
            if job.get('id') == job_id:
                return job
        return None
    
    def add_job_offer(self, job_data: Dict) -> bool:
        """
        Add a new job offer to the database.
        
        Args:
            job_data: Dictionary containing job offer data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            all_jobs = self.fetch_all_jobs()
            
            # Generate new ID
            max_id = max([job.get('id', 0) for job in all_jobs]) if all_jobs else 0
            job_data['id'] = max_id + 1
            
            # Add to list
            all_jobs.append(job_data)
            
            # Save back to file
            job_offers_path = os.path.join(self.data_dir, 'job_offers.json')
            with open(job_offers_path, 'w', encoding='utf-8') as f:
                json.dump(all_jobs, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error adding job offer: {str(e)}")
            return False

# Singleton instance
job_fetcher_agent = JobFetcherAgent()

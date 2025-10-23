from typing import List, Dict, Tuple
from services.nlp_service import nlp_service
from services.utils import create_cv_summary, create_job_summary, calculate_match_score

class MatchingAgent:
    """
    Agent responsible for matching CVs with job offers based on similarity.
    """
    
    def __init__(self):
        self.name = "Matching Agent"
    
    def match_cv_with_jobs(
        self,
        cv_data: Dict,
        job_offers: List[Dict],
        top_n: int = 10
    ) -> List[Dict]:
        """
        Match a CV with job offers and return top N matches.
        
        Args:
            cv_data: Parsed CV data
            job_offers: List of job offers
            top_n: Number of top matches to return
            
        Returns:
            List of job offers with match scores, sorted by score (highest first)
        """
        # Create CV summary for comparison
        cv_summary = create_cv_summary(cv_data)
        if not cv_summary.strip():
            cv_summary = cv_data.get('raw_text', '')
        
        matches = []
        
        for job in job_offers:
            # Create job summary
            job_summary = create_job_summary(job)
            
            # Compute similarity
            similarity_score = nlp_service.compute_similarity(cv_summary, job_summary)
            
            # Calculate overall match score
            match_score = calculate_match_score(cv_data, job, similarity_score)
            
            # Add match score to job data
            job_with_score = job.copy()
            job_with_score['match_score'] = round(match_score, 2)
            job_with_score['similarity_score'] = round(similarity_score * 100, 2)
            
            matches.append(job_with_score)
        
        # Sort by match score (descending)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Return top N matches
        return matches[:top_n]
    
    def rank_jobs(
        self,
        cv_data: Dict,
        job_offers: List[Dict]
    ) -> List[Tuple[Dict, float]]:
        """
        Rank all job offers by match score with the CV.
        
        Args:
            cv_data: Parsed CV data
            job_offers: List of job offers
            
        Returns:
            List of tuples (job_offer, match_score) sorted by score
        """
        matches = self.match_cv_with_jobs(cv_data, job_offers, len(job_offers))
        return [(job, job['match_score']) for job in matches]
    
    def explain_match(self, cv_data: Dict, job_data: Dict) -> Dict:
        """
        Provide detailed explanation of why a job matches a CV.
        
        Args:
            cv_data: Parsed CV data
            job_data: Job offer data
            
        Returns:
            Dictionary with match explanation
        """
        cv_summary = create_cv_summary(cv_data)
        if not cv_summary.strip():
            cv_summary = cv_data.get('raw_text', '')
        
        job_summary = create_job_summary(job_data)
        
        similarity_score = nlp_service.compute_similarity(cv_summary, job_summary)
        match_score = calculate_match_score(cv_data, job_data, similarity_score)
        
        # Find matching skills
        cv_skills = set([s.lower() for s in cv_data.get('skills', [])])
        job_requirements = job_data.get('requirements', [])
        job_skills = set()
        for req in job_requirements:
            job_skills.update([word.lower() for word in req.split() if len(word) > 3])
        
        matching_skills = list(cv_skills.intersection(job_skills))
        
        return {
            'match_score': round(match_score, 2),
            'similarity_score': round(similarity_score * 100, 2),
            'matching_skills': matching_skills[:10],
            'job_title': job_data.get('title', ''),
            'company': job_data.get('company', ''),
            'explanation': self._generate_explanation(match_score, matching_skills)
        }
    
    def _generate_explanation(self, match_score: float, matching_skills: List[str]) -> str:
        """Generate a human-readable explanation of the match."""
        if match_score >= 80:
            level = "excellent"
        elif match_score >= 60:
            level = "good"
        elif match_score >= 40:
            level = "moderate"
        else:
            level = "low"
        
        explanation = f"This is a {level} match (score: {match_score:.1f}/100). "
        
        if matching_skills:
            explanation += f"Your profile matches {len(matching_skills)} key skills including: "
            explanation += ", ".join(matching_skills[:5])
            if len(matching_skills) > 5:
                explanation += f" and {len(matching_skills) - 5} more."
        else:
            explanation += "Consider highlighting relevant transferable skills in your application."
        
        return explanation

# Singleton instance
matching_agent = MatchingAgent()

"""
Groq-powered Cover Letter Generator Service.
Uses Groq LLM for ultra-targeted cover letter generation with skill-matching.
"""

import os
import re
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Constants
MAX_RESPONSIBILITY_LENGTH = 100  # Maximum characters for experience descriptions


class GroqCoverLetterService:
    """
    Service for generating skill-matching-driven cover letters using Groq LLM.
    """
    
    def __init__(self):
        """Initialize Groq client with API key."""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
        self.client = Groq(api_key=api_key)
        self.model = "mixtral-8x7b-32768"  # High-quality model with large context
    
    def _extract_skills(self, cv_data: Dict) -> List[str]:
        """
        Extract skills from CV data.
        
        Args:
            cv_data: Parsed CV data
            
        Returns:
            List of skills
        """
        skills = cv_data.get('skills', [])
        return [skill.strip() for skill in skills if skill.strip()]
    
    def _extract_job_requirements(self, job_data: Dict) -> List[str]:
        """
        Extract requirements from job data.
        
        Args:
            job_data: Job offer data
            
        Returns:
            List of requirements
        """
        requirements = job_data.get('requirements', [])
        
        # Also extract from description if available
        description = job_data.get('description', '') or job_data.get('description_text', '')
        
        # Combine requirements
        all_requirements = list(requirements) if requirements else []
        
        return [req.strip() for req in all_requirements if req.strip()]
    
    def _match_skills(self, cv_data: Dict, job_data: Dict) -> Tuple[List[str], List[str]]:
        """
        Match candidate skills with job requirements.
        
        Args:
            cv_data: Parsed CV data
            job_data: Job offer data
            
        Returns:
            Tuple of (matched_skills, missing_skills)
        """
        cv_skills = set(skill.lower() for skill in self._extract_skills(cv_data))
        job_requirements = set(req.lower() for req in self._extract_job_requirements(job_data))
        
        # Extract potential skill keywords from job description (more conservative)
        description = job_data.get('description', '') or job_data.get('description_text', '')
        if description:
            # Look for capitalized words, tech terms, or words with numbers/special chars
            tech_words = re.findall(r'\b[A-Z][a-z]*(?:[A-Z][a-z]*)*\b|[a-z]+\+\+|[a-z]+\.js|[a-z]+[0-9]', description)
            job_requirements.update([w.lower() for w in tech_words if len(w) > 3])
        
        # Find matches using word boundary matching to avoid false positives
        matched = []
        for cv_skill in cv_skills:
            for job_req in job_requirements:
                # Exact match or skill as complete word in requirement
                if cv_skill == job_req or (cv_skill in job_req and len(cv_skill) > 3):
                    matched.append(cv_skill)
                    break
        
        # Find missing (important job requirements not in CV)
        missing = []
        job_reqs_list = list(self._extract_job_requirements(job_data))
        for req in job_reqs_list[:5]:  # Top 5 requirements
            req_lower = req.lower()
            found = False
            for cv_skill in cv_skills:
                if cv_skill == req_lower or (cv_skill in req_lower and len(cv_skill) > 3):
                    found = True
                    break
            if not found:
                missing.append(req)
        
        return matched[:10], missing[:5]  # Return top matches
    
    def _extract_relevant_experiences(self, cv_data: Dict, matched_skills: List[str]) -> List[Dict]:
        """
        Extract relevant work experiences based on matched skills.
        
        Args:
            cv_data: Parsed CV data
            matched_skills: List of matched skills
            
        Returns:
            List of relevant experiences
        """
        experiences = cv_data.get('experience', [])
        if not experiences:
            return []
        
        # Return most recent experiences (max 3)
        relevant = []
        for exp in experiences[:3]:
            if isinstance(exp, dict):
                relevant.append(exp)
        
        return relevant
    
    def _normalize_text_for_pdf(self, text: str) -> str:
        """
        Normalize text for PDF compatibility.
        Replaces problematic characters with ASCII equivalents.
        
        Args:
            text: Input text
            
        Returns:
            Normalized text safe for PDF
        """
        # Replace smart quotes with regular quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Replace em/en dashes with regular dashes
        text = text.replace('—', '-').replace('–', '-')
        
        # Replace common accented characters with ASCII equivalents
        replacements = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a',
            'ô': 'o', 'ö': 'o',
            'ù': 'u', 'û': 'u', 'ü': 'u',
            'î': 'i', 'ï': 'i',
            'ç': 'c',
            'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
            'À': 'A', 'Â': 'A', 'Ä': 'A',
            'Ô': 'O', 'Ö': 'O',
            'Ù': 'U', 'Û': 'U', 'Ü': 'U',
            'Î': 'I', 'Ï': 'I',
            'Ç': 'C',
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        # Remove any remaining non-ASCII (last resort)
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        return text
    
    def generate_cover_letter(
        self,
        cv_data: Dict,
        job_data: Dict,
        custom_message: str = ""
    ) -> str:
        """
        Generate an ultra-targeted cover letter using Groq LLM.
        
        Args:
            cv_data: Parsed CV data with structured information
            job_data: Job offer data
            custom_message: Optional custom message to include
            
        Returns:
            Generated cover letter text
        """
        # Extract candidate information
        candidate_name = cv_data.get('name', 'Candidate')
        candidate_email = cv_data.get('email', '')
        candidate_phone = cv_data.get('phone', '')
        
        # Extract job information
        job_title = job_data.get('title', 'the position')
        company = job_data.get('company') or job_data.get('organization', 'your company')
        job_description = job_data.get('description', '') or job_data.get('description_text', '')
        
        # Perform skill matching
        matched_skills, missing_skills = self._match_skills(cv_data, job_data)
        relevant_experiences = self._extract_relevant_experiences(cv_data, matched_skills)
        
        # Build experience summary
        experience_text = ""
        for i, exp in enumerate(relevant_experiences, 1):
            title = exp.get('title', 'Professional')
            company_name = exp.get('company', 'a leading organization')
            responsibilities = exp.get('responsibilities', '')
            if isinstance(responsibilities, list):
                responsibilities = ', '.join(responsibilities[:2])
            experience_text += f"{i}. {title} at {company_name}"
            if responsibilities:
                # Truncate at word boundary for cleaner summary
                truncated = responsibilities[:MAX_RESPONSIBILITY_LENGTH]
                if len(responsibilities) > MAX_RESPONSIBILITY_LENGTH:
                    truncated = truncated.rsplit(' ', 1)[0] + '...'
                experience_text += f": {truncated}"
            experience_text += "\n"
        
        # Create the prompt for Groq
        prompt = f"""You are an expert professional cover letter writer. Generate a highly targeted, ATS-friendly cover letter based on the following information.

CANDIDATE INFORMATION:
- Name: {candidate_name}
- Email: {candidate_email}
- Phone: {candidate_phone}
- Matched Skills: {', '.join(matched_skills[:8]) if matched_skills else 'General skills'}

RELEVANT EXPERIENCE:
{experience_text if experience_text else 'Entry-level candidate with educational background'}

JOB INFORMATION:
- Position: {job_title}
- Company: {company}
- Description: {job_description[:500]}

SKILL MATCH ANALYSIS:
- Matching Skills: {', '.join(matched_skills[:5]) if matched_skills else 'To be highlighted from experience'}
- Skills to Emphasize: {', '.join(missing_skills[:3]) if missing_skills else 'Core competencies'}

{f"CUSTOM MESSAGE TO INCORPORATE: {custom_message}" if custom_message else ""}

REQUIREMENTS:
1. Write in a STRICT PROFESSIONAL STRUCTURE with the following sections:
   - Header with candidate contact information
   - Date
   - Recipient address (Hiring Manager, {company})
   - Professional salutation
   - Opening paragraph: State position and express interest
   - Body paragraph 1: Highlight CONCRETE experiences that match job requirements
   - Body paragraph 2: Demonstrate specific skills alignment with the role
   - Closing paragraph: Express enthusiasm and call to action
   - Professional closing (Sincerely,)

2. ENFORCE STRICT RULES:
   - NO clichés (e.g., "I am writing to express my interest", "team player", "detail-oriented")
   - Use ONLY concrete, measurable achievements
   - Reference specific skills from the matched skills list
   - Keep total length to 300-400 words
   - Use active voice and strong action verbs
   - Be direct and specific

3. LANGUAGE: Write in professional English

4. FORMAT: Use simple paragraph formatting suitable for PDF export

Generate the cover letter now:"""

        # Call Groq API
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert cover letter writer who creates professional, ATS-friendly cover letters that highlight concrete skills and experiences. You avoid clichés and focus on measurable achievements."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=2000,
            )
            
            cover_letter = chat_completion.choices[0].message.content
            
            # Normalize text for PDF compatibility
            cover_letter = self._normalize_text_for_pdf(cover_letter)
            
            return cover_letter
            
        except Exception as e:
            raise Exception(f"Error generating cover letter with Groq: {str(e)}")
    
    def get_skill_match_report(self, cv_data: Dict, job_data: Dict) -> Dict:
        """
        Generate a skill match report.
        
        Args:
            cv_data: Parsed CV data
            job_data: Job offer data
            
        Returns:
            Dictionary with skill match analysis
        """
        matched_skills, missing_skills = self._match_skills(cv_data, job_data)
        
        # Calculate match percentage based on job requirements
        job_requirements = self._extract_job_requirements(job_data)
        total_requirements = len(job_requirements)
        
        if total_requirements > 0:
            match_percentage = (len(matched_skills) / total_requirements) * 100
        else:
            # If no specific requirements, use a heuristic
            match_percentage = (len(matched_skills) / max(len(matched_skills) + len(missing_skills), 1)) * 100
        
        return {
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'match_percentage': min(match_percentage, 100)  # Cap at 100%
        }


# Singleton instance - initialized on first use
_groq_cover_letter_service = None

def get_groq_cover_letter_service():
    """Get or create the Groq cover letter service singleton."""
    global _groq_cover_letter_service
    if _groq_cover_letter_service is None:
        _groq_cover_letter_service = GroqCoverLetterService()
    return _groq_cover_letter_service

# For backward compatibility
class _GroqServiceProxy:
    """Proxy to lazily initialize the service."""
    def __getattr__(self, name):
        return getattr(get_groq_cover_letter_service(), name)

groq_cover_letter_service = _GroqServiceProxy()

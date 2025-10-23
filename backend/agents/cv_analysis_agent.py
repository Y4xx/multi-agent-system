import re
from typing import Dict, List
from services.utils import extract_text_from_file

class CVAnalysisAgent:
    """
    Agent responsible for parsing and extracting structured data from CVs.
    """
    
    def __init__(self):
        self.name = "CV Analysis Agent"
    
    def analyze_cv(self, cv_content: str) -> Dict:
        """
        Analyze CV content and extract structured information.
        
        Args:
            cv_content: Raw text content of the CV
            
        Returns:
            Dictionary containing parsed CV data
        """
        cv_data = {
            'name': self._extract_name(cv_content),
            'email': self._extract_email(cv_content),
            'phone': self._extract_phone(cv_content),
            'skills': self._extract_skills(cv_content),
            'experience': self._extract_experience(cv_content),
            'education': self._extract_education(cv_content),
            'languages': self._extract_languages(cv_content),
            'raw_text': cv_content
        }
        
        return cv_data
    
    def analyze_cv_file(self, filepath: str) -> Dict:
        """
        Analyze a CV file and extract structured information.
        
        Args:
            filepath: Path to the CV file
            
        Returns:
            Dictionary containing parsed CV data
        """
        cv_content = extract_text_from_file(filepath)
        return self.analyze_cv(cv_content)
    
    def _extract_name(self, text: str) -> str:
        """Extract name from CV text."""
        # Simple heuristic: first line or first capitalized words
        lines = text.strip().split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) < 50 and not '@' in line:
                # Check if it looks like a name (mostly letters and spaces)
                if re.match(r'^[A-Z][a-zA-Z\s]+$', line):
                    return line
        return ""
    
    def _extract_email(self, text: str) -> str:
        """Extract email from CV text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from CV text."""
        # Match various phone formats
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\d{10}',
            r'\(\d{3}\)\s?\d{3}-\d{4}'
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return ""
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from CV text."""
        skills = []
        
        # Common technical skills to look for
        skill_keywords = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue',
            'Node.js', 'Django', 'FastAPI', 'Flask', 'SQL', 'MongoDB', 'PostgreSQL',
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Git', 'CI/CD',
            'Machine Learning', 'Deep Learning', 'NLP', 'TensorFlow', 'PyTorch',
            'Data Analysis', 'REST API', 'GraphQL', 'Microservices', 'Agile',
            'HTML', 'CSS', 'Tailwind', 'Bootstrap', 'Redis', 'RabbitMQ',
            'Linux', 'Bash', 'DevOps', 'Security', 'Testing', 'Selenium'
        ]
        
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                skills.append(skill)
        
        # Look for skills section
        skills_section_pattern = r'(?:skills?|technical skills?|competencies)[\s:]+(.+?)(?:\n\n|\n[A-Z]|$)'
        matches = re.findall(skills_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if matches:
            section_text = matches[0]
            # Extract comma or bullet-separated items
            items = re.split(r'[,\n•\-]', section_text)
            for item in items:
                item = item.strip()
                if item and len(item) < 50:
                    skills.append(item)
        
        return list(set(skills))[:20]  # Return unique skills, max 20
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience from CV text."""
        experience = []
        
        # Look for experience section
        exp_section_pattern = r'(?:experience|work history|employment)[\s:]+(.+?)(?:\n\n[A-Z]|education|skills|$)'
        matches = re.findall(exp_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if matches:
            section_text = matches[0]
            # Try to extract individual experiences
            # Look for patterns like "Title at Company" or "Company - Title"
            job_patterns = [
                r'([A-Z][A-Za-z\s]+)\s+(?:at|@)\s+([A-Z][A-Za-z\s&.,]+)',
                r'([A-Z][A-Za-z\s&.,]+)\s+-\s+([A-Z][A-Za-z\s]+)'
            ]
            
            for pattern in job_patterns:
                job_matches = re.findall(pattern, section_text)
                for match in job_matches[:5]:  # Max 5 experiences
                    experience.append({
                        'title': match[0].strip(),
                        'company': match[1].strip()
                    })
        
        return experience if experience else []
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education from CV text."""
        education = []
        
        # Look for education section
        edu_section_pattern = r'(?:education|academic|qualifications)[\s:]+(.+?)(?:\n\n[A-Z]|experience|skills|$)'
        matches = re.findall(edu_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if matches:
            section_text = matches[0]
            # Look for degree patterns
            degree_keywords = ['Bachelor', 'Master', 'PhD', 'BSc', 'MSc', 'MBA', 'Degree']
            
            for keyword in degree_keywords:
                if keyword.lower() in section_text.lower():
                    # Extract line containing the degree
                    lines = section_text.split('\n')
                    for line in lines:
                        if keyword.lower() in line.lower():
                            education.append({
                                'degree': line.strip(),
                                'institution': ''
                            })
        
        return education if education else []
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages from CV text."""
        languages = []
        
        common_languages = [
            'English', 'French', 'Spanish', 'German', 'Italian', 'Portuguese',
            'Chinese', 'Japanese', 'Korean', 'Arabic', 'Russian', 'Hindi'
        ]
        
        text_lower = text.lower()
        for lang in common_languages:
            if lang.lower() in text_lower:
                languages.append(lang)
        
        return list(set(languages))

# Singleton instance
cv_analysis_agent = CVAnalysisAgent()

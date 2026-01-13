from typing import Dict
import os
from dotenv import load_dotenv
from openai import OpenAI
from services.utils import get_job_field

load_dotenv()

class MotivationAgent:
    """
    Agent responsible for generating personalized motivation letters using OpenAI API.
    Format-agnostic: works with both old and new job data formats.
    """
    
    def __init__(self):
        self.name = "Motivation Agent"
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.model = os.getenv('MODEL_NAME', 'gpt-4o-mini')
        else:
            self.client = None
            self.model = None
    
    def generate_motivation_letter(
        self,
        cv_data: Dict,
        job_data: Dict,
        custom_message: str = ""
    ) -> str:
        """
        Generate a personalized motivation letter using OpenAI API.
        
        Args:
            cv_data: Parsed CV data
            job_data: Job offer data (supports both old and new formats)
            custom_message: Optional custom message from user
            
        Returns:
            Generated motivation letter text
        """
        # Extract relevant information using format-agnostic helpers
        applicant_name = cv_data.get('name', 'Applicant')
        job_title = get_job_field(job_data, 'title') or 'the position'
        company = get_job_field(job_data, 'company') or 'your company'
        location = get_job_field(job_data, 'location') or 'Not specified'
        job_description = get_job_field(job_data, 'description')
        seniority = get_job_field(job_data, 'seniority') or ''
        
        # Extract applicant's skills and experience
        skills = cv_data.get('skills', [])
        experience = cv_data.get('experience', [])
        education = cv_data.get('education', [])
        
        # If OpenAI is not configured, fall back to basic template
        if not self.client:
            return self._generate_fallback_letter(
                applicant_name, job_title, company, skills, experience, custom_message
            )
        
        # Build prompt for OpenAI
        prompt = self._build_openai_prompt(
            applicant_name, job_title, company, location, job_description,
            seniority, skills, experience, education, custom_message
        )
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career counselor and professional writer specializing in crafting personalized, compelling motivation letters. Your letters are professional, concise, and highlight the candidate's relevant skills and experience."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            motivation_letter = response.choices[0].message.content.strip()
            return motivation_letter
            
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            # Fall back to basic template on error
            return self._generate_fallback_letter(
                applicant_name, job_title, company, skills, experience, custom_message
            )
    
    def _build_openai_prompt(
        self,
        applicant_name: str,
        job_title: str,
        company: str,
        location: str,
        job_description: str,
        seniority: str,
        skills: list,
        experience: list,
        education: list,
        custom_message: str
    ) -> str:
        """Build a comprehensive prompt for OpenAI."""
        
        # Format skills
        skills_text = ', '.join(skills[:10]) if skills else 'various technical skills'
        
        # Format experience
        experience_text = ""
        if experience:
            for i, exp in enumerate(experience[:3]):
                if isinstance(exp, dict):
                    title = exp.get('title', '')
                    comp = exp.get('company', '')
                    if title and comp:
                        experience_text += f"- {title} at {comp}\n"
        
        # Format education
        education_text = ""
        if education:
            for edu in education[:2]:
                if isinstance(edu, dict):
                    degree = edu.get('degree', '')
                    institution = edu.get('institution', '')
                    if degree:
                        education_text += f"- {degree}" + (f" from {institution}" if institution else "") + "\n"
        
        prompt = f"""Write a professional and personalized motivation letter for the following job application:

**Job Details:**
- Position: {job_title}
- Company: {company}
- Location: {location}
{f"- Seniority Level: {seniority}" if seniority else ""}

**Job Description:**
{job_description[:500]}

**Candidate Information:**
- Name: {applicant_name}
- Skills: {skills_text}

**Professional Experience:**
{experience_text if experience_text else "Entry-level candidate"}

**Education:**
{education_text if education_text else "Educational background available"}

{f"**Additional Message to Include:**{chr(10)}{custom_message}{chr(10)}" if custom_message else ""}

**Instructions:**
1. Write a compelling motivation letter that highlights the candidate's relevant skills and experience
2. Align the candidate's qualifications with the job requirements
3. Keep it professional yet engaging
4. Length: 250-350 words
5. Structure: Opening, 2-3 body paragraphs highlighting qualifications, closing
6. End with "Sincerely," followed by the candidate's name
7. Do NOT include a subject line or address header
8. Start directly with "Dear Hiring Manager," or similar greeting

Write the complete motivation letter now:"""
        
        return prompt
    
    def _generate_fallback_letter(
        self,
        applicant_name: str,
        job_title: str,
        company: str,
        skills: list,
        experience: list,
        custom_message: str
    ) -> str:
        """Generate a basic template letter as fallback."""
        letter_parts = []
        
        letter_parts.append("Dear Hiring Manager,")
        letter_parts.append("")
        
        letter_parts.append(
            f"I am writing to express my strong interest in the {job_title} position at {company}. "
            f"With my background and skills, I am confident that I would be a valuable addition to your team."
        )
        letter_parts.append("")
        
        if skills:
            skills_text = ", ".join(skills[:5])
            letter_parts.append(
                f"My technical expertise includes {skills_text}, which align well with the requirements "
                f"for this role."
            )
            letter_parts.append("")
        
        if custom_message:
            letter_parts.append(custom_message)
            letter_parts.append("")
        
        letter_parts.append(
            f"I am excited about the possibility of contributing to {company}'s success and would welcome "
            f"the opportunity to discuss how my background and skills would benefit your team."
        )
        letter_parts.append("")
        letter_parts.append("Sincerely,")
        letter_parts.append(applicant_name)
        
        return "\n".join(letter_parts)
    
    def customize_letter(
        self,
        base_letter: str,
        customizations: Dict
    ) -> str:
        """
        Customize an existing motivation letter with user modifications.
        
        Args:
            base_letter: The base motivation letter
            customizations: Dictionary of customizations to apply
            
        Returns:
            Customized letter
        """
        letter = base_letter
        
        # Apply customizations
        for key, value in customizations.items():
            if key == 'opening':
                # Replace the opening
                lines = letter.split('\n')
                lines[0] = value
                letter = '\n'.join(lines)
            
            elif key == 'closing':
                # Replace the closing
                lines = letter.split('\n')
                # Find "Sincerely" or similar
                for i, line in enumerate(lines):
                    if 'sincerely' in line.lower() or 'regards' in line.lower():
                        lines[i] = value
                        break
                letter = '\n'.join(lines)
            
            elif key == 'additional_paragraph':
                # Add before closing
                lines = letter.split('\n')
                # Find closing position
                for i, line in enumerate(lines):
                    if 'sincerely' in line.lower() or 'regards' in line.lower():
                        lines.insert(i, value)
                        lines.insert(i + 1, "")
                        break
                letter = '\n'.join(lines)
        
        return letter
    
    def generate_short_pitch(self, cv_data: Dict, job_data: Dict) -> str:
        """
        Generate a short elevator pitch for quick applications.
        
        Args:
            cv_data: Parsed CV data
            job_data: Job offer data
            
        Returns:
            Short pitch text
        """
        applicant_name = cv_data.get('name', 'Applicant')
        job_title = get_job_field(job_data, 'title') or 'this position'
        company = get_job_field(job_data, 'company') or 'your company'
        skills = cv_data.get('skills', [])[:3]
        
        skills_text = ", ".join(skills) if skills else "relevant skills"
        
        pitch = (
            f"I am {applicant_name}, and I am very interested in the {job_title} position at {company}. "
            f"With expertise in {skills_text}, I am confident I can contribute to your team's success. "
            f"I would appreciate the opportunity to discuss this role further."
        )
        
        return pitch

# Singleton instance
motivation_agent = MotivationAgent()

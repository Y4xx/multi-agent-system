from typing import Dict
from datetime import datetime

class MotivationAgent:
    """
    Agent responsible for generating personalized motivation letters.
    """
    
    def __init__(self):
        self.name = "Motivation Agent"
    
    def generate_motivation_letter(
        self,
        cv_data: Dict,
        job_data: Dict,
        custom_message: str = ""
    ) -> str:
        """
        Generate a personalized motivation letter.
        
        Args:
            cv_data: Parsed CV data
            job_data: Job offer data
            custom_message: Optional custom message from user
            
        Returns:
            Generated motivation letter text
        """
        # Extract relevant information
        applicant_name = cv_data.get('name', 'Applicant')
        job_title = job_data.get('title', 'the position')
        company = job_data.get('company', 'your company')
        job_description = job_data.get('description', '')
        requirements = job_data.get('requirements', [])
        
        # Extract applicant's skills and experience
        skills = cv_data.get('skills', [])
        experience = cv_data.get('experience', [])
        education = cv_data.get('education', [])
        
        # Generate the letter
        letter_parts = []
        
        # Opening
        letter_parts.append(f"Dear Hiring Manager,")
        letter_parts.append("")
        
        # Introduction
        letter_parts.append(
            f"I am writing to express my strong interest in the {job_title} position at {company}. "
            f"With my background and skills, I am confident that I would be a valuable addition to your team."
        )
        letter_parts.append("")
        
        # Skills and qualifications
        if skills:
            top_skills = skills[:5]
            skills_text = ", ".join(top_skills[:-1])
            if len(top_skills) > 1:
                skills_text += f", and {top_skills[-1]}"
            else:
                skills_text = top_skills[0]
            
            letter_parts.append(
                f"My technical expertise includes {skills_text}, which align well with the requirements "
                f"for this role. I have developed these skills through practical experience and continuous learning."
            )
            letter_parts.append("")
        
        # Experience
        if experience:
            exp_count = len(experience)
            letter_parts.append(
                f"I bring {exp_count} professional experience{'s' if exp_count > 1 else ''} to this role. "
            )
            
            if experience[0] and isinstance(experience[0], dict):
                recent_exp = experience[0]
                letter_parts.append(
                    f"Most recently, I worked as {recent_exp.get('title', 'a professional')} at "
                    f"{recent_exp.get('company', 'a leading organization')}, where I gained valuable "
                    f"experience that directly applies to this position."
                )
            letter_parts.append("")
        
        # Why this company/role
        letter_parts.append(
            f"I am particularly drawn to this opportunity at {company} because of your commitment to "
            f"innovation and excellence. The role's focus on {self._extract_key_focus(job_description)} "
            f"aligns perfectly with my career goals and expertise."
        )
        letter_parts.append("")
        
        # Custom message if provided
        if custom_message:
            letter_parts.append(custom_message)
            letter_parts.append("")
        
        # Closing
        letter_parts.append(
            f"I am excited about the possibility of contributing to {company}'s success and would welcome "
            f"the opportunity to discuss how my background and skills would benefit your team. "
            f"Thank you for considering my application."
        )
        letter_parts.append("")
        letter_parts.append("Sincerely,")
        letter_parts.append(applicant_name)
        
        return "\n".join(letter_parts)
    
    def _extract_key_focus(self, description: str) -> str:
        """Extract the key focus area from job description."""
        # Simple extraction of first meaningful phrase
        sentences = description.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            # Extract key phrase (first 50 chars or until comma)
            key_focus = first_sentence[:50]
            if ',' in key_focus:
                key_focus = key_focus.split(',')[0]
            return key_focus.lower()
        return "the role's responsibilities"
    
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
        job_title = job_data.get('title', 'this position')
        company = job_data.get('company', 'your company')
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

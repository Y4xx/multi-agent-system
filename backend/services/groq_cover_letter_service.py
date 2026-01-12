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
    
    def _match_skills(self, cv_data: Dict, job_data: Dict) -> List[Tuple[str, str]]:
        """
        Match candidate skills with job requirements.
        
        Args:
            cv_data: Parsed CV data
            job_data: Job offer data
            
        Returns:
            List of tuples (candidate_skill, matched_requirement)
        """
        cv_skills = self._extract_skills(cv_data)
        job_requirements = self._extract_job_requirements(job_data)
        
        # Extract potential skill keywords from job description (more conservative)
        description = job_data.get('description', '') or job_data.get('description_text', '')
        if description:
            # Look for capitalized words, tech terms, or words with numbers/special chars
            tech_words = re.findall(r'\b[A-Z][a-z]*(?:[A-Z][a-z]*)*\b|[a-z]+\+\+|[a-z]+\.js|[a-z]+[0-9]', description)
            job_requirements.extend([w for w in tech_words if len(w) > 3])
        
        # Find matches using word boundary matching to avoid false positives
        matched = []
        cv_skills_lower = [s.lower() for s in cv_skills]
        
        for cv_skill in cv_skills:
            cv_skill_lower = cv_skill.lower()
            for job_req in job_requirements:
                job_req_lower = job_req.lower()
                # Exact match or skill as complete word in requirement
                if cv_skill_lower == job_req_lower or (cv_skill_lower in job_req_lower and len(cv_skill_lower) > 3):
                    matched.append((cv_skill, job_req))
                    break
                elif job_req_lower in cv_skill_lower and len(job_req_lower) > 3:
                    matched.append((cv_skill, job_req))
                    break
        
        return matched[:10]  # Return top matches
    
    def _extract_candidate_info(self, cv_data: Dict) -> Dict:
        """
        Extract comprehensive candidate information from CV data.
        
        Args:
            cv_data: Parsed CV data
            
        Returns:
            Dictionary with candidate information
        """
        raw_text = cv_data.get('raw_text', '')
        
        # Extract experiences with more detail
        experiences = []
        exp_data = cv_data.get('experience', [])
        for exp in exp_data[:5]:
            if isinstance(exp, dict):
                title = exp.get('title', '')
                company = exp.get('company', '')
                responsibilities = exp.get('responsibilities', [])
                
                if isinstance(responsibilities, list):
                    resp_text = '; '.join(responsibilities[:2])
                else:
                    resp_text = str(responsibilities)[:MAX_RESPONSIBILITY_LENGTH]
                
                if title and company:
                    exp_str = f"{title} at {company}"
                    if resp_text:
                        exp_str += f" - {resp_text}"
                    experiences.append(exp_str)
        
        # Extract formations/education
        formations = []
        edu_data = cv_data.get('education', [])
        for edu in edu_data[:3]:
            if isinstance(edu, dict):
                degree = edu.get('degree', '')
                institution = edu.get('institution', '')
                if degree:
                    formations.append(f"{degree}" + (f" - {institution}" if institution else ""))
        
        # Extract certifications from raw text or structured data
        certifications = cv_data.get('certifications', [])
        if isinstance(certifications, list):
            certifications = [str(cert) for cert in certifications[:5]]
        
        return {
            'name': cv_data.get('name', 'Candidate'),
            'email': cv_data.get('email', ''),
            'phone': cv_data.get('phone', ''),
            'skills': self._extract_skills(cv_data),
            'experiences': experiences,
            'formations': formations,
            'certifications': certifications
        }
    
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
        # Extract comprehensive candidate information
        candidate_info = self._extract_candidate_info(cv_data)
        
        # Extract job information
        job_title = job_data.get('title', 'the position')
        company = job_data.get('company') or job_data.get('organization', 'your company')
        location = job_data.get('location', '')
        job_description = job_data.get('description', '') or job_data.get('description_text', '')
        job_requirements = self._extract_job_requirements(job_data)
        
        # Perform skill matching
        skill_matches = self._match_skills(cv_data, job_data)
        
        # Detect language from job description
        is_french = any(word in job_description.lower() for word in ['développement', 'expérience', 'équipe', 'nous recherchons'])
        
        # Build the enhanced prompt with skill matching
        if is_french:
            prompt = f"""MISSION : Redige une lettre de motivation ULTRA-CIBLEE pour ce match job/candidat.

=== OFFRE D'EMPLOI ===
Poste : {job_title}
Entreprise : {company}
Localisation : {location if location else 'Not specified'}
Description : {job_description[:600]}
Exigences cles :
{chr(10).join([f"- {req}" for req in job_requirements[:7]])}

=== PROFIL CANDIDAT : {candidate_info['name']} ===
Contact : {candidate_info['email']} | {candidate_info['phone']}

Stack technique :
{', '.join(candidate_info['skills'][:15])}

Experience professionnelle :
{chr(10).join([f"- {exp}" for exp in candidate_info['experiences'][:5]])}

Formation :
{chr(10).join([f"- {form}" for form in candidate_info['formations'][:3]])}

Certifications :
{chr(10).join([f"- {cert}" for cert in candidate_info['certifications'][:3]])}

=== COMPETENCES QUI MATCHENT ===
{chr(10).join([f"- Candidat a '{match[0]}' => Requis '{match[1]}'" for match in skill_matches[:5]]) if skill_matches else "Identifier les transferable skills"}

=== STRUCTURE OBLIGATOIRE (280 mots MAX) ===

PARAGRAPHE 1 - ACCROCHE CIBLEE (3-4 lignes)
Commence par UNE competence ou realisation concrete qui matche l'offre.
Exemple : 'Developper des APIs RESTful avec {candidate_info['skills'][0] if candidate_info['skills'] else 'Python'} qui gerent 50K requetes/jour, c'est ce que je fais actuellement.'
Enchaine sur pourquoi {company} et ce poste specifiquement.

PARAGRAPHE 2 - PREUVES CONCRETES (5-6 lignes)
Cite 2-3 experiences/projets qui correspondent aux exigences du poste.
Format : [Projet/Experience] + [Technologies utilisees] + [Resultat/Impact]
Privilegie les experiences avec les technologies matchees.
Utilise les VRAIES experiences du candidat listees ci-dessus.

PARAGRAPHE 3 - FIT & VALEUR AJOUTEE (4-5 lignes)
Explique pourquoi tu es le bon match pour {company}.
Mentionne la formation si pertinent pour le poste.
Mets en avant la capacite d'apprentissage et les certifications.
Ce que tu apportes : competences techniques + mindset professionnel.

PARAGRAPHE 4 - CLOSING PRO (2 lignes)
'Je serais ravi d'echanger sur comment mes competences peuvent contribuer a [projet/mission de l'entreprise].'
'Disponible pour un entretien a votre convenance.'
Termine par 'Cordialement,' UNIQUEMENT.

{f"CUSTOM MESSAGE TO INCORPORATE: {custom_message}" if custom_message else ""}

=== REGLES D'OR ===
- Utilise les VRAIES experiences du candidat (pas d'invention)
- Adapte chaque phrase au poste vise
- Mentionne des technologies/projets concrets
- Phrases courtes : 15-20 mots max
- ZERO cliche : 'dynamique', 'motive', 'passionne' = INTERDIT
- Ton professionnel mais moderne (pas guinde)
- Pas de signature finale (juste 'Cordialement,')

GO ! Redige cette lettre maintenant."""
            
            system_message = (
                "Tu es un expert en recrutement tech qui redige des lettres de motivation "
                "sur mesure. Tu analyses le profil du candidat et l'offre d'emploi pour creer "
                "un pitch parfait qui met en avant les competences pertinentes. "
                "Style : direct, factuel, professionnel mais moderne. Zero bullshit."
            )
        else:
            # English prompt
            prompt = f"""MISSION: Write an ULTRA-TARGETED cover letter for this job/candidate match.

=== JOB OFFER ===
Position: {job_title}
Company: {company}
Location: {location if location else 'Not specified'}
Description: {job_description[:600]}
Key Requirements:
{chr(10).join([f"- {req}" for req in job_requirements[:7]])}

=== CANDIDATE PROFILE: {candidate_info['name']} ===
Contact: {candidate_info['email']} | {candidate_info['phone']}

Technical Stack:
{', '.join(candidate_info['skills'][:15])}

Professional Experience:
{chr(10).join([f"- {exp}" for exp in candidate_info['experiences'][:5]])}

Education:
{chr(10).join([f"- {form}" for form in candidate_info['formations'][:3]])}

Certifications:
{chr(10).join([f"- {cert}" for cert in candidate_info['certifications'][:3]])}

=== MATCHING SKILLS ===
{chr(10).join([f"- Candidate has '{match[0]}' => Required '{match[1]}'" for match in skill_matches[:5]]) if skill_matches else "Identify transferable skills"}

=== MANDATORY STRUCTURE (280 words MAX) ===

PARAGRAPH 1 - TARGETED HOOK (3-4 lines)
Start with ONE concrete skill or achievement matching the offer.
Example: 'Building RESTful APIs with {candidate_info['skills'][0] if candidate_info['skills'] else 'Python'} handling 50K requests/day is what I do currently.'
Connect to why {company} and this specific position.

PARAGRAPH 2 - CONCRETE PROOF (5-6 lines)
Cite 2-3 experiences/projects matching job requirements.
Format: [Project/Experience] + [Technologies used] + [Result/Impact]
Prioritize experiences with matched technologies.
Use REAL candidate experiences listed above.

PARAGRAPH 3 - FIT & VALUE ADD (4-5 lines)
Explain why you're the right match for {company}.
Mention education if relevant for the position.
Highlight learning capacity and certifications.
What you bring: technical skills + professional mindset.

PARAGRAPH 4 - PROFESSIONAL CLOSING (2 lines)
'I would be delighted to discuss how my skills can contribute to [company project/mission].'
'Available for an interview at your convenience.'
End with 'Sincerely,' ONLY.

{f"CUSTOM MESSAGE TO INCORPORATE: {custom_message}" if custom_message else ""}

=== GOLDEN RULES ===
- Use REAL candidate experiences (no invention)
- Adapt each sentence to target position
- Mention concrete technologies/projects
- Short sentences: 15-20 words max
- ZERO cliches: 'dynamic', 'motivated', 'passionate' = FORBIDDEN
- Professional but modern tone (not stiff)
- No final signature (just 'Sincerely,')

GO! Write this letter now."""
            
            system_message = (
                "You are a tech recruitment expert who writes tailored cover letters. "
                "You analyze the candidate's profile and job offer to create "
                "a perfect pitch highlighting relevant skills. "
                "Style: direct, factual, professional but modern. No bullshit."
            )
        
        # Call Groq API with enhanced prompt
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,  # Use configured model instead of hardcoding
                temperature=0.7,
                max_tokens=900,
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
        skill_matches = self._match_skills(cv_data, job_data)
        
        # Extract matched skills from tuples
        matched_skills = [match[0] for match in skill_matches]
        
        # Calculate match percentage based on job requirements
        job_requirements = self._extract_job_requirements(job_data)
        total_requirements = len(job_requirements)
        
        # Find missing skills (job requirements not in matched skills)
        missing_skills = []
        matched_skills_lower = [s.lower() for s in matched_skills]
        for req in job_requirements[:10]:
            req_lower = req.lower()
            found = False
            for matched_skill in matched_skills_lower:
                if matched_skill in req_lower or req_lower in matched_skill:
                    found = True
                    break
            if not found:
                missing_skills.append(req)
        
        if total_requirements > 0:
            match_percentage = (len(matched_skills) / total_requirements) * 100
        else:
            # If no specific requirements, use a heuristic
            match_percentage = (len(matched_skills) / max(len(matched_skills) + len(missing_skills), 1)) * 100
        
        return {
            'matched_skills': matched_skills,
            'missing_skills': missing_skills[:5],  # Limit to top 5 missing
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

import json
import os
from typing import Any, Dict, List
from datetime import datetime

def load_json_file(filepath: str) -> Any:
    """
    Load and parse a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Parsed JSON data
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {filepath}: {str(e)}")
        return None

def save_json_file(filepath: str, data: Any) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        filepath: Path to save the JSON file
        data: Data to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON file {filepath}: {str(e)}")
        return False

def extract_text_from_file(filepath: str) -> str:
    """
    Extract text from various file formats.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Extracted text content
    """
    try:
        # Get file extension
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == '.pdf':
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(filepath)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except Exception as e:
                print(f"Error reading PDF: {str(e)}")
                return ""
        
        elif ext in ['.doc', '.docx']:
            try:
                from docx import Document
                doc = Document(filepath)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                return text
            except Exception as e:
                print(f"Error reading DOCX: {str(e)}")
                return ""
        
        else:
            # Try to read as plain text
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
                
    except Exception as e:
        print(f"Error extracting text from {filepath}: {str(e)}")
        return ""

def format_date(date_str: str) -> str:
    """
    Format a date string to a standard format.
    
    Args:
        date_str: Input date string
        
    Returns:
        Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except:
        return date_str

def calculate_match_score(cv_data: Dict, job_data: Dict, similarity_score: float) -> float:
    """
    Calculate an overall match score between CV and job.
    
    Args:
        cv_data: Parsed CV data
        job_data: Job offer data
        similarity_score: NLP similarity score
        
    Returns:
        Match score between 0 and 100
    """
    # Base score from NLP similarity (70% weight)
    base_score = similarity_score * 70
    
    # Bonus points for skill matches (20% weight)
    cv_skills = set([s.lower() for s in cv_data.get('skills', [])])
    job_requirements = job_data.get('requirements', [])
    job_skills = set()
    for req in job_requirements:
        job_skills.update([word.lower() for word in req.split() if len(word) > 3])
    
    if cv_skills and job_skills:
        skill_match = len(cv_skills.intersection(job_skills)) / max(len(job_skills), 1)
        skill_score = skill_match * 20
    else:
        skill_score = 0
    
    # Bonus for experience level (10% weight)
    experience_score = 10  # Default
    
    total_score = base_score + skill_score + experience_score
    
    return min(total_score, 100)  # Cap at 100

def create_cv_summary(cv_data: Dict) -> str:
    """
    Create a text summary of CV data.
    
    Args:
        cv_data: Parsed CV data
        
    Returns:
        Text summary of the CV
    """
    parts = []
    
    if cv_data.get('name'):
        parts.append(f"Name: {cv_data['name']}")
    
    if cv_data.get('skills'):
        parts.append(f"Skills: {', '.join(cv_data['skills'])}")
    
    if cv_data.get('experience'):
        parts.append("Experience:")
        for exp in cv_data['experience']:
            if isinstance(exp, dict):
                parts.append(f"  - {exp.get('title', '')} at {exp.get('company', '')}")
            else:
                parts.append(f"  - {exp}")
    
    if cv_data.get('education'):
        parts.append("Education:")
        for edu in cv_data['education']:
            if isinstance(edu, dict):
                parts.append(f"  - {edu.get('degree', '')} from {edu.get('institution', '')}")
            else:
                parts.append(f"  - {edu}")
    
    return "\n".join(parts)

def create_job_summary(job_data: Dict) -> str:
    """
    Create a text summary of job offer data.
    
    Args:
        job_data: Job offer data
        
    Returns:
        Text summary of the job offer
    """
    parts = []
    
    parts.append(f"Position: {job_data.get('title', '')}")
    parts.append(f"Company: {job_data.get('company', '')}")
    parts.append(f"Location: {job_data.get('location', '')}")
    parts.append(f"Type: {job_data.get('type', '')}")
    parts.append(f"Description: {job_data.get('description', '')}")
    
    if job_data.get('requirements'):
        parts.append("Requirements:")
        for req in job_data['requirements']:
            parts.append(f"  - {req}")
    
    return "\n".join(parts)

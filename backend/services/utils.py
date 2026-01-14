import json
import os
import mimetypes
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
    Format-agnostic: supports both old and new job data formats.
    
    Old format: title, company, location, type, description, requirements
    New format: title, organization, description_text, employment_type, 
                locations_derived, remote_derived, seniority
    
    Args:
        job_data: Job offer data
        
    Returns:
        Text summary of the job offer
    """
    parts = []
    
    # Title (both formats use 'title')
    title = job_data.get('title', '')
    if title:
        parts.append(f"Position: {title}")
    
    # Company/Organization (old: company, new: organization)
    company = job_data.get('company') or job_data.get('organization', '')
    if company:
        parts.append(f"Company: {company}")
    
    # Location (old: location, new: locations_derived)
    location = job_data.get('location')
    if not location and job_data.get('locations_derived'):
        # locations_derived might be a list or string
        locations = job_data['locations_derived']
        if isinstance(locations, list):
            location = ', '.join(str(loc) for loc in locations)
        else:
            location = str(locations)
    if location:
        parts.append(f"Location: {location}")
    
    # Remote work (new format only)
    if job_data.get('remote_derived'):
        parts.append(f"Remote: {job_data['remote_derived']}")
    
    # Type (old: type, new: employment_type)
    job_type = job_data.get('type') or job_data.get('employment_type', '')
    if job_type:
        parts.append(f"Type: {job_type}")
    
    # Seniority (new format only)
    if job_data.get('seniority'):
        parts.append(f"Seniority: {job_data['seniority']}")
    
    # Description (old: description, new: description_text)
    description = job_data.get('description') or job_data.get('description_text', '')
    if description:
        parts.append(f"Description: {description}")
    
    # Requirements (old format only, might not exist in new format)
    if job_data.get('requirements'):
        parts.append("Requirements:")
        for req in job_data['requirements']:
            parts.append(f"  - {req}")
    
    return "\n".join(parts)


def get_job_field(job_data: Dict, field_name: str) -> str:
    """
    Get a job field value with format-agnostic field mapping.
    
    Maps between old and new job data formats:
    - title -> title
    - company -> organization
    - location -> locations_derived
    - type -> employment_type
    - description -> description_text
    
    Args:
        job_data: Job offer data
        field_name: Field name (using old format names for backward compatibility)
        
    Returns:
        Field value as string
    """
    # Field mapping: old_name -> [old_name, new_name]
    field_mapping = {
        'title': ['title'],
        'company': ['company', 'organization'],
        'location': ['location', 'locations_derived'],
        'type': ['type', 'employment_type'],
        'description': ['description', 'description_text'],
        'seniority': ['seniority'],
        'remote': ['remote_derived'],
        'application_email': ['application_email']
    }
    
    fields_to_check = field_mapping.get(field_name, [field_name])
    
    for field in fields_to_check:
        value = job_data.get(field)
        if value is not None:  # Allow 0 and False but not None
            # Handle list values (e.g., locations_derived, employment_type)
            if isinstance(value, list):
                # Filter out None values and empty strings after conversion
                filtered = [str(v) for v in value if v is not None and str(v).strip()]
                return ', '.join(filtered) if filtered else ''
            # Handle boolean values
            elif isinstance(value, bool):
                return 'Yes' if value else 'No'
            # Handle string values - only return if not empty
            str_value = str(value).strip()
            if str_value:
                return str_value
    
    return ''


def sanitize_filename(text: str) -> str:
    """
    Sanitize text for use in filenames.
    Removes special characters and replaces spaces with underscores.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text safe for filenames
    """
    # Keep only alphanumeric characters, spaces, hyphens, and underscores
    safe_text = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_'))
    # Strip and replace spaces with underscores
    return safe_text.strip().replace(' ', '_')


def get_mime_type(filepath: str) -> str:
    """
    Get MIME type for a file based on its extension.
    
    Args:
        filepath: Path to the file
        
    Returns:
        MIME type string (e.g., 'application/pdf')
    """
    # Initialize mimetypes if not already done
    if not mimetypes.inited:
        mimetypes.init()
    
    # Get MIME type from extension
    mime_type, _ = mimetypes.guess_type(filepath)
    
    # Default to octet-stream if unknown
    if mime_type is None:
        mime_type = 'application/octet-stream'
    
    return mime_type

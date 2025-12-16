"""
CrewAI Task Definitions.
Defines all tasks for the job application workflow.
"""

from crewai import Task
from typing import Dict, List

def create_cv_parsing_task(agent, cv_text: str):
    """
    Create CV Parsing Task.
    Extracts structured data from a CV.
    """
    return Task(
        description=(
            f"Analyze the following CV and extract structured information:\n\n"
            f"{cv_text}\n\n"
            f"Extract the following information:\n"
            f"- Full name\n"
            f"- Email address\n"
            f"- Phone number\n"
            f"- List of technical and soft skills\n"
            f"- Work experience (job title, company, responsibilities)\n"
            f"- Education (degree, institution)\n"
            f"- Languages spoken\n\n"
            f"Provide the information in a clear, structured format."
        ),
        agent=agent,
        expected_output="Structured CV data with all relevant fields extracted and organized"
    )

def create_job_fetching_task(agent, filters: Dict = None):
    """
    Create Job Fetching Task.
    Retrieves job offers based on criteria.
    """
    filter_desc = ""
    if filters:
        if filters.get('job_type'):
            filter_desc += f"\n- Job type: {filters['job_type']}"
        if filters.get('location'):
            filter_desc += f"\n- Location: {filters['location']}"
        if filters.get('keyword'):
            filter_desc += f"\n- Keyword: {filters['keyword']}"
    
    return Task(
        description=(
            f"Retrieve job offers from the database with the following criteria:"
            f"{filter_desc if filter_desc else ' No specific filters - retrieve all available jobs.'}\n\n"
            f"Ensure you load the most up-to-date job listings and format them properly."
        ),
        agent=agent,
        expected_output="List of job offers matching the specified criteria"
    )

def create_matching_task(agent, cv_data: Dict, jobs: List[Dict], top_n: int = 10):
    """
    Create Matching Task.
    Ranks jobs based on CV compatibility.
    """
    cv_summary = f"Candidate Profile:\n"
    cv_summary += f"- Name: {cv_data.get('name', 'N/A')}\n"
    cv_summary += f"- Skills: {', '.join(cv_data.get('skills', [])[:10])}\n"
    cv_summary += f"- Experience: {len(cv_data.get('experience', []))} positions\n"
    
    jobs_summary = f"\nAvailable Jobs: {len(jobs)} positions to evaluate\n"
    
    return Task(
        description=(
            f"Analyze the candidate's profile and match it with available job offers:\n\n"
            f"{cv_summary}\n"
            f"{jobs_summary}\n"
            f"Rank the top {top_n} jobs based on:\n"
            f"1. Skills alignment\n"
            f"2. Experience level match\n"
            f"3. Education requirements\n"
            f"4. Overall compatibility\n\n"
            f"Provide a match score (0-100) for each job and explain the reasoning."
        ),
        agent=agent,
        expected_output=f"Top {top_n} ranked jobs with match scores and explanations"
    )

def create_cover_letter_task(agent, cv_data: Dict, job_data: Dict, custom_message: str = ""):
    """
    Create Cover Letter Task.
    Generates a personalized French cover letter.
    """
    candidate_name = cv_data.get('name', 'Candidat')
    job_title = job_data.get('title', 'le poste')
    company = job_data.get('company', "l'entreprise")
    job_description = job_data.get('description', '')
    requirements = job_data.get('requirements', [])
    
    skills_text = ', '.join(cv_data.get('skills', [])[:8])
    experience_summary = ""
    if cv_data.get('experience'):
        experience_summary = f"Expérience professionnelle: {len(cv_data.get('experience', []))} postes"
    
    custom_note = ""
    if custom_message:
        custom_note = f"\n\nMessage personnel à intégrer: {custom_message}"
    
    return Task(
        description=(
            f"Rédigez une lettre de motivation professionnelle EN FRANÇAIS pour:\n\n"
            f"CANDIDAT:\n"
            f"- Nom: {candidate_name}\n"
            f"- Compétences: {skills_text}\n"
            f"- {experience_summary}\n\n"
            f"POSTE VISÉ:\n"
            f"- Titre: {job_title}\n"
            f"- Entreprise: {company}\n"
            f"- Description: {job_description}\n"
            f"- Exigences principales: {', '.join(requirements[:5])}\n"
            f"{custom_note}\n\n"
            f"INSTRUCTIONS IMPORTANTES:\n"
            f"1. Écrivez UNIQUEMENT en français\n"
            f"2. Utilisez un ton professionnel et formel\n"
            f"3. Mettez en avant les compétences du candidat qui correspondent aux exigences\n"
            f"4. Gardez la lettre concise (3-4 paragraphes maximum)\n"
            f"5. Optimisez pour les systèmes ATS\n"
            f"6. Incluez une introduction, un corps démontrant l'adéquation, et une conclusion engageante\n"
            f"7. Utilisez la formule de politesse française appropriée\n\n"
            f"La lettre doit convaincre le recruteur d'accorder un entretien au candidat."
        ),
        agent=agent,
        expected_output="Une lettre de motivation professionnelle en français, personnalisée pour le poste et le candidat"
    )

def create_application_task(agent, cv_data: Dict, job_data: Dict, motivation_letter: str):
    """
    Create Application Task.
    Prepares and submits the application.
    """
    return Task(
        description=(
            f"Prepare and submit a job application with the following details:\n\n"
            f"CANDIDATE: {cv_data.get('name', 'N/A')}\n"
            f"JOB: {job_data.get('title', 'N/A')} at {job_data.get('company', 'N/A')}\n"
            f"RECIPIENT EMAIL: {job_data.get('application_email', 'N/A')}\n\n"
            f"The application includes:\n"
            f"- Candidate CV data\n"
            f"- Personalized motivation letter\n\n"
            f"Ensure the application is properly formatted and ready for submission."
        ),
        agent=agent,
        expected_output="Application submission status and confirmation details"
    )

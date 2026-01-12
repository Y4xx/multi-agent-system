"""
FastAPI Routes using CrewAI.
Refactored API endpoints to use CrewAI-based workflow.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil

from crew.crew import job_application_crew
from agents.job_fetcher_agent import job_fetcher_agent
from agents.application_agent import application_agent
from services.utils import save_json_file

# Create router
router = APIRouter()

# Create uploads directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic models for request/response
class MatchRequest(BaseModel):
    cv_data: dict
    job_type: Optional[str] = None
    location: Optional[str] = None
    top_n: int = 10

class GenerateLetterRequest(BaseModel):
    cv_data: dict
    job_id: int
    custom_message: Optional[str] = ""

class ApplyRequest(BaseModel):
    cv_data: dict
    job_id: int
    motivation_letter: str

class BulkApplyRequest(BaseModel):
    cv_data: dict
    applications: List[dict]


# CV Upload endpoint
@router.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload a CV file and extract structured data using CrewAI.
    
    Args:
        file: The CV file (PDF, DOCX, or TXT)
        
    Returns:
        Parsed CV data
    """
    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process CV using CrewAI crew
        cv_data = job_application_crew.analyze_cv_file(file_path)
        
        # Save parsed CV data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        save_json_file(os.path.join(data_dir, "parsed_cv.json"), cv_data)
        
        return {
            "success": True,
            "message": "CV processed successfully",
            "data": cv_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading CV: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing CV file")


# Get job offers endpoint
@router.get("/job-offers")
async def get_job_offers(
    job_type: Optional[str] = None,
    location: Optional[str] = None,
    keyword: Optional[str] = None
):
    """
    Fetch available job offers with optional filters.
    
    Args:
        job_type: Filter by job type (Full-time, Internship, etc.)
        location: Filter by location
        keyword: Filter by keyword in title/description
        
    Returns:
        List of job offers
    """
    try:
        jobs = job_application_crew.fetch_jobs(
            job_type=job_type,
            location=location,
            keyword=keyword
        )
        
        return {
            "success": True,
            "count": len(jobs),
            "data": jobs
        }
        
    except Exception as e:
        print(f"Error fetching jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching job offers")


# Match offers endpoint
@router.post("/match-offers")
async def match_offers(request: MatchRequest):
    """
    Match CV with job offers and return top matches using CrewAI.
    
    Args:
        request: Match request with CV data and optional filters
        
    Returns:
        List of top matching job offers
    """
    try:
        matched_jobs = job_application_crew.get_job_recommendations(
            cv_data=request.cv_data,
            job_type=request.job_type,
            location=request.location,
            top_n=request.top_n
        )
        
        return {
            "success": True,
            "count": len(matched_jobs),
            "data": matched_jobs
        }
        
    except Exception as e:
        print(f"Error matching offers: {str(e)}")
        raise HTTPException(status_code=500, detail="Error matching offers with CV")


# Generate motivation letter endpoint
@router.post("/generate-letter")
async def generate_letter(request: GenerateLetterRequest):
    """
    Generate a personalized motivation letter using CrewAI LLM.
    
    Args:
        request: Request with CV data, job ID, and optional custom message
        
    Returns:
        Generated motivation letter and match information
    """
    try:
        package = job_application_crew.generate_application_package(
            cv_data=request.cv_data,
            job_id=request.job_id,
            custom_message=request.custom_message
        )
        
        if not package.get('success'):
            raise HTTPException(status_code=404, detail=package.get('message'))
        
        return {
            "success": True,
            "data": package
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating letter: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating motivation letter")


# Apply to job endpoint
@router.post("/apply")
async def apply_to_job(request: ApplyRequest):
    """
    Submit a job application via email using CrewAI.
    
    Args:
        request: Application request with CV data, job ID, and motivation letter
        
    Returns:
        Application submission result
    """
    try:
        # Get job data
        job_data = job_fetcher_agent.get_job_by_id(request.job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail=f"Job with ID {request.job_id} not found")
        
        # Submit application using CrewAI crew
        result = job_application_crew.submit_application(
            cv_data=request.cv_data,
            job_data=job_data,
            motivation_letter=request.motivation_letter
        )
        
        return {
            "success": result.get('success'),
            "message": result.get('message'),
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting application: {str(e)}")
        raise HTTPException(status_code=500, detail="Error submitting application")


# Bulk apply endpoint
@router.post("/apply-bulk")
async def apply_bulk(request: BulkApplyRequest):
    """
    Submit multiple job applications at once.
    
    Args:
        request: Bulk application request
        
    Returns:
        List of application results
    """
    try:
        results = application_agent.send_bulk_applications(
            cv_data=request.cv_data,
            applications=request.applications
        )
        
        return {
            "success": True,
            "count": len(results),
            "data": results
        }
        
    except Exception as e:
        print(f"Error submitting bulk applications: {str(e)}")
        raise HTTPException(status_code=500, detail="Error submitting applications")


# Get specific job endpoint
@router.get("/job/{job_id}")
async def get_job(job_id: int):
    """
    Get details of a specific job by ID.
    
    Args:
        job_id: ID of the job
        
    Returns:
        Job details
    """
    try:
        job = job_fetcher_agent.get_job_by_id(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
        
        return {
            "success": True,
            "data": job
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching job: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching job details")


# Get application history endpoint
@router.get("/applications")
async def get_applications():
    """
    Get all application submission records.
    
    Returns:
        List of application records
    """
    try:
        applications = application_agent.get_all_applications()
        
        return {
            "success": True,
            "count": len(applications),
            "data": applications
        }
        
    except Exception as e:
        print(f"Error fetching applications: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching application history")


# Export cover letter to PDF endpoint
@router.post("/export-pdf")
async def export_cover_letter_pdf(
    cv_data: dict,
    job_id: int,
    cover_letter: str,
    filename: Optional[str] = None
):
    """
    Export a cover letter to PDF format.
    
    Args:
        cv_data: Parsed CV data
        job_id: Job ID
        cover_letter: Cover letter text
        filename: Optional custom filename
        
    Returns:
        PDF file path and download information
    """
    try:
        # Get job data
        job_data = job_fetcher_agent.get_job_by_id(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
        
        # Export to PDF
        pdf_path = job_application_crew.export_cover_letter_to_pdf(
            cover_letter_text=cover_letter,
            cv_data=cv_data,
            job_data=job_data,
            filename=filename
        )
        
        return {
            "success": True,
            "pdf_path": pdf_path,
            "filename": os.path.basename(pdf_path),
            "message": "Cover letter exported to PDF successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error exporting to PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Error exporting cover letter to PDF")


# Get skill match analysis endpoint
@router.post("/skill-match")
async def get_skill_match(cv_data: dict, job_id: int):
    """
    Get detailed skill match analysis between CV and job.
    
    Args:
        cv_data: Parsed CV data
        job_id: Job ID
        
    Returns:
        Skill match report with matched/missing skills
    """
    try:
        # Get job data
        job_data = job_fetcher_agent.get_job_by_id(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
        
        # Get skill match analysis
        skill_match = job_application_crew.get_skill_match_analysis(cv_data, job_data)
        
        return {
            "success": True,
            "data": skill_match
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting skill match: {str(e)}")
        raise HTTPException(status_code=500, detail="Error analyzing skill match")

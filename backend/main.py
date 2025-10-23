from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil

from agents.coordinator_agent import coordinator_agent
from agents.job_fetcher_agent import job_fetcher_agent
from services.utils import save_json_file, load_json_file

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Job Application System",
    description="AI-powered system for intelligent job discovery and application automation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
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

# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Multi-Agent Job Application System API",
        "status": "running",
        "version": "1.0.0"
    }

# CV Upload endpoint
@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload a CV file and extract structured data.
    
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
        
        # Process CV
        cv_data = coordinator_agent.process_cv_file(file_path)
        
        # Save parsed CV data
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        save_json_file(os.path.join(data_dir, "parsed_cv.json"), cv_data)
        
        return {
            "success": True,
            "message": "CV processed successfully",
            "data": cv_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CV: {str(e)}")

# Get job offers endpoint
@app.get("/job-offers")
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
        if job_type:
            jobs = job_fetcher_agent.fetch_jobs_by_type(job_type)
        elif location:
            jobs = job_fetcher_agent.fetch_jobs_by_location(location)
        elif keyword:
            jobs = job_fetcher_agent.fetch_jobs_by_keyword(keyword)
        else:
            jobs = job_fetcher_agent.fetch_all_jobs()
        
        return {
            "success": True,
            "count": len(jobs),
            "data": jobs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")

# Match offers endpoint
@app.post("/match-offers")
async def match_offers(request: MatchRequest):
    """
    Match CV with job offers and return top matches.
    
    Args:
        request: Match request with CV data and optional filters
        
    Returns:
        List of top matching job offers
    """
    try:
        matched_jobs = coordinator_agent.get_job_recommendations(
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
        raise HTTPException(status_code=500, detail=f"Error matching offers: {str(e)}")

# Generate motivation letter endpoint
@app.post("/generate-letter")
async def generate_letter(request: GenerateLetterRequest):
    """
    Generate a personalized motivation letter for a specific job.
    
    Args:
        request: Request with CV data, job ID, and optional custom message
        
    Returns:
        Generated motivation letter and match information
    """
    try:
        package = coordinator_agent.generate_application_package(
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
        raise HTTPException(status_code=500, detail=f"Error generating letter: {str(e)}")

# Apply to job endpoint
@app.post("/apply")
async def apply_to_job(request: ApplyRequest):
    """
    Submit a job application via email.
    
    Args:
        request: Application request with CV data, job ID, and motivation letter
        
    Returns:
        Application submission result
    """
    try:
        result = coordinator_agent.submit_application(
            cv_data=request.cv_data,
            job_id=request.job_id,
            motivation_letter=request.motivation_letter
        )
        
        return {
            "success": result.get('success'),
            "message": result.get('message'),
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting application: {str(e)}")

# Bulk apply endpoint
@app.post("/apply-bulk")
async def apply_bulk(request: BulkApplyRequest):
    """
    Submit multiple job applications at once.
    
    Args:
        request: Bulk application request
        
    Returns:
        List of application results
    """
    try:
        from agents.application_agent import application_agent
        
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
        raise HTTPException(status_code=500, detail=f"Error submitting applications: {str(e)}")

# Get specific job endpoint
@app.get("/job/{job_id}")
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
        raise HTTPException(status_code=500, detail=f"Error fetching job: {str(e)}")

# Get application history endpoint
@app.get("/applications")
async def get_applications():
    """
    Get all application submission records.
    
    Returns:
        List of application records
    """
    try:
        from agents.application_agent import application_agent
        
        applications = application_agent.get_all_applications()
        
        return {
            "success": True,
            "count": len(applications),
            "data": applications
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching applications: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas import (
    JobCreationRequest, 
    JobCreationResponse,
    CVComparisonRequest,
    CVComparisonResponse
)
from app.utils.text_extractor import extract_text
from app.services.resume_analysis import analyze_resume
from app.services.matching import match_candidate
from app.services.summary import generate_summary
from app.services.questions import generate_questions
from app.services.jobcreation_service import generate_job_content
from app.services.cv_comparison_service import compare_cvs
import json

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/process-candidate")
async def process_candidate(
    job: str = Form(
        ...,
        description='''Job details in any JSON format. The JSON should contain job-related information such as title, requirements, location, type, etc. Example:
{
  "title": "Dairy Farm Worker",
  "location": "Rural Farm",
  "requirements": ["Cow milking experience", "Animal care skills"],
  "type": "Full-time"
}''',
        example='{\n  "title": "Dairy Farm Worker",\n  "location": "Rural Farm",\n  "requirements": ["Cow milking experience", "Animal care skills"],\n  "type": "Full-time"\n}'
    ),
    resume: UploadFile = File(...)
):
    # Parse the JSON string to dict - accepts any JSON format
    try:
        job_data = json.loads(job)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for job data")

    # Extract text from uploaded resume
    try:
        file_bytes = await resume.read()
        resume_text = extract_text(file_bytes, resume.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing resume file: {str(e)}")

    # Get analysis from all AI services
    try:
        resume_analysis = analyze_resume(resume_text)
        match_result = match_candidate(job_data, resume_text)
        summary = generate_summary(resume_text)
        interview_questions = generate_questions(job_data, resume_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during AI processing: {str(e)}")

    # Combine results in the desired output format
    return {
        "AI_fit_score": match_result["AI_fit_score"],
        "AI_generated_summary": summary,
        "strengths": match_result["strengths"],
        "areas_of_development": match_result["areas_of_development"],
        "work_experience": resume_analysis["work_experience"],
        "skills": resume_analysis["skills"],
        "certifications": resume_analysis["certifications"],
        "cover_letter_insights": resume_analysis["cover_letter_insights"],
        "AI_suggested_interview_questions": interview_questions
    }


@router.post("/create-job", response_model=JobCreationResponse)
async def create_job(job_request: JobCreationRequest):
    """
    Generate AI-powered job description and benefits based on job information.
    
    This endpoint takes basic job information and uses AI to generate:
    - A comprehensive, professional job description
    - A detailed benefits and perks section
    
    The generated content is tailored to the specific farm details provided.
    """
    try:
        # Convert Pydantic model to dictionary
        job_data = job_request.model_dump()
        
        # Generate job content using AI
        result = generate_job_content(job_data)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating job content: {str(e)}")


@router.post("/compare-cvs", response_model=CVComparisonResponse)
async def compare_two_cvs(comparison_request: CVComparisonRequest):
    """
    Compare two CVs and provide detailed analysis of differences.
    
    This endpoint accepts two CVs in JSON format and optionally job context to provide:
    - Overall comparison summary
    - Individual strengths of each candidate
    - Unique skills of each candidate
    - Comparative fit score (50=equal, >50=A stronger, <50=B stronger)
    
    The comparison is more accurate when job context is provided.
    """
    try:
        # Extract data from request
        cv_a = comparison_request.cv_a
        cv_b = comparison_request.cv_b
        job_context = comparison_request.job_context
        
        # Perform CV comparison using AI
        result = compare_cvs(cv_a, cv_b, job_context)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing CVs: {str(e)}")

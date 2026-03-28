import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from typing import Optional
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
    job_details: str = Form(
        ...,
        description='''Job details as a string or JSON format. Can include job title, requirements, location, type, etc. Example:
{
  "title": "Dairy Farm Worker",
  "location": "Rural Farm",
  "requirements": ["Cow milking experience", "Animal care skills"],
  "type": "Full-time"
}
Or simple text: "Looking for a dairy farm worker with milking experience"''',
        example='{\n  "title": "Dairy Farm Worker",\n  "location": "Rural Farm",\n  "requirements": ["Cow milking experience", "Animal care skills"],\n  "type": "Full-time"\n}'
    ),
    ideal_candidate: Optional[str] = Form(
        None,
        description='''Ideal candidate description as a string or JSON format. Can include expected skills, experience, qualifications, etc. Example:
{
  "experience": "3+ years in dairy farming",
  "skills": ["Milking", "Animal care", "Farm equipment operation"],
  "education": "Agricultural background preferred"
}
Or simple text: "3+ years experience in dairy farming with strong animal care skills"''',
        example='{\n  "experience": "3+ years in dairy farming",\n  "skills": ["Milking", "Animal care"],\n  "education": "Agricultural background"\n}'
    ),
    cv_json: Optional[str] = Form(
        None,
        description='''CV data in JSON format. If provided, this will be used instead of file upload. Example:
{
  "name": "John Smith",
  "work_experience": [{"role": "Farm Worker", "duration": "2019-2023"}],
  "skills": ["Milking", "Cattle care"],
  "certifications": ["Animal Welfare Training"]
}'''
    ),
    cv_file: Optional[UploadFile] = File(
        None,
        description="CV file upload (PDF, DOCX, TXT). Either cv_json or cv_file must be provided."
    ),
    cover_letter_file: Optional[UploadFile] = File(
        None,
        description="Cover letter file upload (PDF, DOCX, TXT). Optional field to supplement the CV."
    )
):
    """
    Process candidate CV against job details and ideal candidate profile.
    
    Accepts:
    - job_details: Job description (string or JSON)
    - ideal_candidate: Ideal candidate profile (string or JSON)
    - CV input: Either as JSON string (cv_json) OR file upload (cv_file)
    - cover_letter_file: Optional cover letter file (PDF, DOCX, TXT) to enhance analysis
    
    The cover letter (if provided) will be analysed alongside the CV to provide more accurate:
    - Candidate motivation and key traits
    - Job fit assessment
    - Interview question generation
    
    Returns comprehensive candidate analysis including fit score, summary, strengths, cover letter insights, etc.
    """
    
    # Validate that at least one CV input is provided
    if not cv_json and not cv_file:
        raise HTTPException(
            status_code=400, 
            detail="Either cv_json or cv_file must be provided"
        )
    
    # Parse job details (try JSON, fallback to string)
    try:
        job_data = json.loads(job_details)
    except json.JSONDecodeError:
        job_data = {"description": job_details}
    
    # Parse ideal candidate (try JSON, fallback to string)
    ideal_candidate_data = {}
    if ideal_candidate and ideal_candidate.strip():
        try:
            ideal_candidate_data = json.loads(ideal_candidate)
        except json.JSONDecodeError:
            ideal_candidate_data = {"description": ideal_candidate}
    
    # Get CV text - either from JSON or file
    if cv_json:
        try:
            cv_data = json.loads(cv_json)
            # Convert CV JSON to text format for processing
            resume_text = json.dumps(cv_data, indent=2)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid JSON format for cv_json"
            )
    else:
        # Extract text from uploaded file
        try:
            file_bytes = await cv_file.read()
            resume_text = extract_text(file_bytes, cv_file.filename)
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Error processing CV file: {str(e)}"
            )
    
    # Get cover letter text if provided
    cover_letter_text = ""
    if cover_letter_file:
        try:
            file_bytes = await cover_letter_file.read()
            cover_letter_text = extract_text(file_bytes, cover_letter_file.filename)
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Error processing cover letter file: {str(e)}"
            )
    
    # Combine CV and cover letter for analysis
    if cover_letter_text:
        combined_resume_text = f"{resume_text}\n\n--- COVER LETTER ---\n{cover_letter_text}"
    else:
        combined_resume_text = resume_text
    
    # Combine job details and ideal candidate for analysis
    combined_job_context = {
        "job_details": job_data,
        "ideal_candidate": ideal_candidate_data
    }
    
    # Get analysis from all AI services in PARALLEL for faster response
    try:
        resume_analysis, match_result, summary, interview_questions = await asyncio.gather(
            analyze_resume(combined_resume_text),
            match_candidate(combined_job_context, combined_resume_text),
            generate_summary(combined_resume_text),
            generate_questions(combined_job_context, combined_resume_text)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error during AI processing: {str(e)}"
        )
    
    # Combine results in the desired output format
    return {
        "AI_fit_score": match_result["AI_fit_score"],
        "AI_generated_summary": summary,
        "strengths": match_result["strengths"],
        "areas_of_development": match_result["areas_of_development"],
        "summary": match_result.get("summary", ""),
        "work_experience": resume_analysis["work_experience"],
        "skills": resume_analysis["skills"],
        "certifications": resume_analysis["certifications"],
        "cover_letter_insights": resume_analysis["cover_letter_insights"],
        "AI_suggested_interview_questions": interview_questions
    }


@router.post("/create-job", response_model=JobCreationResponse)
async def create_job(
    job_request: JobCreationRequest,
    jobdescription: Optional[str] = Query(default="", description="User-provided job description context to enhance AI generation"),
    benefitsAndPerks: Optional[str] = Query(default="", description="User-provided benefits and perks context to enhance AI generation")
):
    """
    Generate AI-powered job description and benefits based on job information.
    
    This endpoint takes basic job information and uses AI to generate:
    - A comprehensive, professional job description
    - A detailed benefits and perks section
    
    The generated content is tailored to the specific farm details provided.
    
    You can optionally provide additional context in the jobdescription and benefitsAndPerks 
    query parameters to influence the AI-generated output.
    """
    try:
        job_data = job_request.model_dump()
        # Add the query parameters to job_data for processing
        job_data["jobDescriptionText"] = jobdescription
        job_data["benefitsAndPerksText"] = benefitsAndPerks
        result = await generate_job_content(job_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating job content: {str(e)}"
        )


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
        cv_a = comparison_request.cv_a
        cv_b = comparison_request.cv_b
        job_context = comparison_request.job_context
        
        result = await compare_cvs(cv_a, cv_b, job_context)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error comparing CVs: {str(e)}"
        )
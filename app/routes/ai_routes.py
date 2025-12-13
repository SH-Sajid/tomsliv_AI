from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas import JobRequest
from app.utils.text_extractor import extract_text
from app.services.resume_analysis import analyze_resume
from app.services.matching import match_candidate
from app.services.summary import generate_summary
from app.services.questions import generate_questions
import json

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/process-candidate")
async def process_candidate(
    job: str = Form(...),  # Changed to str and use Form
    resume: UploadFile = File(...)
):
    # Parse the JSON string to dict
    try:
        job_data = json.loads(job)
        job_request = JobRequest(**job_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for job data")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing job data: {str(e)}")

    # Extract text from uploaded resume
    try:
        file_bytes = await resume.read()
        resume_text = extract_text(file_bytes, resume.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing resume file: {str(e)}")

    # Get analysis from all AI services
    try:
        resume_analysis = analyze_resume(resume_text)
        match_result = match_candidate(job_request.job_details, resume_text)
        summary = generate_summary(resume_text)
        interview_questions = generate_questions(job_request.job_details, resume_text)
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
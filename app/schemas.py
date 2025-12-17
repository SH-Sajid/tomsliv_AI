from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class JobDetails(BaseModel):
    title: str = Field(..., description="Job title, e.g. 'Dairy Farm Worker'")
    requirements: List[str] = Field(..., description="List of job requirements")
    location: str = Field(..., description="Job location")
    type: str = Field(..., description="Job type, e.g. 'Full-time'")

class JobRequest(BaseModel):
    job_details: JobDetails = Field(..., description="Job requirements and details")

class FitScore(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Match score between 0-100")
    explanation: str = Field(..., description="Explanation of the fit score")

class WorkExperience(BaseModel):
    role: str = Field(..., description="Job title/role")
    duration: str = Field(..., description="Duration of employment (e.g., 2019-2023)")
    responsibilities: List[str] = Field(..., description="List of key responsibilities")

class CoverLetterInsights(BaseModel):
    motivation: str = Field(..., description="Candidate's motivation and interest")
    key_traits: List[str] = Field(..., description="Key personality traits")

class InterviewQuestions(BaseModel):
    questions: List[str] = Field(..., description="List of suggested interview questions")

class CandidateAnalysisResponse(BaseModel):
    AI_fit_score: FitScore
    AI_generated_summary: str = Field(..., description="Brief summary of the candidate")
    strengths: List[str] = Field(..., description="Candidate's key strengths")
    areas_of_development: List[str] = Field(..., description="Areas for improvement")
    work_experience: List[WorkExperience]
    skills: List[str] = Field(..., description="List of candidate's skills")
    certifications: List[str] = Field(..., description="List of certifications")
    cover_letter_insights: CoverLetterInsights
    AI_suggested_interview_questions: InterviewQuestions

    class Config:
        json_schema_extra = {
            "example": {
                "AI_fit_score": {
                    "score": 86,
                    "explanation": "Candidate meets most job requirements with strong hands-on experience but lacks advanced machinery exposure."
                },
                "AI_generated_summary": "4 years of dairy farm experience with strong skills in milking and cattle care. Reliable and practical worker, suitable for medium to large farms.",
                "strengths": [
                    "Hands-on dairy farm experience",
                    "Strong animal handling skills",
                    "Consistent work history"
                ],
                "areas_of_development": [
                    "Farm equipment maintenance",
                    "Exposure to automated systems"
                ],
                "work_experience": [
                    {
                        "role": "Dairy Farm Worker",
                        "duration": "2019–2023",
                        "responsibilities": [
                            "Milking cows",
                            "Cattle feeding and care",
                            "Maintaining farm hygiene"
                        ]
                    }
                ],
                "skills": [
                    "Cow Milking",
                    "Cattle Care",
                    "Feed Management"
                ],
                "certifications": [
                    "Animal Welfare Training"
                ],
                "cover_letter_insights": {
                    "motivation": "Candidate expresses strong interest in long-term farm work and animal care.",
                    "key_traits": [
                        "Hardworking",
                        "Reliable",
                        "Team-oriented"
                    ]
                },
                "AI_suggested_interview_questions": {
                    "questions": [
                        "Can you describe your daily responsibilities at your previous farm?",
                        "How do you handle sick or injured animals?",
                        "Have you worked with automated milking systems?",
                        "How do you manage feeding schedules?",
                        "What experience do you have maintaining farm equipment?"
                    ]
                }
            }
        }
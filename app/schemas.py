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
    AI_generated_summary: str = Field(..., description="Brief professional summary of the candidate")
    strengths: List[str] = Field(..., description="Evidence-based strengths relative to the job and ideal profile")
    areas_of_development: List[str] = Field(..., description="Clear gaps relative to the job and ideal profile, including staff management depth, decision-making exposure, financial awareness, readiness for role, independent management, and any missing information such as visa status or formal education")
    summary: str = Field(default="", description="3-5 sentence explanation of why the candidate received their fit score, referencing specific evidence from the CV and cover letter")
    work_experience: List[WorkExperience]
    skills: List[str] = Field(..., description="List of candidate's skills")
    certifications: List[str] = Field(..., description="List of certifications")
    cover_letter_insights: CoverLetterInsights
    AI_suggested_interview_questions: InterviewQuestions

    class Config:
        json_schema_extra = {
            "example": {
                "AI_fit_score": {
                    "score": 62,
                    "explanation": "John meets several core job requirements with 2 years of dairy experience but lacks the preferred 5+ years and has no demonstrated staff management experience."
                },
                "AI_generated_summary": "John has 2 years of dairy farm experience focusing on milking and animal care. He is reliable but is early in his career and has not held a supervisory role.",
                "strengths": [
                    "Has direct dairy farming experience including rotary milking shed operation at XYZ Farm (2022–2024), which directly aligns with the core milking requirement.",
                    "Cover letter demonstrates genuine motivation for long-term farm work, citing a desire to grow into a management role."
                ],
                "areas_of_development": [
                    "No evidence of staff management or supervisory experience — the role requires overseeing 2–3 farm assistants.",
                    "Financial awareness not demonstrated; no mention of budgeting, farm accounts, or input cost management.",
                    "Visa status not mentioned in CV or cover letter — eligibility to work in New Zealand cannot be confirmed.",
                    "Formal agricultural qualifications not listed; preferred candidates hold a Level 4 Primary ITO certificate or equivalent."
                ],
                "summary": "John received a fit score of 62 because, while he has relevant dairy farming experience, it falls short of the preferred 5 years and he has no staff management background. His CV does not address visa status or formal qualifications, which are important gaps for this role. He shows motivation and potential but is not yet ready for independent farm management.",
                "work_experience": [
                    {
                        "role": "Dairy Farm Worker",
                        "duration": "2022–2024",
                        "responsibilities": [
                            "Rotary milking shed operation",
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
                    "motivation": "Candidate expresses strong interest in long-term farm work and growing into a management role.",
                    "key_traits": [
                        "Hardworking",
                        "Reliable",
                        "Ambitious"
                    ]
                },
                "AI_suggested_interview_questions": {
                    "questions": [
                        "Can you describe your daily responsibilities at your previous farm?",
                        "How do you handle sick or injured animals?",
                        "Have you ever supervised or trained other farm workers?",
                        "Are you currently eligible to work in New Zealand?",
                        "What experience do you have with farm budgeting or financial reporting?"
                    ]
                }
            }
        }

        # Add these to your existing schemas.py file

class PrimaryLocation(BaseModel):
    type: str = Field(..., description="Type of farm location")
    options: List[str] = Field(..., description="Available location options")

class BasicInformation(BaseModel):
    jobTitle: str = Field(..., description="Job title")
    farmSize_ha: str = Field(..., description="Farm size in hectares")
    peakHerdSize_cows: str = Field(..., description="Peak herd size (number of cows)")
    typicalOnFarmStaff: str = Field(..., description="Typical on-farm staff type")
    closingDateForApplications: Optional[str] = Field(None, description="Closing date for applications")
    positionStartDate: Optional[str] = Field(None, description="Position start date")

class JobDescriptionInfo(BaseModel):
    primaryLocation: PrimaryLocation = Field(..., description="Primary location information")
    role: Optional[str] = Field(None, description="Role description")
    workType: str = Field(..., description="Work type (e.g., Full-time)")

class RemunerationDetails(BaseModel):
    from_: Optional[str] = Field(None, alias="from", description="Remuneration from amount")
    to: Optional[str] = Field(None, description="Remuneration to amount")
    period: str = Field(..., description="Remuneration period (Hourly/Daily/Weekly/Monthly/Yearly)")

class WorkingInformation(BaseModel):
    hourType: Optional[str] = Field(None, description="Hour type")
    averageHoursPerWeek: str = Field(..., description="Average hours per week")
    roster: Optional[str] = Field(None, description="Roster information")
    remunerationPaidBy: Optional[str] = Field(None, description="Who pays remuneration")
    remunerationIfHourlyDailyWeeklyMonthlyYearly: RemunerationDetails = Field(..., description="Remuneration details")
    remunerationIfTotalPackageValue: Optional[str] = Field(None, description="Total package value")
    remunerationIfPerKgMS: Optional[str] = Field(None, description="Remuneration per KgMS")
    remunerationIfPercentageOfMilkCheque: Optional[str] = Field(None, description="Percentage of milk cheque")

class JobCreationRequest(BaseModel):
    basicInformation: BasicInformation = Field(..., description="Basic job information")
    jobDescription: JobDescriptionInfo = Field(..., description="Job description details")
    workingInformation: WorkingInformation = Field(..., description="Working information and remuneration")

    model_config = {
        "json_schema_extra": {
            "example": {
                "basicInformation": {
                    "jobTitle": "Farm assistant",
                    "farmSize_ha": "1200",
                    "peakHerdSize_cows": "60",
                    "typicalOnFarmStaff": "Full time",
                    "closingDateForApplications": "",
                    "positionStartDate": ""
                },
                "jobDescription": {
                    "primaryLocation": {
                        "type": "Single farm",
                        "options": ["Single farm", "Multiple farm", "Corporate farm"]
                    },
                    "role": "",
                    "workType": "Full-time"
                },
                "workingInformation": {
                    "hourType": "",
                    "averageHoursPerWeek": "60",
                    "roster": "",
                    "remunerationPaidBy": "",
                    "remunerationIfHourlyDailyWeeklyMonthlyYearly": {
                        "from": "",
                        "to": "",
                        "period": "Yearly"
                    },
                    "remunerationIfTotalPackageValue": "",
                    "remunerationIfPerKgMS": "",
                    "remunerationIfPercentageOfMilkCheque": ""
                }
            }
        }
    }

class BenefitsAndPerks(BaseModel):
    description: str = Field(..., description="Benefits and perks description")

class JobCreationResponse(BaseModel):
    fullJobDescription: str = Field(..., description="AI-generated full job description")
    benefitsAndPerks: BenefitsAndPerks = Field(..., description="AI-generated benefits and perks")

    class Config:
        json_schema_extra = {
            "example": {
                "fullJobDescription": "We are seeking a dedicated Farm Assistant to join our team on a 1200-hectare dairy farm with a peak herd of 60 cows. This full-time position involves daily farm operations including milking, feeding, and animal care. The ideal candidate will have experience in dairy farming, be physically fit, and able to work in various weather conditions. Responsibilities include operating farm machinery, maintaining facilities, monitoring animal health, and assisting with pasture management. You'll work as part of a full-time on-farm staff team in a supportive rural environment. This role offers hands-on experience in modern dairy farming practices and the opportunity to develop your agricultural skills.",
                "benefitsAndPerks": {
                    "description": "This position offers competitive remuneration in line with industry standards. Additional benefits include on-farm accommodation (if available), flexible roster arrangements to support work-life balance, opportunities for professional development and training in modern farming techniques, and the chance to work in a supportive team environment. You'll gain valuable experience on a well-established dairy operation with a manageable herd size of 60 cows across 1200 hectares, providing excellent learning opportunities for career advancement in the agricultural sector."
                }
            }
        }


        # Add these to your existing schemas.py file

class CVComparisonRequest(BaseModel):
    cv_a: Dict[str, Any] = Field(..., description="CV data for candidate A in JSON format")
    cv_b: Dict[str, Any] = Field(..., description="CV data for candidate B in JSON format")
    job_context: Optional[str] = Field(None, description="Optional job/team context for more accurate comparison")

    class Config:
        json_schema_extra = {
            "example": {
                "cv_a": {
                    "name": "John Smith",
                    "work_experience": [
                        {
                            "role": "Dairy Farm Worker",
                            "duration": "2019-2023",
                            "responsibilities": ["Milking cows", "Cattle care", "Feed management"]
                        }
                    ],
                    "skills": ["Cow Milking", "Cattle Care", "Feed Management"],
                    "certifications": ["Animal Welfare Training"]
                },
                "cv_b": {
                    "name": "Jane Doe",
                    "work_experience": [
                        {
                            "role": "Farm Manager",
                            "duration": "2018-2023",
                            "responsibilities": ["Team supervision", "Herd management", "Equipment maintenance"]
                        }
                    ],
                    "skills": ["Team Leadership", "Herd Management", "Machinery Operation"],
                    "certifications": ["Farm Management Certificate", "Tractor Operation Licence"]
                },
                "job_context": "Looking for a Farm Manager to oversee a 1200-hectare dairy farm with 60 cows. Must have leadership experience and technical knowledge."
            }
        }

class CVComparisonResponse(BaseModel):
    overallComparison: str = Field(..., description="Summary of differences between both CVs")
    strengthsA: List[str] = Field(..., description="Strengths of candidate A")
    strengthsB: List[str] = Field(..., description="Strengths of candidate B")
    uniqueSkillsA: List[str] = Field(..., description="Skills only candidate A has")
    uniqueSkillsB: List[str] = Field(..., description="Skills only candidate B has")
    fitComparisonScore: float = Field(..., ge=0, le=100, description="AI score indicating comparative candidate strength (50=equal, >50=A stronger, <50=B stronger)")

    class Config:
        json_schema_extra = {
            "example": {
                "overallComparison": "Both candidates bring valuable dairy farming experience, but with different strengths. Candidate A has 4 years of hands-on experience with strong animal care skills, while Candidate B has 5 years of experience with management responsibilities and technical expertise. Candidate B demonstrates broader skill set including team leadership and equipment maintenance, which aligns better with farm manager requirements. However, Candidate A shows deeper expertise in direct animal care and daily farm operations.",
                "strengthsA": [
                    "Extensive hands-on experience with cattle care and milking",
                    "Strong focus on animal welfare and daily operations",
                    "Consistent 4-year work history in dairy farming"
                ],
                "strengthsB": [
                    "Management and team leadership experience",
                    "Technical skills in machinery operation and maintenance",
                    "Broader range of certifications including farm management",
                    "Experience overseeing larger-scale operations"
                ],
                "uniqueSkillsA": [
                    "Specialized animal welfare training",
                    "Deep expertise in feed management systems"
                ],
                "uniqueSkillsB": [
                    "Team supervision and staff management",
                    "Equipment maintenance and repair",
                    "Tractor and heavy machinery operation",
                    "Farm management certification"
                ],
                "fitComparisonScore": 35.0
            }
        }
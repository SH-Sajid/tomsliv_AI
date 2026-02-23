from app.config import client
import json

def match_candidate(job_context: dict, resume_text: str):
    """
    Match candidate against job requirements and ideal candidate profile.
    
    job_context can contain:
    - job_details: Job description/requirements
    - ideal_candidate: Ideal candidate profile
    """
    
    job_details = job_context.get('job_details', {})
    ideal_candidate = job_context.get('ideal_candidate', {})
    
    ideal_candidate_prompt = ""
    weighting_instruction = "- How well the candidate matches the job requirements (60% weight)\n    - How close they are to the ideal candidate profile (40% weight)"
    match_instruction = "1. The job requirements\n    2. The ideal candidate profile"
    explanation_instruction = "mentioning what the candidate meets from both job requirements and ideal candidate profile, and what they lack"
    strengths_instruction = "relative to both the job and ideal profile"
    dev_instruction = "to match the ideal profile"

    if not ideal_candidate:
        ideal_candidate_prompt = "Ideal Candidate Profile: (Not provided)"
        weighting_instruction = "- How well the candidate matches the job requirements (100% weight)"
        match_instruction = "1. The job requirements"
        explanation_instruction = "mentioning what the candidate meets from the job requirements and what they lack"
        strengths_instruction = "relative to the job requirements"
        dev_instruction = "to better fit the job requirements"
    else:
        ideal_candidate_prompt = f"Ideal Candidate Profile:\n{json.dumps(ideal_candidate, indent=2)}"

    prompt = f"""
    You are an expert dairy farm recruitment assessor. Your job is to evaluate this candidate objectively and differentiate clearly between average, strong, and exceptional applicants. Do not be overly complimentary of skills and experience if there is no explicit and detailed evidence of those skills and experience. For example, if the applicant lists "problem solving" as a skill, do not conclude that they have "demonstrated excellent problem-solving skills." You need to be specific, use evidence from the applicant's CV and Cover Letter and avoid generic statements.

    LANGUAGE REQUIREMENT: All output must be provided exclusively in professional New Zealand English (British/NZ spelling conventions).
    Apply the following employer-standard NZ English spelling throughout:
    • "analyse" not "analyze"
    • "organisation" not "organization"
    • "recognised" not "recognized"
    • "programme" not "program"
    • "prioritise" not "prioritize"
    • "organised" not "organized"
    • "realise" not "realize"
    • "strategised" not "strategized"

    Maintain professional, employer-standard terminology and formal tone throughout. Do not use American English spellings.

    Position Requirements:
    {json.dumps(job_details, indent=2)}

    {ideal_candidate_prompt}

    Candidate's Resume:
    {resume_text}

    Follow these steps to evaluate the candidate:

    STEP 1 – Assess Job Requirements (60%)
    Score 0–60 based ONLY on how well the candidate meets the essential job requirements.
    0–20 = Missing critical requirements
    21–40 = Meets some requirements but gaps exist
    41–50 = Meets most requirements competently
    51–60 = Fully meets or exceeds all essential requirements
    If the candidate lacks any stated non-negotiable requirement, cap this section at 35 maximum.

    STEP 2 – Assess Ideal Candidate Profile (40%)
    Score 0–40 based on alignment with the ideal traits, leadership ability, initiative, communication, culture fit, ambition, and long-term potential.
    0–10 = Weak alignment
    11–20 = Moderate alignment
    21–30 = Strong alignment
    31–40 = Exceptional alignment
    Do NOT give high scores unless there is clear evidence.
    If no ideal candidate profile is provided, assign a proportional score based on the general professionalism, initiative, communication, and long-term potential evident from the CV and cover letter alone.

    STEP 3 – Calculate Final Score
    Add both sections for a final score out of 100.
    IMPORTANT:
    Use the full range 0–100.
    Avoid clustering in the 70–85 range.
    Scores above 90 should be rare and near perfect.
    Scores between 80 and 90 should be uncommon and for great candidates.
    Scores between 70 and 80 should be common and for candidates who are a good fit but may lack desired traits.
    Scores between 60 and 70 should be common and for candidates who could work on the farm but may not be a good match.
    Scores below 60 should be used when key requirements are missing.
    Differentiate decisively between candidates.
    Fit-Score Caps are as follows:
    - If the candidate has less than the preferred years of experience, then the fit score must not exceed 65.
    - If the candidate has no dairy farming experience, then the fit score must not exceed 40.
    - If the candidate is not eligible to work in New Zealand, then the fit score must not exceed 55.

    STEP 4 – Output Format
    Return a JSON object with this exact structure:
    {{
      "AI_fit_score": {{
        "score": 0-100,
        "explanation": "Brief explanation of the score, {explanation_instruction}"
      }},
      "strengths": [
        "Specific, evidence-based strength highlighting what the candidate does well relative to both the job and ideal profile, with concrete examples from the CV or cover letter.",
        "Another specific strength with evidence..."
      ],
      "areas_of_development": [
        "Clear gap relative to job and ideal profile. Assess staff management depth, decision-making exposure, financial awareness, readiness for role, and independent management where relevant. Identify exactly what skills or experiences the candidate needs to acquire. Note any important missing areas such as formal education, visa status, or ability to work in New Zealand.",
        "Another specific area for development..."
      ],
      "summary": "3-5 sentence summary of the candidate's CV and cover letter explaining why they received the fit score they did. For example: John received a fit score of 60 because of his limited dairy farming experience and no prior staff management. Be specific about the candidate by name where possible."
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
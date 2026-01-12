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
    Please conduct a comprehensive analysis comparing the candidate's resume with the position requirements and ideal candidate profile (if provided).
    
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

    Analyse how well the candidate matches:
    {match_instruction}
    
    Return a JSON object with this exact structure:
    {{
      "AI_fit_score": {{
        "score": 0-100,
        "explanation": "Brief explanation of the score, {explanation_instruction}"
      }},
      "strengths": ["strength 1", "strength 2", "strength 3"],
      "areas_of_development": ["area 1", "area 2"]
    }}

    The score should be a number between 0 and 100 based on:
    {weighting_instruction}
    
    Strengths should highlight what the candidate does well {strengths_instruction}.
    Areas of development should identify skills or experiences the candidate needs to improve or acquire {dev_instruction}.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
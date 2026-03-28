from app.config import async_client
import json

async def generate_questions(job_context: dict, resume_text: str):
    """
    Generate interview questions based on job requirements, ideal candidate profile, and resume.
    
    job_context can contain:
    - job_details: Job description/requirements
    - ideal_candidate: Ideal candidate profile
    """
    
    job_details = job_context.get('job_details', {})
    ideal_candidate = job_context.get('ideal_candidate', {})
    
    ideal_candidate_prompt = ""
    assessment_instruction = "- Assess the candidate's experience related to the job requirements\n    - Evaluate how they match the ideal candidate profile\n    - Explore their strengths\n    - Address any skill gaps between their experience and the ideal profile"
    final_instruction = "designed to reveal whether the candidate truly matches the ideal profile."

    if not ideal_candidate:
        ideal_candidate_prompt = "Ideal Candidate Profile: (Not provided)"
        assessment_instruction = "- Assess the candidate's experience related to the job requirements\n    - Explore their strengths\n    - Address any skill gaps between their experience and the job requirements"
        final_instruction = "designed to reveal whether the candidate truly matches the job requirements."
    else:
        ideal_candidate_prompt = f"Ideal Candidate Profile:\n{json.dumps(ideal_candidate, indent=2)}"

    prompt = f"""
    Please generate 5 strategically-designed interview questions based on the position requirements, ideal candidate profile (if provided), and the candidate's resume.
    
    LANGUAGE REQUIREMENT: All questions must be drafted exclusively in professional New Zealand English (British/NZ spelling conventions).
    Apply the following employer-standard NZ English spelling throughout:
    • "analyse" not "analyze"
    • "organised" not "organized"
    • "recognised" not "recognized"
    • "programme" not "program"
    • "organisation" not "organization"
    • "realise" not "realize"
    • "prioritise" not "prioritize"
    
    Draft questions using formal, professional employer language appropriate for a structured interview process. Do not use American English spellings.
    
    The questions should:
    {assessment_instruction}
    - Be practical and relevant to the role

    Job Details:
    {json.dumps(job_details, indent=2)}

    {ideal_candidate_prompt}

    Candidate's Resume:
    {resume_text}

    Return a JSON object with this exact structure:
    {{
      "questions": [
        "Question 1?",
        "Question 2?",
        "Question 3?",
        "Question 4?",
        "Question 5?"
      ]
    }}
    
    Make the questions specific and insightful, {final_instruction}
    """

    response = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
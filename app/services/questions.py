from app.config import client
import json

def generate_questions(job_context: dict, resume_text: str):
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
    Generate 5 relevant interview questions based on the job requirements, ideal candidate profile (if provided), and the candidate's resume.
    
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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
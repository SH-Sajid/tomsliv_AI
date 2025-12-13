from app.config import client
import json

def match_candidate(job_details: dict, resume_text: str):
    prompt = f"""
    Compare the job requirements with the candidate's resume and provide a detailed matching analysis.

    Job Details:
    {job_details}

    Resume:
    {resume_text}

    Return a JSON object with this exact structure:
    {{
      "AI_fit_score": {{
        "score": 0-100,
        "explanation": "Brief explanation of the score, mentioning what the candidate meets and what they lack"
      }},
      "strengths": ["strength 1", "strength 2", "strength 3"],
      "areas_of_development": ["area 1", "area 2"]
    }}

    The score should be a number between 0 and 100 based on how well the candidate matches the job requirements.
    Strengths should highlight what the candidate does well relative to the job.
    Areas of development should identify skills or experiences the candidate needs to improve or acquire.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
from app.config import client
import json

def generate_questions(job_details: dict, resume_text: str):
    prompt = f"""
    Generate 5 relevant interview questions based on the job requirements and the candidate's resume.
    The questions should:
    - Assess the candidate's experience related to the job
    - Explore their strengths
    - Address any skill gaps or areas that need clarification
    - Be practical and relevant to the role

    Job Details:
    {job_details}

    Resume:
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
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
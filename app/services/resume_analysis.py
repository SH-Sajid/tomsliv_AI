from app.config import client
import json

def analyze_resume(resume_text: str):
    prompt = f"""
    Analyze this resume and extract the following information in JSON format:

    Resume:
    {resume_text}

    Return a JSON object with this exact structure:
    {{
      "work_experience": [
        {{
          "role": "Job Title",
          "duration": "YYYY-YYYY",
          "responsibilities": ["responsibility 1", "responsibility 2", "responsibility 3"]
        }}
      ],
      "skills": ["skill1", "skill2", "skill3"],
      "certifications": ["certification1", "certification2"],
      "cover_letter_insights": {{
        "motivation": "Brief description of candidate's motivation and interest",
        "key_traits": ["trait1", "trait2", "trait3"]
      }}
    }}

    If cover letter is not available, infer motivation and traits from the resume content.
    Extract all work experiences with their roles, durations, and key responsibilities.
    List all technical and professional skills mentioned.
    Include any certifications, training, or qualifications.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
from app.config import client
import json

def analyze_resume(resume_text: str):
    prompt = f"""
    Please analyse this resume and cover letter (if provided) and extract the following information in a structured JSON format.
    
    LANGUAGE REQUIREMENT: All output must be provided exclusively in professional New Zealand English (British/NZ spelling conventions).
    Apply the following employer-standard NZ English spelling throughout:
    • "analyse" not "analyze"
    • "organised" not "organized"  
    • "recognised" not "recognized"
    • "programme" not "program"
    • "licence" not "license"
    • "prioritise" not "prioritize"
    • "realise" not "realize"
    
    Maintain professional, employer-standard terminology throughout. Do not use American English spellings or terminology.

    Resume and Cover Letter:
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
        "motivation": "Brief description of candidate's motivation and interest in the role",
        "key_traits": ["trait1", "trait2", "trait3"]
      }}
    }}

    IMPORTANT INSTRUCTIONS:
    - If a cover letter is present (marked with "--- COVER LETTER ---"), extract motivation and traits SPECIFICALLY from it.
    - For cover_letter_insights, prioritise information found in the actual cover letter section.
    - If no cover letter is available, infer motivation and traits from the resume content.
    - Extract all work experiences with their roles, durations, and key responsibilities from the resume section.
    - List all technical and professional skills mentioned in the resume.
    - Include any certifications, training, or qualifications mentioned in the resume.
    - Ensure cover_letter_insights reflect the candidate's genuine motivation and personality traits expressed in their cover letter.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
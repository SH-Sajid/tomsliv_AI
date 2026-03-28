from app.config import async_client
import json

async def generate_job_content(job_data: dict):
    """
    Generate full job description and benefits/perks based on the provided job information.
    
    Args:
        job_data: Dictionary containing basicInformation, jobDescription, workingInformation,
                  and optionally jobDescriptionText and benefitsAndPerksText
        
    Returns:
        Dictionary with fullJobDescription and benefitsAndPerks
    """
    
    # Extract user-provided context if available
    job_description_text = job_data.pop("jobDescriptionText", None)
    benefits_perks_text = job_data.pop("benefitsAndPerksText", None)
    
    # Build additional context section for the prompt
    additional_context = ""
    if job_description_text and job_description_text.strip():
        additional_context += f"\nUSER PROVIDED JOB DESCRIPTION CONTEXT:\n{job_description_text}\n"
    if benefits_perks_text and benefits_perks_text.strip():
        additional_context += f"\nUSER PROVIDED BENEFITS AND PERKS CONTEXT:\n{benefits_perks_text}\n"
    
    prompt = f"""
    Based on the following position details, please prepare a comprehensive and professional job description and benefits/remuneration summary suitable for publication to potential candidates.
    
    LANGUAGE REQUIREMENT: All output must be provided exclusively in professional New Zealand English (British/NZ spelling conventions).
    Apply the following employer-standard NZ English spelling throughout:
    • "organisation" not "organization"
    • "licence" not "license"
    • "programme" not "program"
    • "analyse" not "analyze"
    • "recognised" not "recognized"
    • "organised" not "organized"
    • "realise" not "realize"
    • "specialising" not "specializing"
    
    Maintain professional, employer-standard terminology and formal tone throughout. Do not use American English spellings.
    Ensure content reflects New Zealand employment practices and industry standards.

    Position Information:
    {json.dumps(job_data, indent=2)}{additional_context}

    Please create:
    1. A detailed, professional full job description (10-15 sentences) that includes:
       - Overview of the position and farm details
       - Key responsibilities and daily tasks
       - Required qualifications and physical requirements
       - Team structure and work environment
       - Learning and development opportunities
       {f"- Incorporate and expand upon the user-provided job description context above" if job_description_text else ""}

    2. A comprehensive benefits and perks description (5-7 sentences) that includes:
       - Remuneration details and competitive pay
       - Additional benefits (accommodation, work-life balance, etc.)
       - Professional development opportunities
       - Career advancement potential
       {f"- Incorporate and expand upon the user-provided benefits and perks context above" if benefits_perks_text else ""}

    Make the content engaging, professional, and specific to the farm details provided (farm size, herd size, work type, hours per week, etc.).
    {f"When user context is provided, use it as a foundation and enhance it with the structured job information." if (job_description_text or benefits_perks_text) else ""}

    Return a JSON object with this exact structure:
    {{
      "fullJobDescription": "Detailed job description here...",
      "benefitsAndPerks": {{
        "description": "Detailed benefits and perks description here..."
      }}
    }}
    """

    response = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
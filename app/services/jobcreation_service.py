from app.config import client
import json

def generate_job_content(job_data: dict):
    """
    Generate full job description and benefits/perks based on the provided job information.
    
    Args:
        job_data: Dictionary containing basicInformation, jobDescription, and workingInformation
        
    Returns:
        Dictionary with fullJobDescription and benefitsAndPerks
    """
    
    prompt = f"""
    Based on the following job information, generate a comprehensive job description and benefits/perks section.

    Job Information:
    {json.dumps(job_data, indent=2)}

    Please create:
    1. A detailed, professional full job description (10-15 sentences) that includes:
       - Overview of the position and farm details
       - Key responsibilities and daily tasks
       - Required qualifications and physical requirements
       - Team structure and work environment
       - Learning and development opportunities

    2. A comprehensive benefits and perks description (5-7 sentences) that includes:
       - Remuneration details and competitive pay
       - Additional benefits (accommodation, work-life balance, etc.)
       - Professional development opportunities
       - Career advancement potential

    Make the content engaging, professional, and specific to the farm details provided (farm size, herd size, work type, hours per week, etc.).

    Return a JSON object with this exact structure:
    {{
      "fullJobDescription": "Detailed job description here...",
      "benefitsAndPerks": {{
        "description": "Detailed benefits and perks description here..."
      }}
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
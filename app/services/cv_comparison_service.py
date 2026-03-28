from app.config import async_client
import json

async def compare_cvs(cv_a: dict, cv_b: dict, job_context: str = None):
    """
    Compare two CVs and provide detailed analysis of differences.
    
    Args:
        cv_a: Dictionary containing CV data for candidate A
        cv_b: Dictionary containing CV data for candidate B
        job_context: Optional job/team context for more accurate comparison
        
    Returns:
        Dictionary with comparison results
    """
    
    # Build the prompt with optional job context
    context_section = ""
    if job_context:
        context_section = f"""
    Job/Team Context:
    {job_context}
    
    Use this context to evaluate which candidate is better suited for the role.
    """
    
    prompt = f"""
    Please provide a comprehensive comparative analysis of both candidates' CVs, highlighting key differentiators, relative strengths, and suitability for the position.
    
    LANGUAGE REQUIREMENT: All output must be provided exclusively in professional New Zealand English (British/NZ spelling conventions).
    Apply the following employer-standard NZ English spelling throughout:
    • "analyse" not "analyze"
    • "organisation" not "organization"
    • "programme" not "program"
    • "recognised" not "recognized"
    • "organised" not "organized"
    • "licence" not "license"
    • "realise" not "realize"
    • "strategised" not "strategized"
    
    Maintain professional, employer-standard terminology and formal analytical tone. Do not use American English spellings.
    
    Candidate A - CV Details:
    {json.dumps(cv_a, indent=2)}
    
    Candidate B CV:
    {json.dumps(cv_b, indent=2)}
    {context_section}
    
    Provide a comprehensive comparison including:
    
    1. Overall Comparison: A summary paragraph (3-5 sentences) highlighting the key differences between both candidates, their experience levels, and overall suitability.
    
    2. Strengths of Candidate A: List 3-5 specific strengths that make candidate A stand out.
    
    3. Strengths of Candidate B: List 3-5 specific strengths that make candidate B stand out.
    
    4. Unique Skills of A: Skills, experiences, or qualifications that only candidate A possesses.
    
    5. Unique Skills of B: Skills, experiences, or qualifications that only candidate B possesses.
    
    6. Fit Comparison Score: A score from 0-100 indicating the comparative strength between candidates:
       - 50 = Both candidates are equally matched
       - Above 50 = Candidate A is stronger (60 = slightly stronger, 70 = moderately stronger, 80+ = significantly stronger)
       - Below 50 = Candidate B is stronger (40 = slightly stronger, 30 = moderately stronger, 20 or less = significantly stronger)
    
    Return a JSON object with this exact structure:
    {{
      "overallComparison": "Detailed summary comparing both candidates...",
      "strengthsA": ["strength 1", "strength 2", "strength 3"],
      "strengthsB": ["strength 1", "strength 2", "strength 3"],
      "uniqueSkillsA": ["unique skill 1", "unique skill 2"],
      "uniqueSkillsB": ["unique skill 1", "unique skill 2"],
      "fitComparisonScore": 50.0
    }}
    """

    response = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
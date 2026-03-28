from app.config import async_client

async def generate_summary(resume_text: str):
    prompt = f"""
    Please prepare a concise professional summary (2-3 sentences) of the candidate's qualifications and suitability for the position.
    The summary should be clear, concise, and provide a professional overview of the candidate's relevant experience and capabilities.
    
    LANGUAGE REQUIREMENT: All output must be provided exclusively in professional New Zealand English (British/NZ spelling conventions).
    Apply the following employer-standard NZ English spelling throughout:
    • "analyse" not "analyze"
    • "recognised" not "recognized"
    • "organised" not "organized"
    • "programme" not "program"
    • "licence" not "license"
    • "organisation" not "organization"
    • "realise" not "realize"
    
    Use formal, professional terminology suitable for employer documentation. Do not use American English spellings.

    Candidate's Resume:
    {resume_text}

    Return only the summary text, no JSON formatting needed.
    """

    response = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
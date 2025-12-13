from app.config import client

def generate_summary(resume_text: str):
    prompt = f"""
    Write a short, clear professional summary (2-3 sentences) about this candidate.
    The summary should be concise and highlight their key experience and suitability.
    Write it in a way that's easy to understand and gives a quick overview of the candidate.

    Resume:
    {resume_text}

    Return only the summary text, no JSON formatting needed.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
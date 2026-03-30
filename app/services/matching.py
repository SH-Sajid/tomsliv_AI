from app.config import async_client
import json

async def match_candidate(job_context: dict, resume_text: str):
    """
    Match candidate against job requirements and ideal candidate profile.
    
    TWO-PHASE APPROACH:
    Phase 1: AI extracts structured matching data with priority classification
    Phase 2: Python code calculates the score with weighted scoring (critical vs preferred)
    """
    
    job_details = job_context.get('job_details', {})
    ideal_candidate = job_context.get('ideal_candidate', {})
    
    has_ideal = bool(ideal_candidate)
    
    if has_ideal:
        ideal_candidate_prompt = f"Ideal Candidate Profile:\n{json.dumps(ideal_candidate, indent=2)}"
    else:
        ideal_candidate_prompt = "Ideal Candidate Profile: (Not provided)"

    # Build JSON template with priority field
    if has_ideal:
        json_template = """
    {
      "requirement_matches": [
        {
          "requirement": "requirement text",
          "priority": "critical",
          "match_level": "strong",
          "evidence": "specific CV evidence"
        }
      ],
      "ideal_trait_matches": [
        {
          "trait": "trait text",
          "matched": true,
          "evidence": "specific CV evidence or No evidence found"
        }
      ],
      "strengths": ["strength 1", "strength 2", "strength 3"],
      "areas_of_development": ["gap 1", "gap 2", "gap 3"],
      "candidate_name": "Name",
      "has_dairy_specific_experience": true,
      "has_relevant_certifications": true,
      "work_eligibility_mentioned": true
    }"""
    else:
        json_template = """
    {
      "requirement_matches": [
        {
          "requirement": "requirement text",
          "priority": "critical",
          "match_level": "strong",
          "evidence": "specific CV evidence"
        }
      ],
      "strengths": ["strength 1", "strength 2", "strength 3"],
      "areas_of_development": ["gap 1", "gap 2", "gap 3"],
      "candidate_name": "Name",
      "has_dairy_specific_experience": true,
      "has_relevant_certifications": true,
      "work_eligibility_mentioned": true
    }"""

    extraction_prompt = f"""
    You are a dairy farm recruitment analyst for New Zealand farms. Analyse the candidate's CV against the job and produce a structured matching report. Do NOT calculate any score.

    LANGUAGE: Use professional New Zealand English spelling throughout.

    === INPUTS ===

    Position Details:
    {json.dumps(job_details, indent=2)}

    {ideal_candidate_prompt}

    Candidate's CV and Cover Letter:
    {resume_text}

    === INSTRUCTIONS ===

    STEP 1: Extract COMPREHENSIVE requirements from the position details.
    You MUST extract AT LEAST 6 requirements by looking at ALL parts of the job details, not just the "requirements" field. Include:
    - Each explicitly listed requirement (from requirements array)
    - Job title relevance (does the candidate have experience in this SPECIFIC role type?)
    - Years/level of experience expected
    - Location suitability
    - Work type compatibility (full-time/part-time)
    - Any implied skills from the job title (e.g., "Dairy Farm Worker" implies dairy-specific knowledge)
    - Physical or practical requirements implied by the role
    - Qualifications or certifications expected in this industry

    STEP 1b: Classify each requirement by PRIORITY.
    For each requirement, assign a priority:
    - "critical": Requirements that are EXPLICITLY stated in the job listing (from requirements array), core job-specific skills directly tied to the job title, and location/work eligibility requirements. These are MUST-HAVE items.
    - "preferred": Requirements that are IMPLIED, generic, or nice-to-have. For example: general physical fitness, generic soft skills, work type compatibility, or certifications not explicitly demanded.

    IMPORTANT PRIORITY RULES:
    - Requirements taken DIRECTLY from the job listing's requirements array are ALWAYS "critical"
    - Skills that are specific to the job title (e.g., milking for a dairy worker) are "critical"
    - Generic requirements that ANY worker would need (physical fitness, teamwork, reliability) are "preferred"
    - Location suitability and work eligibility are "critical"
    - General certifications not explicitly requested are "preferred"

    STEP 2: Match each requirement against the CV.
    For each requirement, assign:
    - "strong": The CV has SPECIFIC, DETAILED evidence that DIRECTLY matches. Not vague — must be clearly demonstrated.
    - "partial": The CV shows RELATED experience but not an exact match. For example, general farming experience when dairy-specific is needed, or a skill is listed but not backed by detailed experience.
    - "none": No evidence at all in the CV.

    IMPORTANT MATCHING RULES:
    - A skill listed without supporting detail or work experience is "partial", NOT "strong"
    - General farming experience when dairy-specific is required is "partial", NOT "strong"  
    - If the CV only has 2 skills and a short work history, it CANNOT strongly match 6+ requirements
    - Be honest about what the CV actually demonstrates vs what it merely claims

    {"STEP 3: Check each ideal candidate trait against the CV independently. A trait is only matched if there is CLEAR evidence. Listing a skill name alone is NOT enough — there must be demonstrated experience or qualification." if has_ideal else ""}

    Return 3-5 strengths and 3-5 areas_of_development, each referencing specific CV content.

    Return this JSON structure (match_level must be exactly "strong", "partial", or "none"; priority must be exactly "critical" or "preferred"):
    {json_template}
    """

    response = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": extraction_prompt}],
        response_format={"type": "json_object"},
        temperature=0.2
    )

    analysis = json.loads(response.choices[0].message.content)

    # ============================
    # PHASE 2: Weighted score calculation
    # ============================
    
    requirements = analysis.get("requirement_matches", [])
    
    if requirements:
        total_points = 0
        max_points = 0

        for req in requirements:
            is_critical = req.get("priority", "preferred").lower().strip() == "critical"
            level = req.get("match_level", "none").lower().strip()
            
            if is_critical:
                # Critical requirements worth 3x more
                max_points += 15
                if level == "strong":
                    total_points += 15
                elif level == "partial":
                    total_points += 6
                # "none" = 0
            else:
                # Preferred requirements worth less
                max_points += 5
                if level == "strong":
                    total_points += 5
                elif level == "partial":
                    total_points += 2
                # "none" = 0

        # Scale to 0-82 range (without ideal candidate match, max score is 82)
        base_score = round((total_points / max_points) * 82) if max_points > 0 else 40

        # Critical-gap penalty: if most critical requirements are unmet, penalise heavily
        critical_reqs = [r for r in requirements if r.get("priority", "preferred").lower().strip() == "critical"]
        if critical_reqs:
            critical_none_count = sum(1 for r in critical_reqs if r.get("match_level", "none").lower().strip() == "none")
            if critical_none_count > len(critical_reqs) / 2:
                # More than half of critical requirements have no match — heavy penalty
                base_score = round(base_score * 0.6)
    else:
        base_score = 40

    # Small adjustments
    has_certs = analysis.get("has_relevant_certifications", False)
    work_elig = analysis.get("work_eligibility_mentioned", False)
    
    if has_certs and base_score < 78:
        base_score = min(base_score + 3, 82)
    
    if not work_elig and base_score > 30:
        base_score = max(base_score - 2, 25)
    
    base_score = max(base_score, 5)
    
    # Hard cap: without ideal candidate match, base score cannot exceed 82
    base_score = min(base_score, 82)
    
    # Ideal Candidate Bonus (0 to +8)
    ideal_bonus = 0
    matched_traits_count = 0
    total_traits_count = 0
    
    if has_ideal:
        ideal_traits = analysis.get("ideal_trait_matches", [])
        if ideal_traits:
            matched_traits_count = sum(1 for t in ideal_traits if t.get("matched", False))
            total_traits_count = len(ideal_traits)
            
            if total_traits_count > 0:
                match_ratio = matched_traits_count / total_traits_count
                ideal_bonus = round(match_ratio * 13)  # 0 to +13 bonus (can push score from 82 up to 95)
    
    final_score = min(base_score + ideal_bonus, 95)  # Cap at 95

    # Build natural explanation
    candidate_name = analysis.get("candidate_name", "The candidate")
    strengths = analysis.get("strengths", [])
    areas = analysis.get("areas_of_development", [])
    
    strong_count = sum(1 for r in requirements if r.get("match_level", "").lower().strip() == "strong")
    partial_count = sum(1 for r in requirements if r.get("match_level", "").lower().strip() == "partial")
    none_count = sum(1 for r in requirements if r.get("match_level", "").lower().strip() == "none")
    total_reqs = len(requirements)
    
    # Count critical vs preferred stats
    critical_reqs = [r for r in requirements if r.get("priority", "preferred").lower().strip() == "critical"]
    critical_strong = sum(1 for r in critical_reqs if r.get("match_level", "").lower().strip() == "strong")
    critical_total = len(critical_reqs)

    # Natural explanation (no base/bonus breakdown)
    explanation_parts = []
    
    if critical_total > 0:
        explanation_parts.append(f"{candidate_name} strongly meets {critical_strong} of {critical_total} critical job requirements")
    if strong_count > 0:
        explanation_parts.append(f"strongly matches {strong_count} of {total_reqs} total requirements")
    if partial_count > 0:
        explanation_parts.append(f"partially meets {partial_count}")
    if none_count > 0:
        explanation_parts.append(f"does not meet {none_count}")
    
    explanation = ", ".join(explanation_parts) + "."
    
    if has_ideal and ideal_bonus > 0:
        explanation += f" Additionally matched {matched_traits_count} of {total_traits_count} ideal candidate traits, which improved the overall score."
    elif has_ideal and ideal_bonus == 0:
        explanation += f" Did not match the ideal candidate traits, so the score reflects only job requirement alignment."

    # Build summary
    summary_parts = [f"{candidate_name} received a fit score of {final_score}."]
    
    if critical_total > 0:
        summary_parts.append(f"Of {critical_total} critical requirements, {critical_strong} were strongly matched.")
    if strong_count > 0:
        summary_parts.append(f"The candidate strongly matched {strong_count} of {total_reqs} total job requirements.")
    if partial_count > 0:
        summary_parts.append(f"{partial_count} requirement(s) were partially matched.")
    if none_count > 0:
        summary_parts.append(f"{none_count} requirement(s) had no matching evidence in the CV.")
    if has_ideal and ideal_bonus > 0:
        summary_parts.append(f"Matching {matched_traits_count} ideal candidate traits contributed additional points to the score.")
    elif has_ideal and ideal_bonus == 0:
        summary_parts.append("The ideal candidate traits were not matched, so no additional points were added.")
    
    summary = " ".join(summary_parts)

    return {
        "AI_fit_score": {
            "score": final_score,
            "explanation": explanation
        },
        "strengths": strengths if strengths else ["No specific strengths identified from the CV."],
        "areas_of_development": areas if areas else ["No specific development areas identified."],
        "summary": summary
    }
"""
services/matching_service.py
Resume–job description matching and skill gap analysis.
"""

from utils.text_utils import truncate_text, parse_json_from_llm, normalize_skill_name
from services.groq_service import call_groq


def analyze_resume_job_match(resume_info: dict, job_description: str) -> tuple[dict, str | None]:
    """
    Compare resume info against job description.

    Returns:
        (result_dict, error_message)
        result_dict keys:
            match_score: int (0–100)
            matching_skills: list of str
            missing_skills: list of {skill, reason, priority, is_essential}
            experience_match: str
            education_match: str
            summary: str
            recommendations: list of str
    """
    if not resume_info:
        return {}, "Resume information not available. Please upload a resume first."
    if not job_description or not job_description.strip():
        return {}, "Job description is empty."

    resume_skills = resume_info.get("skills", [])
    resume_projects = resume_info.get("projects", [])
    resume_experience = resume_info.get("experience", [])
    resume_education = resume_info.get("education", [])
    name = resume_info.get("name", "Candidate")

    truncated_jd = truncate_text(job_description, 2500)
    skills_str = ', '.join(resume_skills) if resume_skills else "Not specified"
    projects_str = '\n- '.join(resume_projects[:5]) if resume_projects else "None listed"
    experience_str = '\n- '.join(resume_experience[:5]) if resume_experience else "None listed"
    education_str = '\n- '.join(resume_education[:3]) if resume_education else "Not specified"

    system_prompt = """You are a career counselor and technical recruiter. Analyze resume-job fit accurately.
Be honest but constructive. Return valid JSON only."""

    prompt = f"""Analyze how well this candidate's resume matches the job description.

CANDIDATE PROFILE:
Name: {name}
Skills: {skills_str}
Education: {education_str}
Experience:
- {experience_str}
Projects:
- {projects_str}

JOB DESCRIPTION:
{truncated_jd}

Return JSON in exactly this format:
{{
  "match_score": <integer 0-100>,
  "matching_skills": ["skill1", "skill2", ...],
  "missing_skills": [
    {{
      "skill": "Skill Name",
      "reason": "Why this skill is needed for this role",
      "is_essential": true or false,
      "learning_priority": "High" or "Medium" or "Low",
      "suggested_resource": "Brief suggestion to learn this skill"
    }}
  ],
  "experience_match": "Brief assessment of experience alignment",
  "education_match": "Brief assessment of education alignment",
  "strengths": ["Strength 1", "Strength 2", ...],
  "summary": "2-3 sentence honest match summary",
  "recommendations": [
    "Specific actionable recommendation to improve this application"
  ]
}}

Scoring guide:
- Only list skills as "matching" if they genuinely appear in the candidate's profile
- Only list skills as "missing" if they appear or are implied in the job description
- Do NOT invent skills not present in either document
- Match score should reflect honest fit (skills + experience + education)

Return ONLY valid JSON."""

    response, error = call_groq(prompt, system_prompt, max_tokens=2000, temperature=0.3)

    if error:
        return _build_heuristic_match(resume_skills, job_description), None

    parsed = parse_json_from_llm(response)
    if not parsed or not isinstance(parsed, dict):
        return _build_heuristic_match(resume_skills, job_description), None

    result = {
        "match_score": max(0, min(100, int(parsed.get("match_score", 50)))),
        "matching_skills": parsed.get("matching_skills", []),
        "missing_skills": parsed.get("missing_skills", []),
        "experience_match": parsed.get("experience_match", "Unable to assess experience match."),
        "education_match": parsed.get("education_match", "Unable to assess education match."),
        "strengths": parsed.get("strengths", []),
        "summary": parsed.get("summary", "Match analysis completed."),
        "recommendations": parsed.get("recommendations", [])
    }

    return result, None


def _build_heuristic_match(resume_skills: list, job_description: str) -> dict:
    """Fallback matching using keyword overlap when LLM is unavailable."""
    jd_lower = job_description.lower()
    matching = [s for s in resume_skills if normalize_skill_name(s) in jd_lower]
    score = min(100, int((len(matching) / max(len(resume_skills), 1)) * 100)) if resume_skills else 0

    return {
        "match_score": score,
        "matching_skills": matching,
        "missing_skills": [],
        "experience_match": "Could not assess — AI analysis unavailable.",
        "education_match": "Could not assess — AI analysis unavailable.",
        "strengths": matching[:3],
        "summary": (
            f"Keyword-based analysis found {len(matching)} skill(s) in common with the job description. "
            "For detailed AI analysis, please configure your Groq API key."
        ),
        "recommendations": [
            "Configure Groq API for detailed AI-powered analysis.",
            "Review the job description requirements carefully.",
            "Highlight matching skills prominently in your application."
        ]
    }

"""
services/risk_service.py
Job scam / risk detection service using NLP heuristics + Groq LLM.
"""

import re
from utils.text_utils import truncate_text, parse_json_from_llm
from services.groq_service import call_groq


# ─────────────────────────────────────────────────────────────────────────────
# Heuristic red flag keywords (fast local check)
# ─────────────────────────────────────────────────────────────────────────────

RED_FLAG_PATTERNS = {
    "Registration/Application Fee": [
        r"registration fee", r"application fee", r"processing fee", r"joining fee",
        r"pay.*to (apply|register|join)", r"fee required", r"refundable deposit"
    ],
    "Money Request": [
        r"send money", r"transfer.*amount", r"pay.*before", r"payment required",
        r"pay.*upfront", r"invest.*to earn", r"buy.*kit", r"purchase.*materials"
    ],
    "Unrealistic Salary": [
        r"earn.*\d+.*lakh.*per (day|week)", r"\$\d{4,}.*per (day|week)",
        r"unlimited earning", r"earn up to.*crore", r"no experience.*high salary",
        r"freshers earn.*lakh"
    ],
    "Guaranteed Job/Income": [
        r"guaranteed (job|placement|income|salary)",
        r"100% (placement|job|hiring|selection)",
        r"assured (job|income|placement)"
    ],
    "Urgency/Pressure Tactics": [
        r"apply (immediately|now|asap|today only)",
        r"last \d+ (seat|spot|position)", r"hurry.*limited", r"offer (expires|ends) (today|soon)",
        r"respond (within|before) 24", r"urgent (hiring|requirement)"
    ],
    "Suspicious Contact": [
        r"whatsapp.*only", r"contact.*gmail\.com", r"yahoo\.com.*recruiter",
        r"no official (email|website)", r"personal (phone|whatsapp) for interview"
    ],
    "Missing Company Info": [
        r"confidential company", r"company name (not|cannot be) (disclosed|shared)",
        r"anonymous employer", r"location.*not (mentioned|provided)"
    ],
    "Too Good To Be True": [
        r"work from home.*high pay.*no experience",
        r"part time.*\d+ (lakh|crore|thousand).*(day|week|month)",
        r"easy (money|work|job).*high (salary|pay)",
        r"no (skill|experience|qualification) needed.*high"
    ],
    "Personal/Bank Info Request": [
        r"share (bank|account) (details|number|info)",
        r"send (aadhaar|pan|passport) (copy|number|scan).*upfront",
        r"credit card.*details",
        r"provide.*bank.*before (interview|joining)"
    ]
}


def check_heuristic_red_flags(job_description: str) -> dict[str, list[str]]:
    """
    Fast regex-based red flag detection (no API call needed).

    Returns:
        Dict mapping category name → list of matched snippets
    """
    found: dict[str, list[str]] = {}
    text_lower = job_description.lower()

    for category, patterns in RED_FLAG_PATTERNS.items():
        matches = []
        for pattern in patterns:
            hits = re.findall(pattern, text_lower)
            matches.extend(hits)
        if matches:
            found[category] = [m.strip() for m in matches[:3]]  # cap at 3 examples

    return found


def analyze_job_risk(job_description: str) -> tuple[dict, str | None]:
    """
    Full risk analysis: heuristic pass + LLM deep analysis.

    Returns:
        (result_dict, error_message)
        result_dict keys:
            risk_level: "LOW" | "MEDIUM" | "HIGH"
            risk_score: int (0–100)
            red_flags: list of {category, description, severity}
            safety_recommendations: list of str
            verification_checklist: list of str
            explanation: str
            disclaimer: str
    """
    if not job_description or not job_description.strip():
        return {}, "Job description is empty. Please paste a job description to analyze."

    # Step 1: Local heuristic check
    heuristic_flags = check_heuristic_red_flags(job_description)

    # Step 2: LLM deep analysis
    truncated_jd = truncate_text(job_description, 3000)

    system_prompt = """You are a job safety analyst helping college students identify risky or suspicious job postings.
You must NEVER definitively claim a job is a scam — use language like "Potential Risk", "Suspicious Indicator", "Needs Verification".
Always respond with valid JSON only."""

    prompt = f"""Analyze this job/internship posting for potential risks and suspicious indicators.

JOB POSTING:
{truncated_jd}

HEURISTIC FLAGS ALREADY DETECTED: {list(heuristic_flags.keys()) if heuristic_flags else "None"}

Analyze and return JSON in exactly this format:
{{
  "risk_level": "LOW" or "MEDIUM" or "HIGH",
  "risk_score": <integer 0-100>,
  "red_flags": [
    {{
      "category": "Category name",
      "description": "Clear explanation of why this is suspicious",
      "severity": "LOW" or "MEDIUM" or "HIGH",
      "matched_text": "quoted text from posting that triggered this flag"
    }}
  ],
  "positive_indicators": ["list of legitimate/trustworthy aspects of this posting"],
  "safety_recommendations": [
    "Actionable recommendation for the job seeker"
  ],
  "verification_checklist": [
    "Step to verify legitimacy"
  ],
  "explanation": "2-3 sentence overall assessment using cautious language like 'potential risk', 'suspicious indicator', 'appears to'"
}}

Risk scoring guide:
- 0-30: Mostly legitimate, minor concerns if any
- 31-60: Several suspicious indicators, verification recommended
- 61-100: Multiple high-severity red flags, exercise extreme caution

Return ONLY valid JSON. No markdown, no extra text."""

    response, error = call_groq(prompt, system_prompt, max_tokens=1800, temperature=0.3)

    if error:
        # If LLM fails, build result from heuristics only
        return _build_heuristic_result(heuristic_flags, job_description), None

    parsed = parse_json_from_llm(response)
    if not parsed or not isinstance(parsed, dict):
        return _build_heuristic_result(heuristic_flags, job_description), None

    # Ensure required keys
    result = {
        "risk_level": parsed.get("risk_level", "MEDIUM"),
        "risk_score": int(parsed.get("risk_score", 50)),
        "red_flags": parsed.get("red_flags", []),
        "positive_indicators": parsed.get("positive_indicators", []),
        "safety_recommendations": parsed.get("safety_recommendations", [
            "Research the company independently before applying.",
            "Never pay any fees to apply for a job.",
            "Verify recruiter identity through official company channels."
        ]),
        "verification_checklist": parsed.get("verification_checklist", [
            "Search for the company on LinkedIn and official directories.",
            "Verify the job posting on the company's official website.",
            "Check if recruiter email matches the official company domain.",
            "Search for reviews on Glassdoor or similar platforms."
        ]),
        "explanation": parsed.get("explanation", "AI assessment completed. Please review the findings carefully."),
        "disclaimer": (
            "⚠️ This is an AI-assisted assessment for awareness purposes only. "
            "It is NOT a legal or definitive determination. Always conduct your own due diligence."
        )
    }

    return result, None


def _build_heuristic_result(flags: dict, jd: str) -> dict:
    """Build a risk result from local heuristics when LLM is unavailable."""
    num_flags = len(flags)
    if num_flags == 0:
        risk_level, risk_score = "LOW", 15
    elif num_flags <= 2:
        risk_level, risk_score = "MEDIUM", 45
    else:
        risk_level, risk_score = "HIGH", 80

    red_flags_list = [
        {
            "category": cat,
            "description": f"Suspicious language detected matching '{cat}' pattern.",
            "severity": "MEDIUM",
            "matched_text": ", ".join(matches[:2])
        }
        for cat, matches in flags.items()
    ]

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "red_flags": red_flags_list,
        "positive_indicators": [],
        "safety_recommendations": [
            "Research the company independently before applying.",
            "Never pay any fees to apply for a job.",
            "Verify recruiter identity through official company channels.",
            "Use official job portals and company websites."
        ],
        "verification_checklist": [
            "Search for the company on LinkedIn.",
            "Verify the company has an official website.",
            "Check recruiter's email domain matches the company.",
            "Look for reviews on Glassdoor or AmbitionBox."
        ],
        "explanation": (
            f"Heuristic analysis detected {num_flags} potential risk indicator(s). "
            "AI deep analysis was unavailable. Please verify this posting manually."
        ),
        "disclaimer": (
            "⚠️ This is an AI-assisted assessment for awareness purposes only. "
            "It is NOT a legal or definitive determination."
        )
    }

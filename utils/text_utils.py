"""
utils/text_utils.py
Shared text processing helpers used across services.
"""

import re
import string


def clean_text(text: str) -> str:
    """Remove excessive whitespace and control characters from text."""
    if not text:
        return ""
    # Normalize newlines and tabs
    text = re.sub(r'\r\n|\r', '\n', text)
    # Remove multiple consecutive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove leading/trailing whitespace per line
    lines = [line.rstrip() for line in text.split('\n')]
    return '\n'.join(lines).strip()


def truncate_text(text: str, max_chars: int = 4000) -> str:
    """Truncate text to max_chars for LLM prompts to avoid token limits."""
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated for analysis]"


def extract_sections_heuristic(text: str) -> dict:
    """
    Heuristically split resume text into common sections.
    Returns dict with keys: skills, education, experience, projects, contact.
    """
    sections = {
        "skills": "",
        "education": "",
        "experience": "",
        "projects": "",
        "certifications": "",
        "contact": "",
        "raw": text
    }

    if not text:
        return sections

    # Common section header keywords (case-insensitive)
    section_patterns = {
        "skills": r"(skills?|technical skills?|core competencies|technologies)",
        "education": r"(education|academic background|qualifications)",
        "experience": r"(experience|work experience|employment|internship)",
        "projects": r"(projects?|personal projects?|academic projects?)",
        "certifications": r"(certifications?|certificates?|achievements?|awards?)",
        "contact": r"(contact|email|phone|linkedin|github)"
    }

    lines = text.split('\n')
    current_section = None
    section_content: dict[str, list] = {k: [] for k in sections if k != "raw"}

    for line in lines:
        line_lower = line.lower().strip()
        matched = False
        for section, pattern in section_patterns.items():
            if re.search(pattern, line_lower) and len(line.strip()) < 60:
                current_section = section
                matched = True
                break
        if not matched and current_section:
            section_content[current_section].append(line)

    for key, lines_list in section_content.items():
        sections[key] = '\n'.join(lines_list).strip()

    return sections


def normalize_skill_name(skill: str) -> str:
    """Normalize a skill name for comparison (lowercase, strip punctuation)."""
    return skill.lower().strip().strip(string.punctuation)


def parse_json_from_llm(text: str) -> dict | list | None:
    """
    Attempt to parse JSON from an LLM response that may contain markdown fences.
    Returns parsed object or None if parsing fails.
    """
    import json

    if not text:
        return None

    # Strip markdown code fences
    text = re.sub(r'```(?:json)?', '', text).replace('```', '').strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find a JSON object/array within the text
    for pattern in [r'\{.*\}', r'\[.*\]']:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                continue

    return None


def safe_int(value, default: int = 0) -> int:
    """Convert value to int safely."""
    try:
        return int(str(value).strip().replace('%', ''))
    except (ValueError, TypeError):
        return default

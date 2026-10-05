"""
services/interview_service.py
AI Mock Interview service: personalized question generation, live answer evaluation,
and comprehensive final performance report via Groq LLM.
"""

from utils.text_utils import truncate_text, parse_json_from_llm
from services.groq_service import call_groq


# ─────────────────────────────────────────────────────────────────────────────
# Question Generation
# ─────────────────────────────────────────────────────────────────────────────

def generate_interview_questions(resume_info: dict, job_description: str,
                                  num_questions: int = 8,
                                  missing_skills: list = None) -> tuple[list, str | None]:
    """
    Generate personalized mock interview questions based on:
    1. Uploaded Resume
    2. Target Job Description
    3. Candidate Skills
    4. Candidate Projects (e.g. 'AI Contract Intelligence')
    5. Missing skills / job requirements

    Returns:
        (questions_list, error_message)
        questions_list: list of {id, question, category, focus_area}
    """
    if not resume_info:
        return [], "Resume information required to generate personalized questions."
    if not job_description or not job_description.strip():
        return [], "Job description required to generate questions."

    name = resume_info.get("name", "the candidate") or "the candidate"
    skills = resume_info.get("skills", [])
    projects = resume_info.get("projects", [])
    experience = resume_info.get("experience", [])

    skills_str = ', '.join(skills[:12]) if skills else "Not specified"
    projects_str = '\n- '.join(projects[:5]) if projects else "None"
    experience_str = '\n- '.join(experience[:4]) if experience else "None"
    missing_str = ', '.join([m.get("skill", "") if isinstance(m, dict) else str(m) for m in (missing_skills or [])[:5]])
    truncated_jd = truncate_text(job_description, 2000)

    system_prompt = """You are an expert technical and hiring interviewer.
Generate personalized interview questions strictly tailored to the specific candidate's resume, projects, and target role.
Do NOT generate generic questions. Always return valid JSON only."""

    prompt = f"""Generate exactly {num_questions} personalized mock interview questions for this candidate.

CANDIDATE RESUME:
Name: {name}
Skills: {skills_str}
Projects:
- {projects_str}
Experience:
- {experience_str}
Potential Skill Gaps for this role: {missing_str or "None identified"}

TARGET JOB DESCRIPTION:
{truncated_jd}

QUESTION CATEGORIES & EXAMPLES TO MODEL:
1. Resume-based project questions:
   e.g. If candidate lists "AI Contract Intelligence", ask:
   "You mentioned an AI Contract Intelligence project. Can you explain how your system identifies contract risks and vector search retrieval?"
2. Skill-based questions:
   e.g. If candidate lists RAG, ask:
   "You listed RAG in your resume. Explain the difference between traditional search and Retrieval-Augmented Generation."
3. Job-based technical questions:
   e.g. If the role requires Python and ML, ask:
   "The role requires Python and scikit-learn. Explain how you would build and evaluate a classification model."
4. Architecture & challenge questions based on listed experience or projects.
5. HR & behavioral questions on career motivation and problem solving.

Return JSON in this exact format:
{{
  "questions": [
    {{
      "id": 1,
      "question": "The actual interview question text referencing actual candidate projects or skills",
      "category": "Resume-Based" or "Technical" or "Job-Specific" or "HR",
      "focus_area": "What this question assesses"
    }}
  ]
}}

Rules:
- Generate exactly {num_questions} questions.
- Reference actual project names, technologies, and tools from THIS resume.
- Ensure questions are open-ended and require substantive explanations.
- Return ONLY valid JSON."""

    response, error = call_groq(prompt, system_prompt, max_tokens=2200, temperature=0.5)

    if error:
        return _generate_fallback_questions(resume_info, job_description, num_questions), None

    parsed = parse_json_from_llm(response)
    if not parsed or "questions" not in parsed:
        return _generate_fallback_questions(resume_info, job_description, num_questions), None

    questions = parsed["questions"]
    if not isinstance(questions, list) or len(questions) == 0:
        return _generate_fallback_questions(resume_info, job_description, num_questions), None

    return questions[:num_questions], None


def _generate_fallback_questions(resume_info: dict, job_description: str, num: int) -> list:
    """Personalized fallback questions when Groq API is unavailable."""
    skills = resume_info.get("skills", [])
    projects = resume_info.get("projects", [])
    proj_name = projects[0] if projects else "your recent technical project"

    questions = [
        {
            "id": 1,
            "question": f"Can you walk me through your project: '{proj_name}'? What was your core architecture and what problem does it solve?",
            "category": "Resume-Based",
            "focus_area": "Project architecture and problem solving"
        },
        {
            "id": 2,
            "question": f"You listed {', '.join(skills[:3]) if skills else 'Python'} in your resume. Can you describe how you applied these tools in a production or research context?",
            "category": "Technical",
            "focus_area": "Technical skill depth"
        },
        {
            "id": 3,
            "question": "The job requires strong backend and machine learning problem solving. How do you approach debugging unexpected model behavior or latency bottlenecks?",
            "category": "Job-Specific",
            "focus_area": "System debugging and performance"
        },
        {
            "id": 4,
            "question": "Tell me about a technical challenge where your initial approach failed. How did you diagnose the issue and pivot?",
            "category": "HR",
            "focus_area": "Resilience and analytical approach"
        },
        {
            "id": 5,
            "question": f"In your work with {skills[1] if len(skills) > 1 else 'data engineering'}, how did you ensure data quality and validation?",
            "category": "Technical",
            "focus_area": "Data engineering and validation"
        },
        {
            "id": 6,
            "question": "How do you evaluate whether a complex AI solution (like an LLM or deep model) is necessary compared to a simpler heuristic or baseline?",
            "category": "Technical",
            "focus_area": "Pragmatic engineering judgment"
        },
        {
            "id": 7,
            "question": "Where do you see yourself contributing most to our engineering team in the first 90 days?",
            "category": "Job-Specific",
            "focus_area": "Team impact and onboarding"
        },
        {
            "id": 8,
            "question": "Why does this specific role align with your long-term career aspirations in AI and software engineering?",
            "category": "HR",
            "focus_area": "Motivation and culture fit"
        }
    ]

    return questions[:num]


# ─────────────────────────────────────────────────────────────────────────────
# Answer Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_answer(question: str, answer: str, resume_info: dict,
                    category: str = "Technical",
                    job_description: str = "") -> tuple[dict, str | None]:
    """
    Evaluate a candidate's answer using Groq LLM across:
    - Relevance
    - Technical correctness
    - Communication & structure
    - Completeness
    - Alignment with job requirements

    Returns:
        (evaluation_dict, error_message)
    """
    if not answer or not answer.strip() or answer == "[Candidate skipped this question]":
        return {
            "score": 1,
            "technical_score": 1,
            "communication_score": 1,
            "relevance_score": 1,
            "resume_score": 1,
            "strengths": ["Attempted to advance through interview."],
            "improvements": ["No answer was recorded for this question. Provide specific technical details using the STAR method."],
            "suggested_better_answer": "Provide a complete structured response outlining Situation, Task, Action taken, and Results achieved.",
            "overall_feedback": "Question was skipped or left blank. Practice answering directly to demonstrate technical knowledge."
        }, None

    skills_str = ', '.join(resume_info.get("skills", [])[:10]) if resume_info else ""

    system_prompt = """You are an objective, constructive technical and hiring interviewer.
Evaluate ONLY the content, technical correctness, clarity, completeness, and relevance of the candidate's answer.
Never judge appearance, accent, gender, or personal identity.
Always respond with valid JSON only."""

    prompt = f"""Evaluate this interview answer:

QUESTION: {question}
CATEGORY: {category}
CANDIDATE SKILLS: {skills_str}
TARGET JOB CONTEXT: {truncate_text(job_description, 500) if job_description else "General Software/AI Role"}

CANDIDATE'S ANSWER:
{truncate_text(answer, 1800)}

Evaluate and return JSON in this exact format:
{{
  "score": <overall score integer 1-10>,
  "technical_score": <integer 1-10, technical accuracy and correctness>,
  "communication_score": <integer 1-10, articulation, structure, and clarity>,
  "relevance_score": <integer 1-10, direct relevance to the question asked>,
  "resume_score": <integer 1-10, demonstration of knowledge claimed in resume or projects>,
  "strengths": [
    "Specific thing the candidate did well in this answer"
  ],
  "improvements": [
    "Actionable thing the candidate should add or improve"
  ],
  "suggested_better_answer": "A concise, high-scoring model answer (3-5 sentences) demonstrating how to best answer this question using the STAR method or clear technical specifics",
  "overall_feedback": "2-3 sentences of constructive feedback"
}}

Evaluation criteria:
- Score 1-4: Incomplete, vague, or contains technical inaccuracies
- Score 5-6: Acceptable baseline answer but lacks technical depth or metrics
- Score 7-8: Good, concrete answer with specific tools, steps, and results
- Score 9-10: Exceptional, articulate response with architecture details, tradeoffs, and impact
- Provide concrete strengths and improvements based on the actual text submitted.
- Return ONLY valid JSON."""

    response, error = call_groq(prompt, system_prompt, max_tokens=1400, temperature=0.3)
    if error:
        return _basic_evaluation(answer, question), None

    parsed = parse_json_from_llm(response)
    if not parsed or not isinstance(parsed, dict):
        return _basic_evaluation(answer, question), None

    def clamp(v, default=5):
        try:
            return max(1, min(10, int(v)))
        except (ValueError, TypeError):
            return default

    result = {
        "score": clamp(parsed.get("score", 5)),
        "technical_score": clamp(parsed.get("technical_score", 5)),
        "communication_score": clamp(parsed.get("communication_score", 5)),
        "relevance_score": clamp(parsed.get("relevance_score", 5)),
        "resume_score": clamp(parsed.get("resume_score", 5)),
        "strengths": parsed.get("strengths", ["Addressed the core topic of the question."]),
        "improvements": parsed.get("improvements", ["Provide more concrete metrics and architectural decisions."]),
        "suggested_better_answer": parsed.get("suggested_better_answer", (
            f"When answering '{question[:60]}...', clearly state the context, "
            "the specific tools you leveraged, the concrete steps you took, and measurable outcomes."
        )),
        "overall_feedback": parsed.get("overall_feedback", "Answer evaluated.")
    }

    return result, None


def _basic_evaluation(answer: str, question: str = "") -> dict:
    """Fallback evaluation when Groq LLM is temporarily unavailable."""
    word_count = len(answer.split())
    score = min(9, max(2, word_count // 18 + 2))
    return {
        "score": score,
        "technical_score": score,
        "communication_score": score,
        "relevance_score": score,
        "resume_score": score,
        "strengths": ["Answer was provided with initial context."] if word_count > 10 else ["Attempted response."],
        "improvements": [
            "Elaborate further with specific project metrics and architecture choices.",
            "Use the STAR method: Situation, Task, Action, Result."
        ],
        "suggested_better_answer": (
            "A strong answer should clearly state the context, "
            "detail the technical tools used, discuss challenges overcome, and highlight quantifiable results."
        ),
        "overall_feedback": "Answer recorded. Connect Groq API for full AI evaluation."
    }


# ─────────────────────────────────────────────────────────────────────────────
# Final Report Generation
# ─────────────────────────────────────────────────────────────────────────────

def generate_final_report(questions: list, evaluations: list,
                           resume_info: dict, job_description: str) -> tuple[dict, str | None]:
    """
    Generate the overall interview performance report card matching user specs:
    - Overall Score: XX/100
    - Technical Knowledge: XX/100
    - Communication: XX/100
    - Job Relevance: XX/100
    - Resume Knowledge: XX/100
    - Strengths
    - Areas to Improve
    - Questions to Practice
    - Recommended Preparation Topics
    - Final AI Feedback

    Returns:
        (report_dict, error_message)
    """
    if not evaluations:
        return {}, "No evaluations available to generate report."

    # Aggregate scores
    scores = [e.get("score", 5) for e in evaluations]
    avg_score = sum(scores) / len(scores) if scores else 5
    overall_pct = int((avg_score / 10) * 100)

    def avg_metric(key, default=50):
        vals = [e.get(key, 5) for e in evaluations if key in e]
        return int((sum(vals) / len(vals)) * 10) if vals else default

    category_scores = {
        "Technical Knowledge": avg_metric("technical_score", overall_pct),
        "Communication": avg_metric("communication_score", overall_pct),
        "Job Relevance": avg_metric("relevance_score", overall_pct),
        "Resume Knowledge": avg_metric("resume_score", overall_pct)
    }

    all_strengths = []
    all_improvements = []
    for e in evaluations:
        all_strengths.extend(e.get("strengths", []))
        all_improvements.extend(e.get("improvements", []))

    eval_summary = "\n".join([
        f"Q{i+1} ({q.get('category', 'General')}): Score {e.get('score', 5)}/10 - {e.get('overall_feedback', '')}"
        for i, (q, e) in enumerate(zip(questions, evaluations))
    ])

    system_prompt = "You are a senior technical career coach generating a final candidate interview evaluation report."

    prompt = f"""Synthesize a final candidate interview performance report:

EVALUATIONS ACROSS QUESTIONS:
{eval_summary}

CANDIDATE SKILLS: {', '.join(resume_info.get('skills', [])[:10]) if resume_info else 'General AI/ML'}
ROLE APPLIED FOR: {truncate_text(job_description, 300) if job_description else 'AI/ML Software Engineer'}

Return JSON in this exact structure:
{{
  "strong_areas": [
    "3-4 specific strengths demonstrated across the interview answers"
  ],
  "improvement_areas": [
    "3-4 prioritized areas where the candidate should improve"
  ],
  "recommendations": [
    "4-5 concrete preparation actions for upcoming live interviews"
  ],
  "practice_questions": [
    "3 specific technical or behavioral questions to practice again"
  ],
  "final_feedback": "3-4 sentences of executive summary assessing candidate readiness, strengths, and roadmap for success."
}}

Return ONLY valid JSON."""

    response, _ = call_groq(prompt, system_prompt, max_tokens=1500, temperature=0.4)
    parsed = parse_json_from_llm(response) if response else None

    report = {
        "overall_score": overall_pct,
        "category_scores": category_scores,
        "strong_areas": (parsed or {}).get("strong_areas", [s for s in all_strengths[:4] if s] or [
            "Demonstrated foundational understanding of core programming and data concepts.",
            "Articulated project context and technical responsibilities."
        ]),
        "improvement_areas": (parsed or {}).get("improvement_areas", [i for i in all_improvements[:4] if i] or [
            "Quantify results with business impact or model accuracy metrics.",
            "Explain algorithmic tradeoffs and edge-case handling in greater depth."
        ]),
        "recommendations": (parsed or {}).get("recommendations", [
            "Practice structuring behavioral and technical answers using the STAR method.",
            "Prepare deep-dive technical explanations for every project listed on your resume.",
            "Review core data structures, algorithms, and system design tradeoffs for the target role.",
            "Rehearse timed mock interviews to build communication conciseness."
        ]),
        "practice_questions": (parsed or {}).get("practice_questions", [
            q.get("question", "") for q in questions[:3] if q.get("question")
        ]),
        "final_feedback": (parsed or {}).get("final_feedback", (
            f"The candidate achieved an overall interview performance score of {overall_pct}%. "
            "Demonstrated good domain awareness with strong opportunities to elevate responses "
            "by incorporating quantitative results and discussing architectural tradeoffs."
        ))
    }

    return report, None

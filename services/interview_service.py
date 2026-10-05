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
                                  num_questions: int = 5,
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
        }
    ]
    return questions[:num]


# ─────────────────────────────────────────────────────────────────────────────
# Dynamic Conversational Interview Engine (No Pre-Generated Fixed Sequence)
# ─────────────────────────────────────────────────────────────────────────────

def generate_initial_interview_question(resume_info: dict, job_description: str = "",
                                        target_role: str = "") -> tuple[dict, str | None]:
    """
    Generate the FIRST opening interview question tailored specifically to the candidate's
    featured resume project, skills, and target role.
    
    Returns:
        (question_dict, error_message)
    """
    name = (resume_info.get("name") if resume_info else None) or "Candidate"
    skills = (resume_info.get("skills") if resume_info else []) or ["Python", "Machine Learning"]
    projects = (resume_info.get("projects") if resume_info else []) or []
    first_proj = projects[0] if projects else None
    role = target_role or "AI/ML Software Engineer"

    system_prompt = """You are JobShield AI's lead technical interviewer conducting a live video-call mock interview.
Craft a warm, professional, and personalized opening greeting and first question.
You MUST greet the candidate by their name, reference the target role and their skills, and invite them to discuss their featured project.
Never use a generic placeholder or hardcode any fake candidate name.
Return valid JSON only."""

    prompt = f"""Generate the OPENING (First) spoken greeting and question for this candidate:

CANDIDATE:
Name: {name}
Target Role: {role}
Featured Project: {first_proj or "Technical project from resume"}
All Projects: {', '.join(projects[:3]) if projects else "None listed"}
Key Skills: {', '.join(skills[:6])}

TARGET JOB DESCRIPTION:
{truncate_text(job_description, 800) if job_description else role}

INSTRUCTIONS:
1. Greet the candidate warmly by their exact name: "{name}".
2. State that you reviewed their resume and the "{role}" role they are targeting.
3. Mention that you noticed their experience in {', '.join(skills[:3]) if skills else 'modern AI tools'}.
4. Ask them an opening technical question about their project "{first_proj or 'technical background'}" (e.g., what core problem they were solving, their architecture, or key technical challenge).
5. Keep it natural, conversational, and suitable to be spoken aloud.
6. Return JSON in this exact structure:
{{
  "question": "Hi {name}. I reviewed your resume and the {role} role you're targeting. I noticed that you have experience with {', '.join(skills[:3]) if skills else 'AI and software engineering'}. Let's start with your {first_proj or 'featured project'} project. Could you explain the main problem you were trying to solve and how your architecture addresses it?",
  "category": "Resume-Based",
  "focus_area": "Project Architecture & Problem Solving"
}}
"""

    response, error = call_groq(prompt, system_prompt, max_tokens=400, temperature=0.5)
    parsed = parse_json_from_llm(response) if response else None

    if parsed and isinstance(parsed, dict) and parsed.get("question"):
        return {
            "id": 1,
            "question": parsed["question"].strip(),
            "category": parsed.get("category", "Resume-Based"),
            "focus_area": parsed.get("focus_area", "Project Overview")
        }, None

    # Dynamic fallback greeting and question (Requirement 10)
    top_skills_str = ', '.join(skills[:3]) if skills else "Python and machine learning"
    if first_proj:
        q_text = f"Hi {name}. I reviewed your resume and the {role} role you're targeting. I noticed that you have experience with {top_skills_str}. Let's start with your '{first_proj}' project. Could you explain the main problem you were trying to solve and the architecture you designed?"
    else:
        q_text = f"Hi {name}. I reviewed your profile for the {role} position. I see strong foundations in {top_skills_str}. Could you tell me about a recent technical system you built and the main problem it was designed to solve?"

    return {
        "id": 1,
        "question": q_text,
        "category": "Resume-Based",
        "focus_area": "Project Architecture & Problem Solving"
    }, None


def generate_conversational_followup(
    conversation_history: list[dict],
    latest_answer: str,
    resume_info: dict,
    job_description: str = "",
    target_role: str = ""
) -> tuple[dict, str | None]:
    """
    True Live Conversational Interview Engine:
    Listens carefully to the candidate's answer, identifies key technologies, claims,
    architectural decisions, and statements, and generates a dynamic follow-up question
    derived directly from what the candidate said.
    
    Remembers the entire conversation history.
    
    Returns:
        (result_dict, error_message)
    """
    clean_ans = (latest_answer or "").strip()
    is_skipped = not clean_ans or clean_ans == "[Candidate skipped this question]"

    if is_skipped:
        # Candidate skipped this topic - pivot naturally
        projects = resume_info.get("projects", []) if resume_info else []
        skills = resume_info.get("skills", []) if resume_info else []
        turn_num = len(conversation_history) // 2 + 1
        return {
            "ai_acknowledgment": "No problem, let's pivot to a different topic.",
            "next_question": f"Let's talk about another area on your profile. How have you utilized {skills[turn_num % len(skills)] if skills else 'system design principles'} in your projects?",
            "category": "Technical",
            "focus_area": "Alternative Technical Skill",
            "turn_score": 3,
            "turn_strengths": ["Candidate navigated forward in the interview."],
            "turn_improvements": ["Prepare concise STAR-format summaries even for less familiar topics."]
        }, None

    # Format entire dialogue history for multi-turn conversational context
    history_transcript = []
    for turn in conversation_history:
        speaker = "Interviewer" if turn.get("role") in ["interviewer", "assistant"] else "Candidate"
        history_transcript.append(f"{speaker}: {turn.get('content', '')}")
    history_str = "\n".join(history_transcript[-8:])  # Keep up to last 8 turns for depth

    system_prompt = """You are a professional human-like interviewer conducting a live technical interview.
Do not follow a fixed question list.
Listen carefully to the candidate's answer.
Identify important technologies, claims, projects, decisions, and statements in the answer.
Ask a relevant follow-up question based on what the candidate actually said.
If the answer is incomplete, ask a clarification question.
If the answer is strong, increase the difficulty naturally.
If the answer is weak, ask a simpler probing question.
Maintain context throughout the conversation.
Do not repeat questions.
Do not ask unrelated questions.
The interview should feel like a natural conversation rather than a questionnaire."""

    role = target_role or "AI/ML Software Engineer"
    skills = resume_info.get("skills", []) if resume_info else []
    projects = resume_info.get("projects", []) if resume_info else []

    prompt = f"""You are actively conducting this live interview for the role of {role}.

CANDIDATE CONTEXT:
Key Skills: {', '.join(skills[:8])}
Resume Projects: {', '.join(projects[:3]) if projects else 'Technical Projects'}
Target Job Context: {truncate_text(job_description, 600) if job_description else role}

ENTIRE CONVERSATION HISTORY SO FAR:
{history_str}

CANDIDATE'S LATEST SUBMITTED ANSWER:
"{truncate_text(clean_ans, 1800)}"

YOUR TASK AS THE INTERVIEWER:
1. Identify specific technologies, libraries, algorithms, metrics, or architectural decisions the candidate explicitly named (e.g. ChromaDB, RAG, Random Forest, Docker, Streamlit, retrieval accuracy, latency, etc.).
2. Craft a brief, natural AI acknowledgment (1-2 sentences) directly referencing what they stated.
3. Formulate the NEXT dynamic follow-up question probing deeper into that specific claim or decision.
   - Example 1: If candidate said "I used ChromaDB and Groq", ask: "You mentioned ChromaDB. Why did you choose ChromaDB for your vector database over alternatives like FAISS or Pinecone?"
   - Example 2: If candidate said "Random forest reduces overfitting", ask: "You mentioned Random Forest reduces overfitting. Can you explain how the ensemble mechanism and bagging achieve that?"
   - Example 3: If candidate said "I built a RAG pipeline", ask: "How did you measure retrieval accuracy, and how did you prevent hallucinations in your generated answers?"
4. Ensure the follow-up question is natural, conversational, and directly connected to what they just said.
5. Provide a quick objective turn score (1-10), strengths, and improvements for the final report.

Return JSON in this EXACT structure:
{{
  "ai_acknowledgment": "Brief 1-2 sentence acknowledgment directly referencing what they explained (e.g. 'Good explanation. You highlighted using ChromaDB for semantic retrieval...').",
  "next_question": "The dynamic follow-up question derived directly from their answer.",
  "category": "Technical" or "Project-Based" or "Problem-Solving" or "Behavioral",
  "focus_area": "What the follow-up probes (e.g. Vector Database Tradeoffs)",
  "turn_score": <integer 1-10>,
  "turn_strengths": [
    "Specific positive technical point from their answer"
  ],
  "turn_improvements": [
    "One constructive improvement or missing technical detail"
  ]
}}
"""

    response, error = call_groq(prompt, system_prompt, max_tokens=850, temperature=0.35)
    parsed = parse_json_from_llm(response) if response else None

    if parsed and isinstance(parsed, dict) and parsed.get("next_question"):
        def clamp_score(v, default=6):
            try:
                return max(1, min(10, int(v)))
            except Exception:
                return default

        return {
            "ai_acknowledgment": parsed.get("ai_acknowledgment", "Thank you for explaining that.").strip(),
            "next_question": parsed.get("next_question", "").strip(),
            "category": parsed.get("category", "Technical"),
            "focus_area": parsed.get("focus_area", "Follow-up Probe"),
            "turn_score": clamp_score(parsed.get("turn_score", 6)),
            "turn_strengths": parsed.get("turn_strengths", ["Provided clear technical response to the question."]),
            "turn_improvements": parsed.get("turn_improvements", ["Deepen explanation with quantifiable metrics."])
        }, None

    # Heuristic dynamic fallback: Extract keywords from answer
    lower_ans = clean_ans.lower()
    if "rag" in lower_ans or "chroma" in lower_ans or "vector" in lower_ans or "retrieval" in lower_ans:
        ack = "You mentioned using retrieval mechanisms in your architecture."
        next_q = "How did you handle chunking strategies and irrelevant or hallucinated responses in your retrieval pipeline?"
        focus = "RAG Pipeline Robustness"
    elif "random forest" in lower_ans or "tree" in lower_ans or "classification" in lower_ans:
        ack = "Good point regarding tree-based ensemble methods."
        next_q = "How did you tune hyperparameters like tree depth and handle class imbalance in your training dataset?"
        focus = "Model Tuning & Imbalance"
    elif "streamlit" in lower_ans or "fastapi" in lower_ans or "api" in lower_ans or "docker" in lower_ans:
        ack = "Thanks for walking through your deployment and interface stack."
        next_q = "How did you manage application state, latency, and concurrency under multiple concurrent users?"
        focus = "Deployment & Scalability"
    elif "pytorch" in lower_ans or "tensorflow" in lower_ans or "neural" in lower_ans or "deep" in lower_ans:
        ack = "Solid overview of your deep learning pipeline."
        next_q = "What loss functions and optimization strategies did you utilize, and how did you prevent gradient issues?"
        focus = "Deep Learning Optimization"
    else:
        ack = "Thanks for walking me through that technical perspective."
        next_q = "Can you elaborate on a specific performance metric or trade-off you evaluated when validating that system?"
        focus = "Technical Trade-offs & Validation"

    return {
        "ai_acknowledgment": ack,
        "next_question": next_q,
        "category": "Technical",
        "focus_area": focus,
        "turn_score": max(4, min(9, len(clean_ans.split()) // 15 + 3)),
        "turn_strengths": ["Candidate articulated project context and key tools."],
        "turn_improvements": ["Elaborate further on quantifiable outcomes and architectural tradeoffs."]
    }, None


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
# Real Conversational Turn Evaluation & AI Spoken Response
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_conversational_turn(
    current_question: str,
    candidate_answer: str,
    resume_info: dict,
    job_description: str = "",
    question_num: int = 1,
    total_questions: int = 5,
    planned_next_question: str = None
) -> tuple[dict, str | None]:
    """
    Evaluate a candidate's spoken/submitted answer and generate a natural,
    conversational response and seamless transition to the next interview question.

    Returns:
        (eval_dict, error_message)
    """
    if not candidate_answer or not candidate_answer.strip() or candidate_answer == "[Candidate skipped this question]":
        is_last = (question_num >= total_questions)
        reply = "I understand you skipped this question. Let's move ahead." if not is_last else "That brings us to the end of our interview session. Let's inspect your overall results."
        return {
            "score": 2,
            "technical_score": 2,
            "communication_score": 2,
            "relevance_score": 2,
            "completeness_score": 1,
            "strengths": ["Attempted question and progressed through the interview."],
            "improvements": ["Provide a concrete answer using the STAR method (Situation, Task, Action, Result)."],
            "ai_conversational_reply": reply,
            "speech_text": reply + (" " + (planned_next_question or "") if not is_last else ""),
            "overall_feedback": "Question was skipped or left blank."
        }, None

    system_prompt = """You are an engaging, supportive, and technically rigorous AI interviewer conducting a real-time mock interview.
Your goal is two-fold:
1. Objectively evaluate the candidate's spoken answer across technical depth, correctness, relevance, and communication.
2. Formulate a warm, natural conversational acknowledgment (1-2 sentences) directly referencing what the candidate said (e.g., 'That is a solid explanation of RAG embeddings and chunking. Let us dive into latency...').
Never judge appearance, voice pitch, or background. Always return valid JSON only."""

    skills_str = ', '.join(resume_info.get("skills", [])[:8]) if resume_info else ""
    projects_str = ', '.join(resume_info.get("projects", [])[:3]) if resume_info else ""
    is_last = (question_num >= total_questions)

    prompt = f"""Evaluate this conversational interview turn (Question {question_num} of {total_questions}):

INTERVIEW QUESTION ASKED:
"{current_question}"

CANDIDATE'S SPOKEN/SUBMITTED ANSWER:
"{truncate_text(candidate_answer, 1800)}"

CONTEXT:
Candidate Skills: {skills_str}
Candidate Projects: {projects_str}
Role Applied For: {truncate_text(job_description, 300) if job_description else "Software/AI Engineer"}
Is Last Question: {is_last}
Planned Next Topic/Question: {planned_next_question or "Technical question on candidate experience or skills"}

Evaluate and return JSON in this exact structure:
{{
  "score": <integer 1-10 overall score>,
  "technical_score": <integer 1-10 technical depth and correctness>,
  "communication_score": <integer 1-10 clarity, structure, and articulation>,
  "relevance_score": <integer 1-10 direct alignment with question>,
  "completeness_score": <integer 1-10 completeness of explanation>,
  "strengths": [
    "Specific strength from this answer",
    "Another positive technical aspect"
  ],
  "improvements": [
    "One concrete improvement or missing nuance"
  ],
  "ai_conversational_reply": "A warm, natural 1-2 sentence conversational reply acknowledging what they said (e.g. 'That is a great explanation. You mentioned X, which is very relevant...').",
  "overall_feedback": "2 sentences summarizing the response quality."
}}

Rules:
- Score realistically: 1-4 weak/vague, 5-6 average, 7-8 solid, 9-10 exceptional.
- Keep strengths and improvements concise and direct.
- Return ONLY valid JSON."""

    response, error = call_groq(prompt, system_prompt, max_tokens=1000, temperature=0.35)
    if error:
        # Fallback evaluation
        word_count = len(candidate_answer.split())
        score = min(9, max(3, word_count // 15 + 2))
        ack = f"Thanks for sharing that perspective on {current_question[:40]}."
        return {
            "score": score,
            "technical_score": score,
            "communication_score": score,
            "relevance_score": score,
            "completeness_score": score,
            "strengths": ["Clear response provided with relevant domain terminology."],
            "improvements": ["Provide more quantifiable architectural metrics and tradeoffs."],
            "ai_conversational_reply": ack,
            "speech_text": ack,
            "overall_feedback": "Answer recorded successfully."
        }, None

    parsed = parse_json_from_llm(response)
    if not parsed or not isinstance(parsed, dict):
        base_eval = _basic_evaluation(candidate_answer, current_question)
        base_eval["ai_conversational_reply"] = "Thank you for that answer. Let's keep going."
        base_eval["speech_text"] = "Thank you for that answer."
        return base_eval, None

    def clamp(v, default=6):
        try:
            return max(1, min(10, int(v)))
        except (ValueError, TypeError):
            return default

    score = clamp(parsed.get("score", 6))
    reply = parsed.get("ai_conversational_reply", "Thank you for sharing your experience.")
    
    # Formulate speech text for optional browser Text-to-Speech
    speech_text = reply
    if not is_last and planned_next_question:
        speech_text += f" Next question: {planned_next_question}"

    result = {
        "score": score,
        "technical_score": clamp(parsed.get("technical_score", score)),
        "communication_score": clamp(parsed.get("communication_score", score)),
        "relevance_score": clamp(parsed.get("relevance_score", score)),
        "completeness_score": clamp(parsed.get("completeness_score", score)),
        "strengths": parsed.get("strengths", ["Addressed the core subject of the question."]),
        "improvements": parsed.get("improvements", ["Provide more concrete metrics and tradeoffs."]),
        "ai_conversational_reply": reply,
        "speech_text": speech_text,
        "overall_feedback": parsed.get("overall_feedback", "Answer evaluated.")
    }

    return result, None


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


def generate_final_interview_evaluation(
    conversation_history: list[dict],
    evaluations: list[dict],
    resume_info: dict,
    job_description: str = "",
    target_role: str = ""
) -> tuple[dict, str | None]:
    """
    Comprehensive End-of-Interview Evaluation synthesizing the ENTIRE conversational transcript:
    - Overall Score (0-100%)
    - Technical Knowledge (0-100%)
    - Communication (0-100%)
    - Relevance (0-100%)
    - Completeness (0-100%)
    - Problem Solving (0-100%)
    - Strengths (Key technical achievements & articulate explanations)
    - Areas to Improve (Prioritized growth targets)
    - Topics to Practice (Specific concepts & systems to prepare)
    - Personalized Feedback (Executive interview summary)
    """
    if not conversation_history and not evaluations:
        return {}, "No conversation history available to evaluate."

    # Format entire dialogue
    dialogue_lines = []
    for turn in conversation_history:
        speaker = "Interviewer" if turn.get("role") in ["interviewer", "assistant"] else "Candidate"
        dialogue_lines.append(f"{speaker}: {turn.get('content', '')}")
    dialogue_str = "\n".join(dialogue_lines)

    # Turn scores fallback calculation
    scores = [e.get("turn_score", e.get("score", 6)) for e in evaluations]
    avg_score = sum(scores) / len(scores) if scores else 6.0
    overall_pct = int(min(100, max(20, (avg_score / 10.0) * 100)))

    role = target_role or "AI/ML Software Engineer"
    skills = resume_info.get("skills", []) if resume_info else []

    system_prompt = """You are an executive technical interview evaluator and principal hiring director.
Analyze the candidate's entire multi-turn technical interview conversation comprehensively and objectively.
Return ONLY valid JSON."""

    prompt = f"""Conduct a comprehensive final evaluation of this complete technical interview for {role}:

CANDIDATE SKILLS: {', '.join(skills[:10])}
TARGET JOB CONTEXT: {truncate_text(job_description, 500) if job_description else role}

COMPLETE INTERVIEW CONVERSATION TRANSCRIPT:
{truncate_text(dialogue_str, 4500)}

EVALUATION RUBRIC:
1. Overall Score (0-100%): Synthesized assessment of readiness for this role.
2. Pillar Scores (0-100% each):
   - technical_knowledge: Depth, correctness, and architecture awareness.
   - communication: Clarity, structure, articulation, and conciseness.
   - relevance: How directly answers addressed the questions asked.
   - completeness: Full explanations with tools, methods, and outcomes.
   - problem_solving: Analytical thinking, tradeoff analysis, and engineering judgment.
3. Strengths: 3-5 concrete positive points demonstrated during this conversation.
4. Areas to Improve: 3-4 prioritized technical or communication weaknesses to address.
5. Topics to Practice: 3-4 specific topics, tools, or architectural concepts to study.
6. Personalized Feedback: 3-4 sentences of constructive executive coaching.

Return JSON in this EXACT structure:
{{
  "overall_score": <integer 0-100>,
  "technical_knowledge": <integer 0-100>,
  "communication": <integer 0-100>,
  "relevance": <integer 0-100>,
  "completeness": <integer 0-100>,
  "problem_solving": <integer 0-100>,
  "strengths": [
    "Specific strength with examples from their answers"
  ],
  "improvement_areas": [
    "Prioritized area for improvement"
  ],
  "topics_to_practice": [
    "Specific concept or technology to practice"
  ],
  "personalized_feedback": "3-4 sentences summarizing their interview performance and readiness."
}}
"""

    response, error = call_groq(prompt, system_prompt, max_tokens=1400, temperature=0.35)
    parsed = parse_json_from_llm(response) if response else None

    def clamp_pct(val, default):
        try:
            return max(10, min(100, int(val)))
        except Exception:
            return default

    if parsed and isinstance(parsed, dict):
        fin_overall = clamp_pct(parsed.get("overall_score"), overall_pct)
        return {
            "overall_score": fin_overall,
            "technical_knowledge": clamp_pct(parsed.get("technical_knowledge"), fin_overall),
            "communication": clamp_pct(parsed.get("communication"), fin_overall),
            "relevance": clamp_pct(parsed.get("relevance"), fin_overall),
            "completeness": clamp_pct(parsed.get("completeness"), fin_overall),
            "problem_solving": clamp_pct(parsed.get("problem_solving"), fin_overall),
            "category_scores": {
                "Technical Knowledge": clamp_pct(parsed.get("technical_knowledge"), fin_overall),
                "Communication": clamp_pct(parsed.get("communication"), fin_overall),
                "Relevance": clamp_pct(parsed.get("relevance"), fin_overall),
                "Completeness": clamp_pct(parsed.get("completeness"), fin_overall),
                "Problem Solving": clamp_pct(parsed.get("problem_solving"), fin_overall),
            },
            "strong_areas": parsed.get("strengths", [
                "Demonstrated domain understanding of machine learning and modern software tools.",
                "Articulated practical system components and design rationale."
            ]),
            "improvement_areas": parsed.get("improvement_areas", [
                "Incorporate quantifiable business impact and benchmark metrics into explanations.",
                "Explain architectural tradeoffs and alternative implementations in greater depth."
            ]),
            "topics_to_practice": parsed.get("topics_to_practice", [
                "System architecture, vector database indexing, and latency benchmarking.",
                "STAR method response structuring for open-ended technical questions."
            ]),
            "recommendations": parsed.get("topics_to_practice", [
                "Deep-dive into production deployment constraints and latency optimization.",
                "Practice STAR-structured answers for technical system walkthroughs."
            ]),
            "practice_questions": [
                "Explain the end-to-end retrieval and generation cycle in your RAG pipeline.",
                "How do you handle model drift, monitoring, and automated retraining in production?"
            ],
            "final_feedback": parsed.get("personalized_feedback", (
                f"Candidate achieved an overall score of {fin_overall}%. Exhibited solid foundational knowledge "
                "with strong potential to excel by detailing system bottlenecks, latency tradeoffs, and quantifiable results."
            ))
        }, None

    # Fallback when LLM is unavailable
    tech_score = clamp_pct(int(overall_pct * 1.02), overall_pct)
    comm_score = clamp_pct(int(overall_pct * 0.98), overall_pct)
    rel_score = clamp_pct(overall_pct, overall_pct)
    comp_score = clamp_pct(int(overall_pct * 0.95), overall_pct)
    ps_score = clamp_pct(overall_pct, overall_pct)

    return {
        "overall_score": overall_pct,
        "technical_knowledge": tech_score,
        "communication": comm_score,
        "relevance": rel_score,
        "completeness": comp_score,
        "problem_solving": ps_score,
        "category_scores": {
            "Technical Knowledge": tech_score,
            "Communication": comm_score,
            "Relevance": rel_score,
            "Completeness": comp_score,
            "Problem Solving": ps_score,
        },
        "strong_areas": [
            "Demonstrated domain awareness of core programming concepts and system architectures.",
            "Navigated technical discussion with relevant domain vocabulary."
        ],
        "improvement_areas": [
            "Quantify results with precision metrics, latency benchmarks, or user adoption stats.",
            "Explain architectural tradeoffs and why specific alternatives were rejected."
        ],
        "topics_to_practice": [
            "RAG indexing strategies, chunking mechanisms, and vector database evaluation.",
            "System design, API concurrency, and containerized deployment pipelines."
        ],
        "recommendations": [
            "Structure answers strictly with the STAR format (Situation, Task, Action, Result).",
            "Prepare detailed trade-off justifications for all tools listed on your resume."
        ],
        "practice_questions": [
            "How do you evaluate retrieval precision and prevent hallucinations in production?",
            "What strategies do you use for profiling latency bottlenecks in AI applications?"
        ],
        "final_feedback": (
            f"Overall performance evaluated at {overall_pct}%. Candidate demonstrates good grasp of core concepts. "
            "Focus on quantifying project outcomes and discussing trade-offs to stand out to senior technical interviewers."
        )
    }, None

"""
test_conversational_turns.py
Verification script for Section 18:
Tests 3 consecutive conversational turns:
- Question 1 -> Answer A
- Follow-up B generated based on Answer A
- Answer B
- Follow-up C generated based on Answer B
- Answer C
- Follow-up D generated based on Answer C
- Final interview evaluation synthesizing the entire dialogue.
"""

from services.interview_service import (
    generate_initial_interview_question,
    generate_conversational_followup,
    generate_final_interview_evaluation
)

print("=" * 65)
print("TESTING TRUE CONVERSATIONAL MULTI-TURN AI MOCK INTERVIEW")
print("=" * 65)

resume_info = {
    "name": "Arjun Sharma",
    "skills": ["Python", "ChromaDB", "Groq", "RAG", "LangChain", "FastAPI"],
    "projects": ["Government Scheme RAG Assistant: Built retrieval assistant for citizens using ChromaDB and Groq"],
    "experience": ["AI Engineering Intern"],
    "education": ["B.Tech Computer Science"]
}

job_desc = "AI Engineer position requiring experience with RAG, vector databases, LLMs, and Python APIs."
target_role = "AI Engineer"

# 1. Opening Question
print("\n[Step 1] Generating Initial Opening Question...")
q1, err1 = generate_initial_interview_question(resume_info, job_desc, target_role)
assert err1 is None, f"Initial question failed: {err1}"
print(f"AI (Question 1): \"{q1['question']}\"")
assert len(q1["question"]) > 10, "Question must not be empty"

# Initialize conversation history
conversation_history = [
    {"role": "interviewer", "content": q1["question"]}
]
evaluations = []

# 2. Turn 1
# User speaks/transcribes Answer A mentioning ChromaDB and Groq
answer_a = "I developed a RAG based assistant using ChromaDB and Groq to answer citizen queries on government welfare programs."
print(f"\n[Turn 1] User Answer A:\n\"{answer_a}\"")

conversation_history.append({"role": "user", "content": answer_a})

followup_b, err_b = generate_conversational_followup(
    conversation_history, answer_a, resume_info, job_desc, target_role
)
assert err_b is None, f"Followup B error: {err_b}"
evaluations.append(followup_b)
print(f"\nAI Acknowledgment B: \"{followup_b.get('ai_acknowledgment')}\"")
print(f"AI Follow-up Question B: \"{followup_b.get('next_question')}\"")
print(f"Focus Area: {followup_b.get('focus_area')}")

# Verify Follow-up B relates to Answer A
lower_q_b = (followup_b.get("next_question", "") + " " + followup_b.get("ai_acknowledgment", "")).lower()
keywords_a = ["chroma", "rag", "vector", "database", "retriev", "groq", "citizen", "scheme", "embedding"]
matched_a = any(k in lower_q_b for k in keywords_a)
print(f"Verified connection to Answer A: {matched_a}")
assert matched_a, f"Follow-up B must connect to technologies in Answer A. Got: {followup_b.get('next_question')}"

conversation_history.append({"role": "interviewer", "content": followup_b.get("next_question")})

# 3. Turn 2
# User speaks/transcribes Answer B mentioning HNSW indexing and low latency
answer_b = "I selected ChromaDB specifically because of its lightweight SQLite and DuckDB backend with HNSW indexing, which kept search latency under 45 milliseconds for 50,000 document chunks."
print(f"\n[Turn 2] User Answer B:\n\"{answer_b}\"")

conversation_history.append({"role": "user", "content": answer_b})

followup_c, err_c = generate_conversational_followup(
    conversation_history, answer_b, resume_info, job_desc, target_role
)
assert err_c is None, f"Followup C error: {err_c}"
evaluations.append(followup_c)
print(f"\nAI Acknowledgment C: \"{followup_c.get('ai_acknowledgment')}\"")
print(f"AI Follow-up Question C: \"{followup_c.get('next_question')}\"")
print(f"Focus Area: {followup_c.get('focus_area')}")

# Verify Follow-up C relates to Answer B
lower_q_c = (followup_c.get("next_question", "") + " " + followup_c.get("ai_acknowledgment", "")).lower()
keywords_b = ["hnsw", "chunk", "latency", "index", "vector", "retriev", "scale", "search", "millisecond", "document"]
matched_b = any(k in lower_q_c for k in keywords_b)
print(f"Verified connection to Answer B: {matched_b}")
assert matched_b, f"Follow-up C must connect to concepts in Answer B. Got: {followup_c.get('next_question')}"

conversation_history.append({"role": "interviewer", "content": followup_c.get("next_question")})

# 4. Turn 3
# User speaks/transcribes Answer C about re-ranking and preventing hallucinations
answer_c = "To minimize hallucinations, I implemented a cross-encoder re-ranking stage and set a strict cosine similarity relevance cutoff of 0.78, prompting the LLM to state that information was unavailable if confidence was low."
print(f"\n[Turn 3] User Answer C:\n\"{answer_c}\"")

conversation_history.append({"role": "user", "content": answer_c})

followup_d, err_d = generate_conversational_followup(
    conversation_history, answer_c, resume_info, job_desc, target_role
)
assert err_d is None, f"Followup D error: {err_d}"
evaluations.append(followup_d)
print(f"\nAI Acknowledgment D: \"{followup_d.get('ai_acknowledgment')}\"")
print(f"AI Follow-up Question D: \"{followup_d.get('next_question')}\"")
print(f"Focus Area: {followup_d.get('focus_area')}")

# Verify Follow-up D relates to Answer C
lower_q_d = (followup_d.get("next_question", "") + " " + followup_d.get("ai_acknowledgment", "")).lower()
keywords_c = ["cross-encoder", "re-rank", "re rank", "hallucinat", "threshold", "cutoff", "confidence", "relevan", "evaluat", "similarity", "precision", "rag"]
matched_c = any(k in lower_q_d for k in keywords_c)
print(f"Verified connection to Answer C: {matched_c}")
assert matched_c, f"Follow-up D must connect to concepts in Answer C. Got: {followup_d.get('next_question')}"

# 5. Final Evaluation synthesizing the entire dialogue
print("\n[Step 5] Synthesizing Final Comprehensive Interview Evaluation...")
final_report, rep_err = generate_final_interview_evaluation(
    conversation_history=conversation_history,
    evaluations=evaluations,
    resume_info=resume_info,
    job_description=job_desc,
    target_role=target_role
)
assert rep_err is None, f"Final report error: {rep_err}"
print(f"Overall Score: {final_report.get('overall_score')}%")
print(f"Technical Knowledge: {final_report.get('technical_knowledge')}%")
print(f"Communication: {final_report.get('communication')}%")
print(f"Relevance: {final_report.get('relevance')}%")
print(f"Completeness: {final_report.get('completeness')}%")
print(f"Problem Solving: {final_report.get('problem_solving')}%")
print(f"Strengths: {final_report.get('strong_areas')[:2]}")
print(f"Areas to Improve: {final_report.get('improvement_areas')[:2]}")
print(f"Feedback: {final_report.get('final_feedback')[:100]}...")

print("\n" + "=" * 65)
print("SUCCESS: ALL 3 CONSECUTIVE CONVERSATIONAL TURNS AND FINAL REPORT PASSED!")
print("=" * 65)

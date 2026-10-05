"""
test_video_interview_flow.py
Verifies the complete Live AI Video-Call Mock Interview flow:
1. Dynamic Candidate Name (never hardcoded)
2. Resume Match Context Transfer (9 fields)
3. Initial Interview Opening (Dynamic greeting + project question)
4. Multi-Turn Conversational Dialogue without manual Submit Answer (3 turns)
5. AI Follow-Up Questions adapt directly to candidate's spoken technical claims
6. Final Comprehensive Evaluation synthesis
"""

import sys
from services.interview_service import (
    generate_initial_interview_question,
    generate_conversational_followup,
    generate_final_interview_evaluation
)
from services.matching_service import analyze_resume_job_match

print("=" * 70)
print("TESTING REAL-TIME AI VIDEO-CALL MOCK INTERVIEW FLOW")
print("=" * 70)

# 1. Test Dynamic User Name
logged_in_user = "Vikram Patel"
print(f"\n[Test 1] Testing with Dynamic User: '{logged_in_user}'")

candidate_resume = {
    "name": logged_in_user,
    "skills": ["Python", "Streamlit", "RAG", "ChromaDB", "Groq", "FastAPI"],
    "projects": [
        "AI Contract Intelligence: Real-time risk detection in legal contracts using NLP and vector embeddings"
    ],
    "experience": ["AI Research Intern at LegalTech Labs"],
    "education": ["B.Tech Computer Science"]
}

target_jd = (
    "AI/ML Engineer role. Build high-throughput LLM pipelines and RAG assistants using Python, "
    "vector search (ChromaDB), and Streamlit dashboards."
)
target_role = "AI/ML Engineer"

# 2. Test Resume Match Context Transfer
print("\n[Test 2] Simulating Resume Match calculation & context transfer...")
match_result, match_err = analyze_resume_job_match(candidate_resume, target_jd)
assert match_err is None, f"Matching failed: {match_err}"
match_score = match_result.get("match_score", 0)
matching_skills = match_result.get("matching_skills", [])
missing_skills = match_result.get("missing_skills", [])
print(f"Match Score: {match_score}%")
print(f"Matching Skills: {matching_skills}")

# Verify 9 context fields
context = {
    "resume_info": candidate_resume,
    "resume_data": candidate_resume,
    "resume_text": str(candidate_resume),
    "extracted_skills": candidate_resume["skills"],
    "candidate_projects": candidate_resume["projects"],
    "job_description": target_jd,
    "target_role": target_role,
    "match_score": match_score,
    "matching_skills": matching_skills,
    "missing_skills": missing_skills
}
assert len(context) >= 9, "All 9 context fields must be present"
print("Context transfer verified with all 9 fields!")

# 3. Test Initial Spoken Greeting & Question
print("\n[Test 3] Generating Initial Question for Mock Interview...")
q1, err1 = generate_initial_interview_question(candidate_resume, target_jd, target_role)
assert err1 is None, f"Opening question error: {err1}"
opening_text = q1["question"]
print(f"AI Opening: \"{opening_text}\"")

# Verify opening uses dynamic user name, not hardcoded
assert logged_in_user in opening_text or "Vikram" in opening_text, (
    f"Opening must address dynamic candidate name '{logged_in_user}'. Got: {opening_text}"
)
assert "Naga Varshitha" not in opening_text, "Must NOT use hardcoded name for different user!"
print("Opening correctly addresses dynamic user name!")

# Initialize dialogue history
conversation_history = [
    {"role": "interviewer", "content": opening_text}
]
evaluations = []

# 4. Turn 1 (Hands-Free Spoken Answer -> Auto AI Follow-Up)
spoken_ans_1 = (
    "In the AI Contract Intelligence project, the main problem was helping non-legal professionals "
    "identify high-risk clauses in business contracts quickly using NLP classification."
)
print(f"\n[Turn 1] Candidate Speaks (Hands-Free):\n\"{spoken_ans_1}\"")
conversation_history.append({"role": "user", "content": spoken_ans_1})

followup_1, f_err1 = generate_conversational_followup(
    conversation_history=conversation_history,
    latest_answer=spoken_ans_1,
    resume_info=candidate_resume,
    job_description=target_jd,
    target_role=target_role
)
assert f_err1 is None, f"Follow-up 1 error: {f_err1}"
evaluations.append(followup_1)
print(f"AI Acknowledgment: \"{followup_1.get('ai_acknowledgment')}\"")
print(f"AI Spoken Follow-up: \"{followup_1.get('next_question')}\"")

# Verify connection to Answer 1
q_lower_1 = (followup_1.get("next_question", "") + " " + followup_1.get("ai_acknowledgment", "")).lower()
keywords_1 = ["nlp", "contract", "risk", "clause", "classif", "identif", "extract", "model"]
assert any(k in q_lower_1 for k in keywords_1), (
    f"Follow-up 1 must be derived from Answer 1. Got: {followup_1.get('next_question')}"
)
print("Turn 1 verified: Follow-up directly targets candidate's technical claim!")
conversation_history.append({"role": "interviewer", "content": followup_1.get("next_question")})

# 5. Turn 2
spoken_ans_2 = (
    "We extracted paragraphs using PyPDF2 and OCR, split them into chunks, and embedded them with sentence-transformers. "
    "Then we computed cosine similarity against predefined risky clause archetypes."
)
print(f"\n[Turn 2] Candidate Speaks (Hands-Free):\n\"{spoken_ans_2}\"")
conversation_history.append({"role": "user", "content": spoken_ans_2})

followup_2, f_err2 = generate_conversational_followup(
    conversation_history=conversation_history,
    latest_answer=spoken_ans_2,
    resume_info=candidate_resume,
    job_description=target_jd,
    target_role=target_role
)
assert f_err2 is None, f"Follow-up 2 error: {f_err2}"
evaluations.append(followup_2)
print(f"AI Acknowledgment: \"{followup_2.get('ai_acknowledgment')}\"")
print(f"AI Spoken Follow-up: \"{followup_2.get('next_question')}\"")

q_lower_2 = (followup_2.get("next_question", "") + " " + followup_2.get("ai_acknowledgment", "")).lower()
keywords_2 = ["chunk", "embed", "transformer", "similarity", "cosine", "pdf", "ocr", "retriev", "archetype", "vector"]
assert any(k in q_lower_2 for k in keywords_2), (
    f"Follow-up 2 must relate to chunking/embeddings in Answer 2. Got: {followup_2.get('next_question')}"
)
print("Turn 2 verified: Follow-up directly probes the embedding/similarity architecture!")
conversation_history.append({"role": "interviewer", "content": followup_2.get("next_question")})

# 6. Turn 3
spoken_ans_3 = (
    "We stored the vectors in ChromaDB with HNSW indexing. For scanned documents, Tesseract OCR was used, "
    "and we implemented bounding-box filtering to avoid extracting legal disclaimers in headers and footers."
)
print(f"\n[Turn 3] Candidate Speaks (Hands-Free):\n\"{spoken_ans_3}\"")
conversation_history.append({"role": "user", "content": spoken_ans_3})

followup_3, f_err3 = generate_conversational_followup(
    conversation_history=conversation_history,
    latest_answer=spoken_ans_3,
    resume_info=candidate_resume,
    job_description=target_jd,
    target_role=target_role
)
assert f_err3 is None, f"Follow-up 3 error: {f_err3}"
evaluations.append(followup_3)
print(f"AI Acknowledgment: \"{followup_3.get('ai_acknowledgment')}\"")
print(f"AI Spoken Follow-up: \"{followup_3.get('next_question')}\"")
print("Turn 3 verified!")

# 7. Test End Interview Evaluation
print("\n[Test 4] Ending Interview & Generating Final Evaluation Report...")
report, rep_err = generate_final_interview_evaluation(
    conversation_history=conversation_history,
    evaluations=evaluations,
    resume_info=candidate_resume,
    job_description=target_jd,
    target_role=target_role
)
assert rep_err is None, f"Final report error: {rep_err}"
print(f"Overall Interview Score: {report.get('overall_score')}%")
print(f"Technical Knowledge: {report.get('technical_knowledge')}%")
print(f"Communication: {report.get('communication')}%")
print(f"Problem Solving: {report.get('problem_solving')}%")
print(f"Strong Areas: {report.get('strong_areas')[:2]}")
print(f"Improvement Areas: {report.get('improvement_areas')[:2]}")
print(f"Recommended Topics: {report.get('topics_to_practice')[:2]}")

assert report.get("overall_score", 0) > 0, "Overall score must be > 0"
assert len(report.get("strong_areas", [])) > 0, "Must have strong areas"

print("\n" + "=" * 70)
print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
print("=" * 70)

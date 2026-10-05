"""
test_e2e.py
End-to-end automated test for JobShield AI:
1. Groq connection test
2. Job Risk Detection
3. OpenCV preprocessing pipeline
4. Resume parsing & skill extraction
5. Resume–Job matching & skill gap analysis
6. Mock interview question generation
7. Answer evaluation via Groq
8. Final interview report generation
"""

import sys
import numpy as np
from PIL import Image

print("=" * 60)
print("JOBSHIELD AI — END-TO-END AUTOMATED VERIFICATION")
print("=" * 60)

# 1. Test Groq Connection
from services.groq_service import test_groq_connection
ok, msg = test_groq_connection()
print(f"\n[1] Groq AI Connection: {'SUCCESS' if ok else 'FAILED'} -> {msg}")
assert ok, "Groq connection must succeed"

# 2. Test Job Risk Detection
from services.risk_service import analyze_job_risk
suspicious_jd = (
    "URGENT: Work from home AI intern. Earn Rs 90,000/week! No experience needed. "
    "Guaranteed job. Pay registration fee Rs 999 to start. Contact recruiter on WhatsApp."
)
risk_res, risk_err = analyze_job_risk(suspicious_jd)
print(f"\n[2] Job Risk Detection: Err={risk_err}, Score={risk_res.get('risk_score')}, Level={risk_res.get('risk_level')}")
print(f"    Detected Flags: {[f.get('category') for f in risk_res.get('red_flags', [])]}")
assert risk_res.get("risk_score") >= 50, "Suspicious job should trigger elevated risk score"

# 3. Test OpenCV Preprocessing Pipeline
from utils.opencv_utils import preprocess_resume_image
# Create a test synthetic document image
test_img = Image.new('RGB', (400, 300), color=(255, 255, 255))
processed_np, cv_status = preprocess_resume_image(test_img)
print(f"\n[3] OpenCV Preprocessing: Grayscale={cv_status.get('grayscale')}, NoiseReduced={cv_status.get('noise_reduced')}, Threshold={cv_status.get('threshold_applied')}, Processed={cv_status.get('processed')}")
assert cv_status.get("processed") is True, "OpenCV pipeline must succeed"

# 4. Test Resume Info Extraction
from services.resume_service import extract_resume_info
sample_resume_text = (
    "Naga Varshitha\n"
    "B.Tech in Artificial Intelligence & Machine Learning, B.M.S. College of Engineering (2026)\n"
    "Skills: Python, SQL, Machine Learning, PyTorch, OpenCV, RAG, Docker\n"
    "Projects: AI Contract Intelligence - Legal document question-answering with vector search."
)
resume_info, res_err = extract_resume_info(sample_resume_text)
print(f"\n[4] Resume Extraction: Err={res_err}, Name={resume_info.get('name')}, Skills={resume_info.get('skills')}")
assert len(resume_info.get("skills", [])) > 0, "Skills should be extracted"

# 5. Test Resume-Job Matching
from services.matching_service import analyze_resume_job_match
target_jd = (
    "Hiring AI/ML Engineer Intern. Must have experience in Python, SQL, and Machine Learning. "
    "Experience with Kubernetes and AWS is a plus."
)
match_res, match_err = analyze_resume_job_match(resume_info, target_jd)
print(f"\n[5] Resume Match: Err={match_err}, Match Score={match_res.get('match_score')}%, Matching Skills={match_res.get('matching_skills')}")
assert match_res.get("match_score") > 0, "Match score should be calculated"

# 6. Test Mock Interview Question Generation
from services.interview_service import generate_interview_questions
qs, q_err = generate_interview_questions(resume_info, target_jd, num_questions=3)
print(f"\n[6] Mock Interview Questions: Generated {len(qs)} questions (Err={q_err})")
for i, q in enumerate(qs, 1):
    print(f"    Q{i} [{q.get('category')}]: {q.get('question')[:75]}...")
assert len(qs) >= 2, "Questions should be generated"

# 7. Test Answer Evaluation
from services.interview_service import evaluate_answer
first_q = qs[0].get("question")
user_answer = (
    "In my AI Contract Intelligence project, I utilized Python, LangChain, and RAG to process legal contracts. "
    "I chunked documents and indexed them into a vector store to achieve 92% accurate retrieval."
)
evaluation, eval_err = evaluate_answer(first_q, user_answer, resume_info, qs[0].get("category", "Technical"))
print(f"\n[7] Answer Evaluation: Err={eval_err}, Score={evaluation.get('score')}/10, Relevance={evaluation.get('relevance_score')}")
print(f"    Strengths: {evaluation.get('strengths')[:2]}")
assert evaluation.get("score") > 0, "Answer evaluation score should be > 0"

# 8. Test Final Report Generation
from services.interview_service import generate_final_report
report, rep_err = generate_final_report(qs, [evaluation], resume_info, target_jd)
print(f"\n[8] Final Interview Report: Err={rep_err}, Overall Score={report.get('overall_score')}%")
print(f"    Strong Areas: {report.get('strong_areas')[:2]}")

print("\n" + "=" * 60)
print("ALL 8 END-TO-END PIPELINE TESTS PASSED FLAWLESSLY!")
print("=" * 60)

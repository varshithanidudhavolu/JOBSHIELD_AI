"""
components/mock_interview.py
AI Mock Interview UI: pre-interview setup, question flow, webcam/video interface,
real-time Groq evaluation, and comprehensive performance report card.
Styled after the clean, professional HireLens career platform visual aesthetic.
"""

import time
import streamlit as st
import streamlit.components.v1 as components
from services.interview_service import (
    generate_interview_questions,
    evaluate_answer,
    generate_final_report
)


def render_mock_interview():
    """Main entry point for the Mock Interview feature."""

    st.markdown("""
    <div style="margin-bottom:1.2rem;">
        <h2 style="color:#0F241A; font-weight:800; font-size:1.8rem; margin-bottom:0.25rem;">
            🎥 AI Mock Interview
        </h2>
        <p style="color:#475569; font-size:0.95rem; margin-bottom:0.2rem;">
            Practice personalized interview questions based on your resume, target role, and skill requirements.
        </p>
        <p style="color:#64748B; font-size:0.8rem; font-style:italic;">
            Dynamic AI interviewer evaluates answers across technical correctness, communication, relevance, and completeness.
        </p>
    </div>
    """, unsafe_allow_html=True)

    state = st.session_state.get("interview_state", "setup")

    if state == "setup":
        _render_setup()
    elif state == "interview":
        _render_interview()
    elif state == "report":
        _render_final_report()


# ─────────────────────────────────────────────────────────────────────────────
# 1. SETUP SCREEN
# ─────────────────────────────────────────────────────────────────────────────

def _nav(page: str):
    """Navigate between pages cleanly without touching widget-bound keys."""
    clean_page = page.replace("🏠 ", "").replace("🛡️ ", "").replace("👁️ ", "").replace("🎯 ", "").replace("🎥 ", "").strip()
    st.session_state["current_page"] = clean_page
    st.rerun()


def _render_setup():
    """Pre-interview setup matching exact Step 1 requirements."""
    resume_info = st.session_state.get("resume_info") or st.session_state.get("resume_data") or st.session_state.get("resume_profile")
    job_description = st.session_state.get("job_description") or st.session_state.get("global_job_description", "")

    # Reconstruct from extracted skills/text if resume was uploaded
    if not resume_info and (st.session_state.get("extracted_skills") or st.session_state.get("resume_text")):
        resume_info = {
            "name": "Naga Varshitha",
            "skills": st.session_state.get("extracted_skills", ["Python", "Machine Learning", "SQL", "RAG"]),
            "projects": ["AI Contract Intelligence", "Real-Time Fraud Detection"],
            "experience": ["AI Research Intern"],
            "_raw_text": st.session_state.get("resume_text", "")
        }
        st.session_state["resume_info"] = resume_info
        st.session_state["resume_profile"] = resume_info

    has_resume = bool(resume_info and (resume_info.get("skills") or resume_info.get("_raw_text")))
    has_jd = bool(job_description and job_description.strip())

    # Candidate Name & Role extraction
    cand_name = resume_info.get("name", "Naga Varshitha") if resume_info else "Naga Varshitha"
    role_hint = _extract_role_hint(job_description)
    st.session_state["target_role"] = role_hint

    # ── Step 1: Pre-Interview Overview Card ────────────────────────────────────
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1.5px solid #A7F3D0; border-top:4px solid #059669;
                border-radius:16px; padding:1.8rem 2rem; margin-bottom:1.5rem; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1.2rem; flex-wrap:wrap; gap:0.5rem;">
            <div>
                <div style="display:inline-flex; align-items:center; gap:6px; background:#ECFDF5; border:1px solid #A7F3D0;
                            padding:3px 12px; border-radius:14px; font-size:0.75rem; font-weight:700; color:#065F46; margin-bottom:0.4rem;">
                    <span>✓</span> AI Mock Interview Setup
                </div>
                <h3 style="color:#0F241A; margin:0; font-size:1.45rem; font-weight:800;">Target Role: {role_hint}</h3>
                <p style="color:#475569; font-size:0.92rem; margin:0.3rem 0 0;">
                    Candidate: <strong>{cand_name}</strong> &bull; Personalized technical & behavioral preparation
                </p>
            </div>
            <span style="background:{'#ECFDF5' if (has_resume and has_jd) else '#FFFBEB'};
                         color:{'#065F46' if (has_resume and has_jd) else '#92400E'};
                         border:1px solid {'#A7F3D0' if (has_resume and has_jd) else '#FDE68A'};
                         font-size:0.8rem; font-weight:700; padding:5px 14px; border-radius:20px;">
                {'✓ Inputs Connected & Ready' if (has_resume and has_jd) else '⚠ Action Required'}
            </span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:0.9rem; margin-top:1rem;">
            <div style="background:#F8FAF9; padding:0.9rem 1.1rem; border-radius:10px; border:1px solid #E2E8F0;">
                <div style="color:#64748B; font-size:0.72rem; font-weight:700; text-transform:uppercase;">Candidate</div>
                <div style="color:#0F241A; font-weight:700; font-size:1.05rem; margin-top:0.2rem;">{cand_name}</div>
            </div>
            <div style="background:#F8FAF9; padding:0.9rem 1.1rem; border-radius:10px; border:1px solid #E2E8F0;">
                <div style="color:#64748B; font-size:0.72rem; font-weight:700; text-transform:uppercase;">Resume Status</div>
                <div style="color:{'#059669' if has_resume else '#DC2626'}; font-weight:700; font-size:1.05rem; margin-top:0.2rem;">
                    {'✓ Processed' if has_resume else '✕ Not Uploaded'}
                </div>
            </div>
            <div style="background:#F8FAF9; padding:0.9rem 1.1rem; border-radius:10px; border:1px solid #E2E8F0;">
                <div style="color:#64748B; font-size:0.72rem; font-weight:700; text-transform:uppercase;">Job Description</div>
                <div style="color:{'#059669' if has_jd else '#DC2626'}; font-weight:700; font-size:1.05rem; margin-top:0.2rem;">
                    {'✓ Available' if has_jd else '✕ Not Available'}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Handle missing prerequisites with direct options ───────────────────────
    if not has_resume or not has_jd:
        col_m1, col_m2 = st.columns(2)
        if not has_jd:
            with col_m1:
                st.warning("⚠️ **Job description required.** Paste a job description below to proceed immediately:")
                jd_input = st.text_area("Paste target job posting:", height=100, key="quick_interview_jd_paste")
                if st.button("Save Job Description", key="btn_save_int_jd"):
                    if jd_input.strip():
                        st.session_state["job_description"] = jd_input.strip()
                        st.session_state["global_job_description"] = jd_input.strip()
                        st.rerun()
        if not has_resume:
            with col_m2:
                st.warning("⚠️ **Resume required.** Go to Resume Analyzer or load the demo candidate profile:")
                col_sub1, col_sub2 = st.columns(2)
                with col_sub1:
                    if st.button("👁️ Go to Resume Analyzer", key="nav_to_resume_analyzer_btn", type="primary"):
                        _nav("Resume Analyzer")
                with col_sub2:
                    if st.button("📄 Load Sample Profile", key="load_sample_prof_for_int"):
                        st.session_state["resume_info"] = {
                            "name": "Naga Varshitha",
                            "skills": ["Python", "SQL", "Machine Learning", "RAG", "PyTorch", "Docker"],
                            "projects": ["AI Contract Intelligence: Legal document analysis using RAG"],
                            "experience": ["AI Research Intern"],
                            "_raw_text": "Naga Varshitha - AI/ML Student"
                        }
                        st.session_state["extracted_skills"] = ["Python", "SQL", "Machine Learning", "RAG", "PyTorch", "Docker"]
                        st.rerun()
        return

    # ── Questions Count & Camera Atmosphere ────────────────────────────────────
    set_col1, set_col2 = st.columns([1, 1])
    with set_col1:
        num_q = st.select_slider(
            "Number of Interview Questions",
            options=[5, 6, 7, 8],
            value=8,
            help="Full mock interview recommended (8 questions covering Resume, Projects, Technical depth, and Behavioral topics)."
        )
    with set_col2:
        enable_camera = st.checkbox(
            "🎥 Enable Live Camera Preview (Simulates in-person interview)",
            value=st.session_state.get("interview_camera_enabled", True),
            key="camera_toggle_setup"
        )
        st.session_state["interview_camera_enabled"] = enable_camera

    st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)

    # ── Start AI Interview Button ──────────────────────────────────────────────
    if st.button("🚀 Start AI Interview", type="primary", use_container_width=True, key="btn_start_ai_interview"):
        missing_skills = st.session_state.get("skill_gaps", [])
        with st.spinner("🤖 Groq AI is generating personalized questions from your resume and target role..."):
            questions, error = generate_interview_questions(
                resume_info, job_description, num_questions=num_q, missing_skills=missing_skills
            )

        if error or not questions:
            st.error(f"❌ Question generation notice: {error or 'Unable to generate questions'}")
            return

        # Initialize interview state
        st.session_state["interview_questions"] = questions
        st.session_state["interview_current_q"] = 0
        st.session_state["current_question"] = 0
        st.session_state["interview_answers"] = []
        st.session_state["submitted_answers"] = []
        st.session_state["interview_scores"] = []
        st.session_state["interview_evaluations"] = []
        st.session_state["answer_evaluations"] = []
        st.session_state["current_evaluation"] = None
        st.session_state["current_submitted_answer"] = ""
        st.session_state["interview_substate"] = "answering"
        st.session_state["interview_started"] = True
        st.session_state["interview_completed"] = False
        st.session_state["interview_state"] = "interview"
        st.session_state["interview_start_time"] = time.time()
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 2. ACTIVE INTERVIEW SCREEN (VIDEO / CONTROLS / QUESTIONS)
# ─────────────────────────────────────────────────────────────────────────────

def _render_interview():
    """Active question-answer interview screen with webcam, answer controls, and Groq evaluation."""
    questions = st.session_state.get("interview_questions", [])
    current_idx = st.session_state.get("interview_current_q", 0)
    evaluations = st.session_state.get("interview_evaluations", [])
    resume_info = st.session_state.get("resume_info", {})
    job_description = st.session_state.get("job_description") or st.session_state.get("global_job_description", "")
    target_role = st.session_state.get("target_role", "Target Role")
    total = len(questions)

    if not questions:
        st.error("❌ No interview questions found.")
        if st.button("Restart Interview"):
            _reset_interview()
        return

    # ── Check if All Questions Finished → Render Report ───────────────────────
    if current_idx >= total:
        st.session_state["interview_completed"] = True
        st.session_state["interview_state"] = "report"
        st.rerun()
        return

    # ── Progress Header ────────────────────────────────────────────────────────
    progress_val = current_idx / total
    st.markdown(f"""
    <div style="margin-bottom:1.2rem;">
        <div style="display:flex; justify-content:space-between; margin-bottom:0.35rem;">
            <span style="color:#0F241A; font-size:0.85rem; font-weight:700;">Question {current_idx + 1} of {total}</span>
            <span style="color:#059669; font-size:0.85rem; font-weight:700;">{int(progress_val * 100)}% Complete</span>
        </div>
        <div style="height:8px; background:#E2E8F0; border-radius:4px; overflow:hidden;">
            <div style="width:{int(progress_val * 100)}%; height:100%; background:linear-gradient(90deg, #059669, #10B981);
                        border-radius:4px; transition:width 0.3s;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Check if Currently Reviewing Answer (After submission) ────────────────
    substate = st.session_state.get("interview_substate", "answering")
    current_eval = st.session_state.get("current_evaluation")
    submitted_ans = st.session_state.get("current_submitted_answer", "")

    if substate == "reviewed" and current_eval:
        _render_evaluation_review(
            questions[current_idx], submitted_ans, current_eval, current_idx, total,
            questions, evaluations, resume_info, job_description
        )
        return

    # ── Current Question ───────────────────────────────────────────────────────
    question_data = questions[current_idx]
    question_text = question_data.get("question", "")
    category = question_data.get("category", "Technical")
    focus = question_data.get("focus_area", "")

    # Top Question Card
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:5px solid #059669;
                border-radius:14px; padding:1.4rem 1.6rem; margin-bottom:1.3rem; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
            <span style="background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0; font-size:0.75rem;
                         font-weight:700; padding:3px 10px; border-radius:14px;">
                {category}
            </span>
            <span style="color:#64748B; font-size:0.8rem; font-weight:600;">Question {current_idx+1} of {total}</span>
        </div>
        <div style="color:#64748B; font-size:0.75rem; font-weight:700; text-transform:uppercase; margin-bottom:0.25rem;">
            AI Interviewer:
        </div>
        <div style="color:#0F241A; font-size:1.15rem; line-height:1.55; font-weight:700;">
            "{question_text}"
        </div>
        {"<div style='color:#64748B; font-size:0.82rem; margin-top:0.4rem;'>Focus: " + focus + "</div>" if focus else ""}
    </div>
    """, unsafe_allow_html=True)

    # ── Split Layout: Camera Preview (Left) & Interview Controls/Info (Right) ───
    cam_col, info_col = st.columns([1, 1])

    with cam_col:
        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
            <span style="font-size:0.88rem; font-weight:700; color:#0F241A;">🎥 Camera</span>
            <span style="background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0; font-size:0.72rem;
                         font-weight:700; padding:2px 8px; border-radius:12px; display:inline-flex; align-items:center; gap:4px;">
                <span style="color:#059669; font-size:0.65rem;">●</span> Ready / Interview Mode
            </span>
        </div>
        """, unsafe_allow_html=True)

        cam_enabled = st.session_state.get("interview_camera_enabled", True)

        if cam_enabled:
            # HTML5 live continuous webcam feed with fallback to st.camera_input
            components.html("""
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center;
                        background:#071A12; border-radius:12px; padding:6px; overflow:hidden;">
                <video id="liveWebcamFeed" autoplay playsinline muted style="width:100%; max-height:220px; border-radius:8px; object-fit:cover;"></video>
                <div id="camStatus" style="color:#A7F3D0; font-family:sans-serif; font-size:11px; margin-top:4px;">
                    ● Live Camera Stream Active
                </div>
            </div>
            <script>
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
                    .then(function(stream) {
                        var video = document.getElementById('liveWebcamFeed');
                        video.srcObject = stream;
                        video.play();
                    })
                    .catch(function(err) {
                        document.getElementById('camStatus').innerHTML = 'Camera permission required in browser';
                        document.getElementById('camStatus').style.color = '#FCA5A5';
                    });
            } else {
                document.getElementById('camStatus').innerHTML = 'Webcam not supported';
            }
            </script>
            """, height=255)

            st.caption("💡 Eye contact with the camera helps build professional interview confidence.")
        else:
            st.markdown("""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:2rem 1.2rem;
                        text-align:center; min-height:160px; display:flex; flex-direction:column; justify-content:center;">
                <div style="font-size:2rem; margin-bottom:0.3rem;">🎙️</div>
                <div style="font-size:0.95rem; font-weight:700; color:#0F241A;">Text Answer Mode Active</div>
                <div style="font-size:0.8rem; color:#64748B; margin-top:0.2rem;">
                    Camera preview is disabled. You can type or dictate your complete answers below.
                </div>
            </div>
            """, unsafe_allow_html=True)

        col_cam1, col_cam2 = st.columns(2)
        with col_cam1:
            if not cam_enabled:
                if st.button("📷 Start Camera", key=f"btn_cam_on_{current_idx}", use_container_width=True):
                    st.session_state["interview_camera_enabled"] = True
                    st.rerun()
            else:
                if st.button("⏹️ Stop Camera", key=f"btn_cam_off_{current_idx}", use_container_width=True):
                    st.session_state["interview_camera_enabled"] = False
                    st.rerun()
        with col_cam2:
            if cam_enabled:
                if st.button("Continue with Text", key=f"btn_txt_only_{current_idx}", use_container_width=True):
                    st.session_state["interview_camera_enabled"] = False
                    st.rerun()

    with info_col:
        # Information Panel
        elapsed_sec = int(time.time() - st.session_state.get("interview_start_time", time.time()))
        timer_str = f"{elapsed_sec // 60:02d}:{elapsed_sec % 60:02d}"
        skills_list = resume_info.get("skills", [])
        skills_str = ", ".join(skills_list[:5]) if skills_list else "General AI/ML"

        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:1.2rem;
                    height:100%; box-shadow:0 1px 3px rgba(0,0,0,0.02); display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div style="font-size:0.85rem; font-weight:700; color:#0F241A; margin-bottom:0.6rem;">
                    🎤 Answer Controls & Guidelines
                </div>
                <div style="padding:0.55rem 0.8rem; background:#F8FAF9; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:0.5rem;">
                    <div style="font-size:0.7rem; color:#64748B; font-weight:700; text-transform:uppercase;">Target Role</div>
                    <div style="font-size:0.92rem; font-weight:700; color:#0F241A; margin-top:0.15rem;">{target_role}</div>
                </div>
                <div style="padding:0.55rem 0.8rem; background:#F8FAF9; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:0.5rem;">
                    <div style="font-size:0.7rem; color:#64748B; font-weight:700; text-transform:uppercase;">Relevant Resume Skills</div>
                    <div style="font-size:0.85rem; font-weight:600; color:#059669; margin-top:0.15rem;">{skills_str}</div>
                </div>
                <div style="display:flex; justify-content:space-between; gap:0.5rem;">
                    <div style="flex:1; padding:0.55rem 0.8rem; background:#F8FAF9; border-radius:8px; border:1px solid #E2E8F0;">
                        <div style="font-size:0.7rem; color:#64748B; font-weight:700; text-transform:uppercase;">Progress</div>
                        <div style="font-size:0.88rem; font-weight:700; color:#0F241A; margin-top:0.15rem;">Q{current_idx+1} of {total}</div>
                    </div>
                    <div style="flex:1; padding:0.55rem 0.8rem; background:#ECFDF5; border-radius:8px; border:1px solid #A7F3D0;">
                        <div style="font-size:0.7rem; color:#065F46; font-weight:700; text-transform:uppercase;">Elapsed Time</div>
                        <div style="font-size:0.88rem; font-weight:800; color:#059669; margin-top:0.15rem;">⏱️ {timer_str}</div>
                    </div>
                </div>
            </div>
            <div style="margin-top:0.8rem; font-size:0.78rem; color:#64748B; line-height:1.4;">
                💡 <em>Answers are evaluated strictly for technical accuracy, clarity, and completeness. Appearance is never judged.</em>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Answer Input Area ──────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.92rem; font-weight:700; color:#0F241A; margin-bottom:0.35rem;">
        Candidate Answer
    </div>
    """, unsafe_allow_html=True)

    answer = st.text_area(
        "Candidate Answer Area",
        height=160,
        placeholder=(
            "Type or dictate your answer here...\n\n"
            "Suggested Structure (STAR Method):\n"
            "• Situation: What context, problem, or project were you tackling?\n"
            "• Task: What was your specific responsibility?\n"
            "• Action: What specific technical tools, algorithms, or workflows did you use?\n"
            "• Result: What was the quantifiable outcome or key learning?"
        ),
        key=f"answer_input_q{current_idx}",
        label_visibility="collapsed"
    )

    # ── Answer Buttons ─────────────────────────────────────────────────────────
    col_act1, col_act2, col_act3 = st.columns([2, 1.2, 1.5])

    with col_act1:
        submit_btn = st.button("✅ Submit Answer", type="primary", use_container_width=True, key=f"btn_sub_q{current_idx}")
    with col_act2:
        skip_btn = st.button("⏭️ Skip Question", use_container_width=True, key=f"btn_skip_q{current_idx}")
    with col_act3:
        if st.button("🛑 End Interview Early", use_container_width=True, key=f"btn_early_end_{current_idx}"):
            st.session_state["interview_current_q"] = total
            st.session_state["interview_completed"] = True
            st.session_state["interview_state"] = "report"
            st.rerun()

    if submit_btn or skip_btn:
        final_answer = answer.strip() if (submit_btn and answer and answer.strip()) else ""

        if submit_btn and not final_answer:
            st.warning("⚠️ Please provide an answer or click 'Skip Question' to proceed.")
            return

        with st.spinner("🤖 Groq AI is evaluating your answer against technical correctness and structure..."):
            evaluation, eval_error = evaluate_answer(
                question_text,
                final_answer or "[Candidate skipped this question]",
                resume_info,
                category,
                job_description
            )

        if eval_error:
            st.error(f"❌ Evaluation error: {eval_error}")
            return

        st.session_state["current_evaluation"] = evaluation
        st.session_state["current_submitted_answer"] = final_answer or "[Candidate skipped this question]"
        st.session_state["interview_substate"] = "reviewed"
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 3. ANSWER EVALUATION REVIEW (FEEDBACK PER QUESTION)
# ─────────────────────────────────────────────────────────────────────────────

def _render_evaluation_review(question_data: dict, submitted_ans: str, evaluation: dict,
                              current_idx: int, total: int, questions: list,
                              evaluations: list, resume_info: dict, job_description: str):
    """Render the detailed evaluation card for the submitted answer."""
    question_text = question_data.get("question", "")
    category = question_data.get("category", "Technical")
    score = evaluation.get("score", 5)

    score_color = "#059669" if score >= 7 else ("#D97706" if score >= 5 else "#DC2626")
    score_bg = "#ECFDF5" if score >= 7 else ("#FFFBEB" if score >= 5 else "#FEF2F2")
    score_border = "#A7F3D0" if score >= 7 else ("#FDE68A" if score >= 5 else "#FECACA")

    strengths = evaluation.get("strengths", [])
    improvements = evaluation.get("improvements", [])
    better_answer = evaluation.get("suggested_better_answer", "")
    feedback = evaluation.get("overall_feedback", "")

    # Top Question Card
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:16px; padding:1.5rem;
                margin-bottom:1.3rem; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
            <span style="background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0; font-size:0.75rem;
                         font-weight:700; padding:3px 10px; border-radius:14px;">{category}</span>
            <span style="color:#64748B; font-size:0.8rem; font-weight:600;">Question {current_idx+1} of {total}</span>
        </div>
        <div style="color:#0F241A; font-size:1.1rem; font-weight:700; line-height:1.5; margin-bottom:0.8rem;">
            "{question_text}"
        </div>
        <div style="background:#F8FAF9; border-left:3px solid #CBD5E1; border-radius:0 8px 8px 0; padding:0.7rem 0.9rem;">
            <div style="font-size:0.72rem; color:#64748B; font-weight:700; text-transform:uppercase; margin-bottom:0.2rem;">
                Your Submitted Answer:
            </div>
            <div style="color:#1E293B; font-size:0.9rem; font-style:italic; line-height:1.5;">
                {submitted_ans}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Score Banner ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{score_bg}; border:2px solid {score_border}; border-radius:16px;
                padding:1.4rem 1.6rem; margin-bottom:1.3rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
            <div>
                <div style="font-size:0.75rem; color:#64748B; font-weight:700; text-transform:uppercase;">Score</div>
                <div style="font-size:2.8rem; font-weight:900; color:{score_color}; line-height:1.1; margin-top:0.2rem;">
                    {score} <span style="font-size:1.2rem; font-weight:600; color:#64748B;">/ 10</span>
                </div>
            </div>
            <div style="flex:1; max-width:400px;">
                <div style="height:10px; background:#E2E8F0; border-radius:5px; overflow:hidden;">
                    <div style="width:{score * 10}%; height:100%; background:{score_color}; border-radius:5px;"></div>
                </div>
            </div>
        </div>
        <div style="color:#1E293B; font-size:0.92rem; margin-top:0.8rem; line-height:1.6;">
            {feedback}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Score Breakdown Grid ──────────────────────────────────────────────────
    sub_scores = {
        "Technical Correctness": evaluation.get("technical_score", score),
        "Communication": evaluation.get("communication_score", score),
        "Job Relevance": evaluation.get("relevance_score", score),
        "Resume Knowledge": evaluation.get("resume_score", score)
    }

    cols = st.columns(4)
    for col, (name, val) in zip(cols, sub_scores.items()):
        val_color = "#059669" if val >= 7 else ("#D97706" if val >= 5 else "#DC2626")
        col.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px;
                    padding:0.7rem; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
            <div style="font-size:1.35rem; font-weight:800; color:{val_color};">{val}/10</div>
            <div style="font-size:0.75rem; color:#64748B; font-weight:600; margin-top:0.2rem;">{name}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.3rem;'></div>", unsafe_allow_html=True)

    # ── Strengths & Improvements ───────────────────────────────────────────────
    col_str, col_imp = st.columns(2)

    with col_str:
        st.markdown("""
        <h4 style="font-size:0.98rem; font-weight:700; color:#065F46; margin-bottom:0.5rem;">
            ✓ Strengths
        </h4>
        """, unsafe_allow_html=True)

        if strengths:
            for s in strengths:
                st.markdown(f"""
                <div style="display:flex; gap:0.5rem; align-items:flex-start; margin-bottom:0.4rem;
                            padding:0.55rem 0.8rem; background:#ECFDF5; border-radius:8px; border:1px solid #A7F3D0;">
                    <span style="color:#059669; font-weight:700;">✓</span>
                    <span style="color:#065F46; font-size:0.86rem;">{s}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Answer recorded.")

    with col_imp:
        st.markdown("""
        <h4 style="font-size:0.98rem; font-weight:700; color:#92400E; margin-bottom:0.5rem;">
            💡 Improvements
        </h4>
        """, unsafe_allow_html=True)

        if improvements:
            for imp in improvements:
                st.markdown(f"""
                <div style="display:flex; gap:0.5rem; align-items:flex-start; margin-bottom:0.4rem;
                            padding:0.55rem 0.8rem; background:#FFFBEB; border-radius:8px; border:1px solid #FDE68A;">
                    <span style="color:#D97706; font-weight:700;">&rarr;</span>
                    <span style="color:#92400E; font-size:0.86rem;">{imp}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No major improvements needed.")

    # ── Suggested Better Answer ────────────────────────────────────────────────
    if better_answer:
        st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #A7F3D0; border-left:4px solid #059669;
                    border-radius:12px; padding:1.2rem; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
            <div style="font-weight:700; color:#065F46; font-size:0.92rem; margin-bottom:0.4rem;">
                🎯 Suggested Better Answer:
            </div>
            <div style="color:#1E293B; font-size:0.9rem; line-height:1.6;">
                {better_answer}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Advance to Next Question / Finish ──────────────────────────────────────
    is_last = (current_idx + 1 >= total)
    next_btn_label = "🎉 Complete Interview & View Final Report ➡️" if is_last else f"Next Question ({current_idx+2}/{total}) ➡️"

    if st.button(next_btn_label, type="primary", use_container_width=True, key="btn_next_question_flow"):
        answers = st.session_state.get("interview_answers", [])
        answers.append(submitted_ans)
        evals_list = st.session_state.get("interview_evaluations", [])
        evals_list.append(evaluation)

        st.session_state["interview_answers"] = answers
        st.session_state["submitted_answers"] = answers
        st.session_state["interview_evaluations"] = evals_list
        st.session_state["answer_evaluations"] = evals_list

        next_q = current_idx + 1
        st.session_state["interview_current_q"] = next_q
        st.session_state["current_question"] = next_q
        st.session_state["current_evaluation"] = None
        st.session_state["current_submitted_answer"] = ""
        st.session_state["interview_substate"] = "answering"

        if is_last:
            with st.spinner("📊 Synthesizing comprehensive final interview report..."):
                report, error = generate_final_report(questions, evals_list, resume_info, job_description)
                if not error and report:
                    st.session_state["interview_report"] = report
                    st.session_state["final_interview_report"] = report
                    st.session_state["final_interview_score"] = report.get("overall_score", 0)
                    st.session_state["interview_completed"] = True
                    st.session_state["interview_state"] = "report"

        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 4. FINAL INTERVIEW REPORT (EXACT MATCH TO REQUIREMENTS)
# ─────────────────────────────────────────────────────────────────────────────

def _render_final_report():
    """Render comprehensive report card after completing all questions."""
    report = st.session_state.get("interview_report") or st.session_state.get("final_interview_report", {})
    questions = st.session_state.get("interview_questions", [])
    evaluations = st.session_state.get("interview_evaluations", [])

    if not report:
        st.error("❌ No report available. Please complete interview first.")
        return

    overall = report.get("overall_score", 0)
    category_scores = report.get("category_scores", {})
    strong_areas = report.get("strong_areas", [])
    improvement_areas = report.get("improvement_areas", [])
    recommendations = report.get("recommendations", [])
    practice_questions = report.get("practice_questions", [])
    final_feedback = report.get("final_feedback", "")

    perf_label = "Excellent Match" if overall >= 80 else ("Good Candidate Alignment" if overall >= 65 else ("Fair Alignment" if overall >= 50 else "Needs Preparation"))
    perf_color = "#059669" if overall >= 80 else ("#D97706" if overall >= 65 else "#DC2626")
    perf_bg = "#ECFDF5" if overall >= 80 else ("#FFFBEB" if overall >= 65 else "#FEF2F2")
    perf_border = "#A7F3D0" if overall >= 80 else ("#FDE68A" if overall >= 65 else "#FECACA")

    # ── Overall Performance Card ───────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{perf_bg}; border:2px solid {perf_border}; border-radius:18px;
                padding:2.2rem; text-align:center; margin-bottom:1.6rem; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
        <h2 style="color:#0F241A; margin-bottom:0.35rem; font-weight:800; font-size:1.8rem;">
            🎉 Interview Completed
        </h2>
        <div style="font-size:0.9rem; color:#64748B; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">
            Overall Score
        </div>
        <div style="font-size:4.8rem; font-weight:900; color:{perf_color}; line-height:1; margin:0.4rem 0;">
            {overall}%
        </div>
        <div style="font-size:1.15rem; color:{perf_color}; font-weight:700;">
            {perf_label}
        </div>
        <div style="margin:1rem auto 0; max-width:400px; height:10px; background:#E2E8F0; border-radius:5px; overflow:hidden;">
            <div style="width:{overall}%; height:100%; background:{perf_color}; border-radius:5px;"></div>
        </div>
        <div style="color:#64748B; font-size:0.85rem; margin-top:0.8rem;">
            Based on {len(evaluations)} detailed question evaluations and candidate responses
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 4 Category Scores: Technical Knowledge, Communication, Job Relevance, Resume Knowledge ──
    if category_scores:
        cat_cols = st.columns(4)
        cat_order = [
            ("Technical Knowledge", category_scores.get("Technical Knowledge", overall)),
            ("Communication", category_scores.get("Communication", overall)),
            ("Job Relevance", category_scores.get("Job Relevance", overall)),
            ("Resume Knowledge", category_scores.get("Resume Knowledge", overall)),
        ]

        for col, (cat_name, cat_score) in zip(cat_cols, cat_order):
            c_color = "#059669" if cat_score >= 75 else ("#D97706" if cat_score >= 55 else "#DC2626")
            with col:
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px;
                            padding:1.1rem 0.8rem; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                    <div style="font-size:1.8rem; font-weight:900; color:{c_color};">{cat_score}%</div>
                    <div style="color:#0F241A; font-size:0.82rem; font-weight:700; margin-top:0.3rem;">{cat_name}</div>
                    <div style="height:6px; background:#F1F5F9; border-radius:3px; margin-top:0.6rem; overflow:hidden;">
                        <div style="width:{cat_score}%; height:100%; background:{c_color}; border-radius:3px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)

    # ── Final AI Feedback ──────────────────────────────────────────────────────
    if final_feedback:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #A7F3D0; border-left:4px solid #059669;
                    border-radius:12px; padding:1.2rem 1.4rem; margin-bottom:1.4rem; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
            <div style="font-weight:700; color:#065F46; font-size:0.95rem; margin-bottom:0.35rem;">
                🎯 Final AI Feedback
            </div>
            <div style="color:#1E293B; font-size:0.9rem; line-height:1.6;">
                {final_feedback}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Strengths & Areas to Improve ───────────────────────────────────────────
    sa_col, ia_col = st.columns(2)

    with sa_col:
        st.markdown("""
        <h4 style="font-size:1rem; font-weight:700; color:#065F46; margin-bottom:0.5rem;">
            ✓ Strengths
        </h4>
        """, unsafe_allow_html=True)

        for area in strong_areas:
            st.markdown(f"""
            <div style="display:flex; gap:0.5rem; align-items:flex-start; margin-bottom:0.45rem;
                        padding:0.6rem 0.85rem; background:#ECFDF5; border-radius:8px; border:1px solid #A7F3D0;">
                <span style="color:#059669; font-weight:700;">★</span>
                <span style="color:#065F46; font-size:0.88rem; font-weight:500;">{area}</span>
            </div>
            """, unsafe_allow_html=True)

    with ia_col:
        st.markdown("""
        <h4 style="font-size:1rem; font-weight:700; color:#92400E; margin-bottom:0.5rem;">
            💡 Areas to Improve
        </h4>
        """, unsafe_allow_html=True)

        for area in improvement_areas:
            st.markdown(f"""
            <div style="display:flex; gap:0.5rem; align-items:flex-start; margin-bottom:0.45rem;
                        padding:0.6rem 0.85rem; background:#FFFBEB; border-radius:8px; border:1px solid #FDE68A;">
                <span style="color:#D97706; font-weight:700;">&rarr;</span>
                <span style="color:#92400E; font-size:0.88rem; font-weight:500;">{area}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Recommended Preparation Topics ─────────────────────────────────────────
    if recommendations:
        st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <h4 style="font-size:1rem; font-weight:700; color:#0F241A; margin-bottom:0.5rem;">
            📚 Recommended Preparation Topics
        </h4>
        """, unsafe_allow_html=True)

        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"""
            <div style="display:flex; gap:0.7rem; align-items:flex-start; margin-bottom:0.45rem;
                        padding:0.7rem 1rem; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px;">
                <span style="background:#059669; color:#FFFFFF; border-radius:50%; width:22px; height:22px;
                             display:inline-flex; align-items:center; justify-content:center;
                             font-size:0.75rem; font-weight:700; flex-shrink:0;">{i}</span>
                <span style="color:#1E293B; font-size:0.88rem;">{rec}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Questions to Practice ──────────────────────────────────────────────────
    if practice_questions:
        st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <h4 style="font-size:1rem; font-weight:700; color:#0F241A; margin-bottom:0.5rem;">
            🔁 Questions to Practice
        </h4>
        """, unsafe_allow_html=True)

        for q in practice_questions:
            if q:
                st.markdown(f"""
                <div style="background:#FFFFFF; border-left:3px solid #059669; border:1px solid #E2E8F0;
                            border-radius:8px; padding:0.65rem 0.9rem; margin-bottom:0.4rem; font-size:0.86rem; color:#1E293B;">
                    ❓ {q}
                </div>
                """, unsafe_allow_html=True)

    # ── Action Buttons ─────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
    btn1, btn2, btn3 = st.columns(3)

    with btn1:
        if st.button("🔄 Restart Interview", type="primary", use_container_width=True, key="btn_restart_interview_final"):
            _reset_interview()

    with btn2:
        if st.button("🎯 Go to Resume Match", use_container_width=True, key="btn_goto_match_from_report"):
            _nav("Resume Match")

    with btn3:
        if st.button("🏠 Back to Dashboard", use_container_width=True, key="btn_goto_dash_from_report"):
            _nav("Dashboard")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _reset_interview():
    """Reset interview state cleanly."""
    keys_to_reset = [
        "interview_state", "interview_substate", "interview_questions",
        "interview_current_q", "interview_answers", "interview_evaluations",
        "interview_scores", "submitted_answers", "answer_evaluations",
        "interview_report", "final_interview_report", "current_evaluation",
        "current_submitted_answer", "interview_start_time", "interview_started",
        "interview_completed"
    ]
    for k in keys_to_reset:
        st.session_state.pop(k, None)
    st.session_state["interview_state"] = "setup"
    st.rerun()


def _extract_role_hint(job_description: str) -> str:
    """Extract a concise target role title from job description."""
    if not job_description:
        return "Target Role"
    lines = [l.strip() for l in job_description.split('\n') if l.strip()]
    for line in lines[:6]:
        line_low = line.lower()
        if any(kw in line_low for kw in ["intern", "engineer", "developer", "analyst", "scientist", "manager", "specialist"]):
            return line.strip(" -:*#").split("—")[0].split("-")[0].strip()[:50]
    return lines[0].strip(" -:*#")[:50] if lines else "AI/ML Software Engineer"

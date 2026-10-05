"""
components/dashboard.py
Home dashboard — Hero section, feature cards, connected workflow, and session overview.
Styled after the clean, professional HireLens career platform aesthetic.
"""

import streamlit as st
from services.groq_service import is_api_configured, test_groq_connection


def render_dashboard():
    """Render the main landing/home dashboard."""

    user_name = st.session_state.get("user_name", "Candidate")

    # ── Hero Section (HireLens Clean Career Platform Style) ─────────────────────
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:16px; padding:2rem 1.8rem;
                margin-bottom:1.8rem; box-shadow:0 1px 3px rgba(0,0,0,0.03); text-align:center;">
        <div style="display:inline-flex; align-items:center; gap:8px; background:#ECFDF5; border:1px solid #A7F3D0;
                    padding:4px 14px; border-radius:20px; font-size:0.8rem; font-weight:700; color:#065F46; margin-bottom:0.8rem;">
            <span>🛡️</span> AI Career Intelligence & Verification Platform
        </div>
        <div style="font-size:1.4rem; font-weight:700; color:#0F241A; margin-bottom:0.4rem;">
            Welcome, {user_name} 👋
        </div>
        <h1 style="font-size:2.4rem; font-weight:800; color:#0F241A; margin-bottom:0.35rem; letter-spacing:-0.02em;">
            JobShield AI
        </h1>
        <p style="font-size:1.1rem; color:#059669; font-weight:600; margin-bottom:0.6rem;">
            Analyze. Match. Prepare. Apply with confidence.
        </p>
        <p style="font-size:0.95rem; color:#475569; max-width:720px; margin:0 auto 0.4rem; line-height:1.6;">
            Understand job risks, compare your resume with job requirements, identify skill gaps, and practice personalized interviews using AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── AI Connection Quick Bar ────────────────────────────────────────────────
    status_col1, status_col2 = st.columns([3, 1])

    with status_col1:
        if is_api_configured():
            st.markdown("""
            <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:10px; padding:0.6rem 1rem;
                        display:flex; align-items:center; gap:8px;">
                <span style="color:#059669; font-weight:700; font-size:1rem;">✓</span>
                <span style="color:#065F46; font-size:0.88rem; font-weight:600;">Groq AI Connected &bull; Real-time LLM inference active</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:10px; padding:0.6rem 1rem;
                        display:flex; align-items:center; gap:8px;">
                <span style="color:#D97706; font-weight:700; font-size:1rem;">⚠</span>
                <span style="color:#92400E; font-size:0.88rem; font-weight:600;">Groq API Key Required in .env file &bull; Fallback heuristic mode ready</span>
            </div>
            """, unsafe_allow_html=True)

    with status_col2:
        if st.button("⚡ Test AI Connection", key="dash_test_ai_btn", use_container_width=True):
            with st.spinner("Testing Groq AI connection..."):
                ok, msg = test_groq_connection()
            if ok:
                st.success("✓ Groq API operational", icon=None)
            else:
                st.error(f"❌ {msg}", icon=None)

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # ── 4 Feature Cards (HireLens Clean Rounded Card Grid) ─────────────────────
    st.markdown("""
    <div style="margin-bottom:0.8rem;">
        <h3 style="font-size:1.15rem; font-weight:700; color:#0F241A; margin:0;">Platform Features</h3>
        <p style="font-size:0.85rem; color:#64748B; margin:0.15rem 0 0;">Four end-to-end intelligent career modules designed for student and applicant success.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    cards = [
        ("🛡️", "Job Risk Detection",
         "Identify suspicious indicators and potential risks in job postings before you apply.",
         "Job Risk Detection"),
        ("👁️", "Resume Analyzer",
         "Extract resume information using document processing, OpenCV and OCR.",
         "Resume Analyzer"),
        ("🎯", "Resume Match",
         "Compare your resume with the target job and identify skill gaps.",
         "Resume Match"),
        ("🎥", "Mock Interview",
         "Practice personalized interview questions based on your resume and target role.",
         "Mock Interview"),
    ]

    for col, (icon, title, desc, target_page) in zip([col1, col2, col3, col4], cards):
        with col:
            st.markdown(f"""
            <div style="
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-top: 3.5px solid #059669;
                border-radius: 14px;
                padding: 1.3rem 1.1rem;
                min-height: 185px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-shadow: 0 1px 3px rgba(0,0,0,0.03);
                margin-bottom: 0.6rem;
            ">
                <div>
                    <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">{icon}</div>
                    <div style="font-weight: 700; color: #0F241A; font-size: 0.98rem; margin-bottom: 0.4rem;">{title}</div>
                    <div style="color: #64748B; font-size: 0.82rem; line-height: 1.5;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Open {title} →", key=f"btn_open_{title}", use_container_width=True):
                st.session_state["current_page"] = target_page
                st.rerun()

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Live Session Milestones ────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom:0.8rem;">
        <h3 style="font-size:1.15rem; font-weight:700; color:#0F241A; margin:0;">Application Progress</h3>
        <p style="font-size:0.85rem; color:#64748B; margin:0.15rem 0 0;">Real-time persistence across your active evaluation workflow.</p>
    </div>
    """, unsafe_allow_html=True)

    has_jd = bool(st.session_state.get("job_description") or st.session_state.get("global_job_description"))
    has_resume_uploaded = bool(st.session_state.get("resume_file") or st.session_state.get("resume_info") or st.session_state.get("resume_text"))
    has_resume_processed = bool(st.session_state.get("resume_info") and (st.session_state.get("resume_info", {}).get("skills") or st.session_state.get("extracted_skills")))
    has_risk = bool(st.session_state.get("risk_analysis") or st.session_state.get("risk_result"))
    has_match = bool(st.session_state.get("match_analysis") or st.session_state.get("match_result"))
    has_interview_ready = bool(has_jd and has_resume_processed)

    stat_cols = st.columns(6)
    stats_data = [
        ("Job Description", has_jd, "Job Risk Detection"),
        ("Resume Uploaded", has_resume_uploaded, "Resume Analyzer"),
        ("Resume Processed", has_resume_processed, "Resume Analyzer"),
        ("Risk Analyzed", has_risk, "Job Risk Detection"),
        ("Match Analyzed", has_match, "Resume Match"),
        ("Interview Ready", has_interview_ready, "Mock Interview"),
    ]

    for col, (label, done, target_page) in zip(stat_cols, stats_data):
        with col:
            badge_color = "#059669" if done else "#64748B"
            badge_bg = "#ECFDF5" if done else "#F8FAFC"
            border_c = "#A7F3D0" if done else "#E2E8F0"
            icon = "✓" if done else "○"
            text_status = "Completed" if done else "Pending"

            st.markdown(f"""
            <div style="background:{badge_bg}; border:1px solid {border_c}; border-radius:10px;
                        padding:0.75rem 0.5rem; text-align:center;">
                <div style="color:{badge_color}; font-weight:800; font-size:1.1rem;">{icon}</div>
                <div style="color:#0F241A; font-size:0.78rem; font-weight:600; margin:0.2rem 0;">{label}</div>
                <div style="color:{badge_color}; font-size:0.7rem; font-weight:700;">{text_status}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Connected Analysis Workflow ────────────────────────────────────────────
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:1.2rem 1.4rem;
                display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:0.5rem; margin-bottom:1.5rem;
                box-shadow:0 1px 3px rgba(0,0,0,0.02);">
        <div style="display:flex; align-items:center; gap:0.4rem;">
            <span style="background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px;">Step 1</span>
            <span style="font-weight:700; color:#0F241A; font-size:0.85rem;">Job Description</span>
        </div>
        <span style="color:#CBD5E1;">→</span>
        <div style="display:flex; align-items:center; gap:0.4rem;">
            <span style="background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px;">Step 2</span>
            <span style="font-weight:700; color:#0F241A; font-size:0.85rem;">OpenCV + OCR</span>
        </div>
        <span style="color:#CBD5E1;">→</span>
        <div style="display:flex; align-items:center; gap:0.4rem;">
            <span style="background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px;">Step 3</span>
            <span style="font-weight:700; color:#0F241A; font-size:0.85rem;">Risk Assessment</span>
        </div>
        <span style="color:#CBD5E1;">→</span>
        <div style="display:flex; align-items:center; gap:0.4rem;">
            <span style="background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px;">Step 4</span>
            <span style="font-weight:700; color:#0F241A; font-size:0.85rem;">Match & Gap Fit</span>
        </div>
        <span style="color:#CBD5E1;">→</span>
        <div style="display:flex; align-items:center; gap:0.4rem;">
            <span style="background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px;">Step 5</span>
            <span style="font-weight:700; color:#0F241A; font-size:0.85rem;">AI Mock Interview</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Call To Action Banner ──────────────────────────────────────────────────
    next_step = "Job Risk Detection" if not has_jd else ("Resume Analyzer" if not has_resume_processed else "Resume Match")
    st.markdown(f"""
    <div style="text-align:center; padding:1.8rem; background:linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%);
                border-radius:16px; border:1.5px solid #A7F3D0; margin-bottom:1.5rem;">
        <h3 style="color:#065F46; font-size:1.3rem; font-weight:800; margin-bottom:0.35rem;">Start Your Application Evaluation</h3>
        <p style="color:#166534; font-size:0.92rem; max-width:620px; margin:0 auto 1.2rem; line-height:1.5;">
            Input your target job posting and upload your resume once — all risk analysis, skill gaps,
            and personalized interview questions will automatically synchronize across the platform.
        </p>
    </div>
    """, unsafe_allow_html=True)

    cta1, cta2, cta3 = st.columns([1, 2, 1])
    with cta2:
        if st.button(f"🚀 Start Analysis ({next_step}) →", type="primary", use_container_width=True, key="btn_dash_start_analysis"):
            st.session_state["current_page"] = next_step
            st.rerun()

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Tech Expo Demonstration Guide ──────────────────────────────────────────
    with st.expander("💡 Tech Expo Evaluator Guide — Complete Feature Walkthrough", expanded=False):
        st.markdown("""
        **How JobShield AI Demonstrates Real-World AI Safety & Career Preparation:**

        1. **🛡️ Job Risk & Scam Detection:** Evaluates job/internship postings using dual-layer NLP heuristics and Groq LLM to detect application fees, registration traps, salary inflation, and suspicious recruiter channels. Provides risk score (0-100), red flags, and verification checklists.
        2. **📄 Resume Analyzer (OpenCV + OCR + LLM):** Preprocesses scanned or digital resumes via OpenCV (grayscale, Gaussian noise reduction, adaptive binarization, deskewing) and extracts structured profiles (skills, projects, education, experience) via Groq LLM without inventing information.
        3. **🎯 Resume–Job Match & Skill Gaps:** Automatically loads saved resume data and job description. Generates honest match percentage, highlights overlapping skills, and classifies missing skills by priority (High / Medium / Low) with actionable learning recommendations.
        4. **🎥 AI Mock Interview with Camera Atmosphere:** Dynamically generates personalized questions citing actual resume projects (e.g. *AI Contract Intelligence*) and job duties. Evaluates each candidate answer across relevance, technical correctness, completeness, and clarity with STAR model suggestions, concluding with a comprehensive evaluation report.
        """)

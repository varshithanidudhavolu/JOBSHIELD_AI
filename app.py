"""
app.py — JobShield AI Main Application
AI-Powered Job & Internship Safety, Matching & Mock Interview Assistant
HireLens-Style Professional Visual Design System & Rock-Solid Button Navigation

Run with:  streamlit run app.py
"""

import os
import sys
import streamlit as st
from services.groq_service import load_project_env, is_api_configured, test_groq_connection

# ── Ensure project root .env is loaded safely ──────────────────────────────
load_project_env()

# ── Page configuration (must be first Streamlit call) ──────────────────────
st.set_page_config(
    page_title="JobShield AI — Career Intelligence & Safety",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "JobShield AI — AI-Powered Job Safety, Matching & Mock Interview Assistant"
    }
)

# ── Global CSS — High-Contrast Sidebar & HireLens Theme ────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Global Typography & Background ── */
html, body, [data-testid="stAppViewContainer"], .main {
    background-color: #F8FAF9 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    color: #0F241A !important;
}

/* ── Hide default Streamlit overhead ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Clean Content Container ── */
.main .block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1220px !important;
}

/* ── Topbar / Header Shell ── */
.topbar-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1.25rem;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.topbar-breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.88rem;
    font-weight: 600;
    color: #475569;
}

.topbar-breadcrumb span.active {
    color: #047857;
    font-weight: 700;
}

.topbar-user {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.topbar-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #E6F4EA;
    border: 1.5px solid #10B981;
    color: #065F46;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.85rem;
}

.topbar-user-info {
    text-align: right;
    line-height: 1.2;
}

.topbar-user-name {
    font-size: 0.88rem;
    font-weight: 700;
    color: #0F241A;
}

.topbar-user-role {
    font-size: 0.75rem;
    color: #059669;
    font-weight: 500;
}

/* ── Sidebar: Deep Slate Forest Green ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071A12 0%, #0D281D 50%, #06160F 100%) !important;
    border-right: 1px solid #163B2B !important;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* ── Sidebar Navigation Buttons (Bulletproof, No Radio, No Exceptions) ── */
[data-testid="stSidebar"] div.stButton > button {
    text-align: left !important;
    justify-content: flex-start !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.6rem !important;
    padding: 0.65rem 0.95rem !important;
    border-radius: 10px !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    margin-bottom: 0.35rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

/* Inactive Sidebar Buttons: Crisp White on Dark Green */
[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.05) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
    background: rgba(16, 185, 129, 0.16) !important;
    border-color: rgba(16, 185, 129, 0.5) !important;
    color: #FFFFFF !important;
    transform: translateX(2px);
}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"] p,
[data-testid="stSidebar"] div.stButton > button[kind="secondary"] span {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Active Sidebar Button: Bright Green Border, Lighter Background, High Contrast */
[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: rgba(16, 185, 129, 0.28) !important;
    color: #FFFFFF !important;
    border: 2px solid #10B981 !important;
    box-shadow: 0 2px 10px rgba(16, 185, 129, 0.35) !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="primary"] p,
[data-testid="stSidebar"] div.stButton > button[kind="primary"] span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* ── Primary Buttons in Main Content ── */
.main .stButton button[kind="primary"] {
    background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 0.55rem 1.3rem !important;
    box-shadow: 0 2px 6px rgba(5, 150, 105, 0.25) !important;
    transition: all 0.2s ease !important;
}

.main .stButton button[kind="primary"]:hover {
    background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
    box-shadow: 0 4px 10px rgba(5, 150, 105, 0.35) !important;
    transform: translateY(-1px);
}

.main .stButton button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #1E293B !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}

.main .stButton button[kind="secondary"]:hover {
    border-color: #10B981 !important;
    color: #059669 !important;
}

/* ── Form Inputs ── */
.stTextArea textarea, .stTextInput input {
    border-radius: 10px !important;
    border: 1.5px solid #E2E8F0 !important;
    background-color: #FFFFFF !important;
    color: #0F241A !important;
    font-size: 0.92rem !important;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #10B981 !important;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15) !important;
}

/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    border: 2px dashed #A7F3D0 !important;
    border-radius: 14px !important;
    padding: 0.8rem !important;
    background: #F0FDF4 !important;
}

/* ── Camera Preview ── */
[data-testid="stCameraInput"] {
    border-radius: 14px !important;
    border: 1.5px solid #10B981 !important;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)


# ── Import Components ──────────────────────────────────────────────────────
try:
    from components.dashboard import render_dashboard
    from components.risk_analysis import render_risk_analysis
    from components.resume_match import render_resume_analyzer, render_resume_match
    from components.mock_interview import render_mock_interview
    from components.auth import render_auth_page, logout_user
except ImportError as e:
    st.error(f"❌ Import error: {e}. Please ensure all components are in place.")
    st.stop()


# ── Complete Persistent Session State ─────────────────────────────────────
def _init_session_state():
    """Ensure all required session state keys are persistently initialized."""
    defaults = {
        "logged_in": False,
        "user_id": None,
        "user_name": "",
        "user_email": "",
        "auth_mode": "login",
        "current_page": "Dashboard",
        "job_description": "",
        "global_job_description": "",
        "resume_file": None,
        "resume_text": "",
        "resume_data": None,
        "resume_info": None,
        "resume_profile": None,
        "extracted_skills": [],
        "risk_analysis": None,
        "risk_result": None,
        "match_analysis": None,
        "match_result": None,
        "skill_gaps": [],
        "target_role": "AI/ML Software Engineer",
        "interview_state": "setup",
        "interview_substate": "answering",
        "interview_camera_enabled": True,
        "interview_questions": [],
        "interview_current_q": 0,
        "current_question": 0,
        "interview_answers": [],
        "submitted_answers": [],
        "interview_scores": [],
        "interview_evaluations": [],
        "answer_evaluations": [],
        "interview_started": False,
        "interview_completed": False,
        "interview_report": None,
        "final_interview_report": None,
        "final_interview_score": None,
        "current_evaluation": None,
        "current_submitted_answer": "",
        "confirm_clear_session": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_session_state()


def navigate_to(page: str):
    """
    Clean navigation helper.
    Never assigns to widget-bound keys like 'main_navigation' to prevent StreamlitAPIException.
    """
    clean_page = page.replace("🏠 ", "").replace("🛡️ ", "").replace("👁️ ", "").replace("🎯 ", "").replace("🎥 ", "").strip()
    st.session_state["current_page"] = clean_page
    st.rerun()


# ── Topbar Component ───────────────────────────────────────────────────────
def _render_topbar():
    """Render HireLens-inspired top navigation bar with breadcrumb, dynamic candidate profile and logout."""
    current_page = st.session_state.get("current_page", "Dashboard")
    user_name = st.session_state.get("user_name", "Candidate")
    user_email = st.session_state.get("user_email", "")

    # Initials
    parts = user_name.strip().split()
    initials = "".join([p[0].upper() for p in parts[:2]]) if parts else "US"

    tb_left, tb_right = st.columns([2.6, 1.4])

    with tb_left:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:0.65rem 1.1rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.02); display:flex; align-items:center; gap:6px;">
            <span style="color:#64748B; font-size:0.88rem; font-weight:600;">JobShield AI</span>
            <span style="color:#CBD5E1;">/</span>
            <span style="color:#047857; font-size:0.88rem; font-weight:700;">{current_page}</span>
        </div>
        """, unsafe_allow_html=True)

    with tb_right:
        u_info_col, u_btn_col = st.columns([2.2, 1])
        with u_info_col:
            st.markdown(f"""
            <div style="display:flex; align-items:center; justify-content:flex-end; gap:8px; padding-top:4px;">
                <div style="text-align:right; line-height:1.2;">
                    <div style="font-size:0.86rem; font-weight:700; color:#0F241A;">👤 {user_name}</div>
                    <div style="font-size:0.72rem; color:#64748B;">{user_email}</div>
                </div>
                <div style="width:34px; height:34px; border-radius:50%; background:#E6F4EA; border:1.5px solid #10B981;
                            color:#065F46; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.82rem;">
                    {initials}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with u_btn_col:
            if st.button("Logout", key="btn_topbar_logout", use_container_width=True):
                logout_user()

    st.markdown("<div style='margin-bottom:0.8rem;'></div>", unsafe_allow_html=True)


# ── Sidebar Navigation with Pure Button Implementation (No Radio) ──────────
def _render_sidebar():
    """Render persistent left sidebar with branding, dynamic user profile, button navigation, session state & AI status."""
    with st.sidebar:
        # JobShield AI Logo & Brand
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0 0.5rem;">
            <div style="display:inline-flex; align-items:center; justify-content:center; width:52px; height:52px;
                        background:rgba(16,185,129,0.2); border:1.5px solid #10B981; border-radius:14px; margin-bottom:0.5rem;">
                <span style="font-size:1.8rem;">🛡️</span>
            </div>
            <div style="font-size:1.35rem; font-weight:800; color:#FFFFFF; letter-spacing:0.02em;">JobShield AI</div>
            <div style="font-size:0.75rem; color:#A7F3D0; margin-top:0.25rem; font-weight:500; line-height:1.4;">
                Analyze. Match. Prepare.<br>Apply with confidence.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Dynamic Logged-in User Badge in Sidebar
        user_name = st.session_state.get("user_name", "Candidate")
        user_email = st.session_state.get("user_email", "")
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.14);
                    border-radius:10px; padding:0.55rem 0.8rem; margin:0.4rem 0 0.8rem;">
            <div style="font-size:0.82rem; font-weight:700; color:#FFFFFF;">👤 {user_name}</div>
            <div style="font-size:0.68rem; color:#A7F3D0; overflow:hidden; text-overflow:ellipsis;">{user_email}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr style="border-color:rgba(255,255,255,0.12); margin:0.2rem 0 0.8rem;">', unsafe_allow_html=True)

        # ── Navigation Buttons ──
        current = st.session_state.get("current_page", "Dashboard")

        nav_pages = [
            ("Dashboard", "🏠 Dashboard"),
            ("Job Risk Detection", "🛡️ Job Risk Detection"),
            ("Resume Analyzer", "👁️ Resume Analyzer"),
            ("Resume Match", "🎯 Resume Match"),
            ("Mock Interview", "🎥 Mock Interview"),
        ]

        for page_id, display_label in nav_pages:
            is_active = (current == page_id)
            btn_title = f"●  {display_label}" if is_active else f"   {display_label}"
            
            # Using primary for active, secondary for inactive.
            # Fully custom styled via CSS above.
            if st.button(
                btn_title,
                key=f"nav_btn_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state["current_page"] = page_id
                st.rerun()

        st.markdown('<hr style="border-color:rgba(255,255,255,0.12); margin:0.9rem 0;">', unsafe_allow_html=True)

        # ── Session Status Indicators ──
        st.markdown("""
        <div style="font-size:0.72rem; font-weight:800; color:#A7F3D0; letter-spacing:0.08em; margin-bottom:0.6rem; text-transform:uppercase;">
            Session Status
        </div>
        """, unsafe_allow_html=True)

        has_jd = bool(st.session_state.get("job_description") or st.session_state.get("global_job_description"))
        has_resume_uploaded = bool(st.session_state.get("resume_file") or st.session_state.get("resume_info") or st.session_state.get("resume_text"))
        has_resume_processed = bool(st.session_state.get("resume_info") and (st.session_state.get("resume_info", {}).get("skills") or st.session_state.get("extracted_skills")))
        has_risk = bool(st.session_state.get("risk_analysis") or st.session_state.get("risk_result"))
        has_match = bool(st.session_state.get("match_analysis") or st.session_state.get("match_result"))
        has_interview_ready = bool(has_jd and has_resume_processed)

        status_items = [
            ("📋 Job Description", has_jd),
            ("📄 Resume Uploaded", has_resume_uploaded),
            ("⚙️ Resume Processed", has_resume_processed),
            ("🛡️ Risk Analyzed", has_risk),
            ("🎯 Match Analyzed", has_match),
            ("🎥 Interview Ready", has_interview_ready),
        ]

        for label, done in status_items:
            icon = "✓" if done else "○"
            status_text = "Ready" if done else "Pending"
            badge_color = "#34D399" if done else "#CBD5E1"
            badge_bg = "rgba(16, 185, 129, 0.22)" if done else "rgba(255, 255, 255, 0.08)"
            border_c = "rgba(16, 185, 129, 0.45)" if done else "rgba(255, 255, 255, 0.15)"

            st.markdown(
                f'<div style="display:flex; justify-content:space-between; align-items:center;'
                f'background:rgba(255,255,255,0.05); border:1px solid {border_c};'
                f'border-radius:8px; padding:0.4rem 0.7rem; margin-bottom:0.35rem;">'
                f'<span style="color:#FFFFFF !important; font-size:0.8rem; font-weight:600;">{label}</span>'
                f'<span style="background:{badge_bg}; color:{badge_color} !important; font-size:0.68rem; font-weight:700;'
                f'padding:2px 8px; border-radius:10px; display:inline-flex; align-items:center; gap:3px;">{icon} {status_text}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown('<hr style="border-color:rgba(255,255,255,0.12); margin:0.8rem 0;">', unsafe_allow_html=True)

        # ── AI Connection Status & Test Button ──
        if is_api_configured():
            st.markdown("""
            <div style="display:flex; align-items:center; gap:6px; background:rgba(16,185,129,0.18);
                        border:1px solid rgba(16,185,129,0.45); border-radius:8px; padding:0.45rem 0.7rem; margin-bottom:0.5rem;">
                <span style="color:#34D399; font-size:0.9rem;">✓</span>
                <span style="color:#FFFFFF !important; font-size:0.8rem; font-weight:600;">Groq AI Connected</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display:flex; align-items:center; gap:6px; background:rgba(239,68,68,0.18);
                        border:1px solid rgba(239,68,68,0.45); border-radius:8px; padding:0.45rem 0.7rem; margin-bottom:0.5rem;">
                <span style="color:#F87171; font-size:0.9rem;">⚠</span>
                <span style="color:#FFFFFF !important; font-size:0.8rem; font-weight:600;">AI Connection Required</span>
            </div>
            """, unsafe_allow_html=True)

        if st.button("⚡ Test AI Connection", key="btn_test_ai_sidebar", use_container_width=True):
            with st.spinner("Testing Groq connection..."):
                ok, msg = test_groq_connection()
            if ok:
                st.success("✓ Groq API operational", icon=None)
            else:
                st.error(f"❌ {msg}", icon=None)

        # ── Clear Session Action ──
        st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
        if not st.session_state.get("confirm_clear_session", False):
            if st.button("🗑️ Clear Session", use_container_width=True, key="btn_req_clear"):
                st.session_state["confirm_clear_session"] = True
                st.rerun()
        else:
            st.warning("Reset all session data?")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                if st.button("✓ Yes", type="primary", use_container_width=True, key="btn_conf_yes"):
                    keys = [
                        "job_description", "global_job_description", "resume_file",
                        "resume_text", "extracted_skills", "resume_info", "resume_data",
                        "resume_profile", "risk_analysis", "risk_result", "match_analysis",
                        "match_result", "skill_gaps", "target_role", "interview_state",
                        "interview_substate", "interview_questions", "interview_current_q",
                        "current_question", "interview_answers", "submitted_answers",
                        "interview_scores", "interview_evaluations", "answer_evaluations",
                        "interview_started", "interview_completed", "interview_report",
                        "final_interview_report", "final_interview_score", "current_evaluation",
                        "current_submitted_answer", "risk_jd_input", "sidebar_jd",
                        "confirm_clear_session"
                    ]
                    for k in keys:
                        st.session_state.pop(k, None)
                    _init_session_state()
                    st.session_state["current_page"] = "Dashboard"
                    st.rerun()
            with col_c2:
                if st.button("Cancel", use_container_width=True, key="btn_conf_no"):
                    st.session_state["confirm_clear_session"] = False
                    st.rerun()

        st.markdown("<div style='margin-top:0.4rem;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", key="btn_sidebar_logout", use_container_width=True):
            logout_user()

        st.markdown("""
        <div style="color:#A7F3D0 !important; opacity:0.85; font-size:0.72rem; text-align:center; margin-top:1.2rem;">
            JobShield AI &bull; Tech Expo Edition<br>
            Powered by Groq LLM + OpenCV
        </div>
        """, unsafe_allow_html=True)


# ── Main Application Router ────────────────────────────────────────────────
def main():
    # Login protection: Require authentication before accessing platform
    if not st.session_state.get("logged_in", False):
        render_auth_page()
        return

    _render_sidebar()
    _render_topbar()

    page = st.session_state.get("current_page", "Dashboard")

    if page == "Dashboard":
        render_dashboard()
    elif page == "Job Risk Detection":
        render_risk_analysis()
    elif page == "Resume Analyzer":
        render_resume_analyzer()
    elif page == "Resume Match":
        render_resume_match()
    elif page == "Mock Interview":
        render_mock_interview()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()

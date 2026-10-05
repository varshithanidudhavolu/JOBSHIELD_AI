"""
components/auth.py
Clean, professional Login and Registration interface for JobShield AI.
Features secure authentication, error alerts, tab/mode switching, and quick demo credentials.
"""

import streamlit as st
from services.auth_service import authenticate_user, create_user


def render_auth_page():
    """Render the JobShield AI authentication screen (Login / Sign Up)."""

    auth_mode = st.session_state.get("auth_mode", "login")

    # Center card container
    _, center_col, _ = st.columns([1, 1.4, 1])

    with center_col:
        # Header / Branding
        st.markdown("""
        <div style="text-align:center; padding:1.5rem 0 1rem;">
            <div style="display:inline-flex; align-items:center; justify-content:center; width:64px; height:64px;
                        background:rgba(16,185,129,0.15); border:2px solid #10B981; border-radius:18px; margin-bottom:0.75rem;">
                <span style="font-size:2.2rem;">🛡️</span>
            </div>
            <h1 style="font-size:2.1rem; font-weight:800; color:#0F241A; margin-bottom:0.3rem; letter-spacing:-0.02em;">
                JobShield AI
            </h1>
            <p style="font-size:0.95rem; color:#059669; font-weight:600; margin-bottom:0.2rem;">
                AI Career Intelligence & Verification Platform
            </p>
            <p style="font-size:0.82rem; color:#64748B;">
                Sign in to analyze job postings, evaluate your resume, and conduct real-time AI mock interviews.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Main Card
        st.markdown("""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-top:4px solid #059669;
                    border-radius:16px; padding:1.8rem 2rem 1.4rem; box-shadow:0 4px 20px rgba(0,0,0,0.04); margin-bottom:1.2rem;">
        """, unsafe_allow_html=True)

        if auth_mode == "login":
            _render_login_form()
        else:
            _render_signup_form()

        st.markdown("</div>", unsafe_allow_html=True)

        # Quick Demo Login Buttons for Evaluators & Expo Demo
        st.markdown("""
        <div style="background:#F0FDF4; border:1px dashed #A7F3D0; border-radius:12px; padding:1rem 1.2rem; text-align:center;">
            <div style="font-size:0.78rem; font-weight:700; color:#065F46; text-transform:uppercase; margin-bottom:0.5rem; letter-spacing:0.04em;">
                ⚡ One-Click Demo Access
            </div>
        """, unsafe_allow_html=True)

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            if st.button("👤 Varshitha (Admin)", use_container_width=True, key="demo_btn_varshitha"):
                _perform_login("varshitha@jobshield.ai", "password123")
        with d_col2:
            if st.button("🎓 Candidate Demo", use_container_width=True, key="demo_btn_candidate"):
                _perform_login("demo@jobshield.ai", "demo123")

        st.markdown("</div>", unsafe_allow_html=True)


def _render_login_form():
    """Render Login Form."""
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.2rem;">
        <h3 style="margin:0; font-size:1.25rem; font-weight:700; color:#0F241A;">Sign In</h3>
        <span style="font-size:0.75rem; color:#059669; font-weight:700; background:#ECFDF5; padding:2px 8px; border-radius:10px;">
            Secure Local Auth
        </span>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email Address", placeholder="name@example.com", key="login_email_input")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pwd_input")

        submit = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

    if submit:
        _perform_login(email, password)

    st.markdown('<div style="text-align:center; margin-top:1rem; font-size:0.85rem; color:#64748B;">', unsafe_allow_html=True)
    st.write("Don't have an account?")
    if st.button("Create an account &rarr;", key="goto_signup_btn", use_container_width=True):
        st.session_state["auth_mode"] = "signup"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def _render_signup_form():
    """Render Registration Form."""
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.2rem;">
        <h3 style="margin:0; font-size:1.25rem; font-weight:700; color:#0F241A;">Create Account</h3>
        <span style="font-size:0.75rem; color:#059669; font-weight:700; background:#ECFDF5; padding:2px 8px; border-radius:10px;">
            New Candidate
        </span>
    </div>
    """, unsafe_allow_html=True)

    with st.form("signup_form", clear_on_submit=False):
        name = st.text_input("Full Name", placeholder="e.g. Naga Varshitha or Rahul Sharma", key="signup_name_input")
        email = st.text_input("Email Address", placeholder="name@example.com", key="signup_email_input")
        password = st.text_input("Password (min 6 characters)", type="password", placeholder="Create secure password", key="signup_pwd_input")
        confirm_pwd = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="signup_conf_pwd_input")

        submit = st.form_submit_button("Create Account →", use_container_width=True, type="primary")

    if submit:
        if password != confirm_pwd:
            st.error("❌ Passwords do not match. Please re-enter.")
            return

        user, err = create_user(name, email, password)
        if err:
            st.error(f"❌ {err}")
            return

        # Auto-login newly registered user
        _set_session_user(user)
        st.success(f"✓ Account created successfully! Welcome, {user['name']}.")
        st.session_state["auth_mode"] = "login"
        st.rerun()

    st.markdown('<div style="text-align:center; margin-top:1rem; font-size:0.85rem; color:#64748B;">', unsafe_allow_html=True)
    st.write("Already have an account?")
    if st.button("&larr; Back to Sign In", key="goto_login_btn", use_container_width=True):
        st.session_state["auth_mode"] = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def _perform_login(email: str, password: str):
    """Execute user login, update session state, and navigate to Dashboard."""
    user, err = authenticate_user(email, password)
    if err:
        st.error(f"❌ {err}")
        return

    _set_session_user(user)
    st.success(f"✓ Welcome back, {user['name']}!")
    st.session_state["current_page"] = "Dashboard"
    st.rerun()


def _set_session_user(user: dict):
    """Populate persistent session state with authenticated user profile."""
    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["user_name"] = user["name"]
    st.session_state["user_email"] = user["email"]


def logout_user():
    """Clear user session and return to Login view."""
    auth_keys = ["logged_in", "user_id", "user_name", "user_email"]
    for k in auth_keys:
        st.session_state.pop(k, None)
    st.session_state["auth_mode"] = "login"
    st.session_state["current_page"] = "Dashboard"
    st.rerun()

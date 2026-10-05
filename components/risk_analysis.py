"""
components/risk_analysis.py
Job Risk & Scam Detection page.
Analyzes job and internship postings using NLP heuristics + Groq LLM.
Styled according to the HireLens professional visual design system.
"""

import streamlit as st
from services.risk_service import analyze_job_risk


def render_risk_analysis():
    """Render the Job Risk Detection page."""

    # ── Page Header ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom:1.2rem;">
        <h2 style="color:#0F241A; font-weight:800; font-size:1.8rem; margin-bottom:0.25rem;">
            🛡️ Job Risk Detection
        </h2>
        <p style="color:#475569; font-size:0.95rem; margin-bottom:0.2rem;">
            Check a job or internship posting for suspicious indicators before you apply.
        </p>
        <p style="color:#64748B; font-size:0.8rem; font-style:italic;">
            AI-assisted evaluation identifies suspicious patterns and provides verification guidance to keep candidates safe.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Retrieve existing job description ──────────────────────────────────────
    saved_jd = st.session_state.get("job_description") or st.session_state.get("global_job_description", "")

    # Quick demo samples for Expo evaluators
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
        <span style="font-size:0.88rem; font-weight:700; color:#0F241A;">Job / Internship Description</span>
        <span style="font-size:0.75rem; color:#64748B;">Paste or load a demo sample</span>
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2, col_s3 = st.columns([1.5, 1.5, 3])
    with col_s1:
        if st.button("📋 Load Suspicious Sample", key="btn_sample_suspicious", use_container_width=True):
            saved_jd = (
                "We are hiring a remote AI/ML intern.\n"
                "The candidate must pay ₹5,000 registration fee before the interview.\n"
                "Guaranteed salary of ₹80,000 per month.\n"
                "Send your Aadhaar, PAN and bank details through WhatsApp immediately.\n"
                "Limited seats. Pay today to secure your position."
            )
            st.session_state["job_description"] = saved_jd
            st.session_state["global_job_description"] = saved_jd
            st.rerun()

    with col_s2:
        if st.button("🏢 Load Legitimate Sample", key="btn_sample_legit", use_container_width=True):
            saved_jd = (
                "Software Engineer Intern — Machine Learning & Backend\n"
                "Company: NovaScale Technologies Ltd.\n"
                "Location: Bangalore, India (Hybrid) | Duration: 6 months internship\n\n"
                "About the Role:\n"
                "We are seeking an enthusiastic AI/ML Intern to join our platform engineering team. You will assist in developing data pipelines, evaluating LLM integrations, and building microservices in Python.\n\n"
                "Key Responsibilities:\n"
                "- Build and optimize machine learning models and REST APIs using Python and FastAPI.\n"
                "- Collaborate with senior engineers on RAG and document processing workflows.\n"
                "- Write unit tests and maintain documentation for ML deployment.\n\n"
                "Requirements:\n"
                "- Strong proficiency in Python and SQL.\n"
                "- Familiarity with Git, PyTorch, Docker, or OpenCV.\n"
                "- Currently pursuing B.Tech/M.Tech in CS/AI or related degree.\n\n"
                "Stipend: Rs 45,000/month. No fees of any kind are charged at any stage of recruitment. Apply via careers@novascale.io."
            )
            st.session_state["job_description"] = saved_jd
            st.session_state["global_job_description"] = saved_jd
            st.rerun()

    # ── Job Description Text Area ──────────────────────────────────────────────
    job_desc = st.text_area(
        "Job Description Input",
        value=saved_jd,
        height=220,
        placeholder="Paste full job posting or internship description here...",
        key="risk_jd_input",
        label_visibility="collapsed"
    )

    # ── Action Buttons ─────────────────────────────────────────────────────────
    col_act1, col_act2, col_act3 = st.columns([2, 2, 4])
    with col_act1:
        analyze_btn = st.button("🛡️ Analyze Risk", type="primary", use_container_width=True)
    with col_act2:
        save_btn = st.button("💾 Save Job Description", use_container_width=True)
    with col_act3:
        if st.button("🗑️ Clear Result", use_container_width=False):
            st.session_state.pop("risk_result", None)
            st.session_state.pop("risk_analysis", None)
            st.rerun()

    if save_btn:
        if not job_desc or not job_desc.strip():
            st.warning("⚠️ Please paste a job description first.")
        else:
            st.session_state["job_description"] = job_desc.strip()
            st.session_state["global_job_description"] = job_desc.strip()
            st.success("✓ Job description saved and synchronized across all features!")

    if analyze_btn:
        if not job_desc or not job_desc.strip():
            st.error("❌ Please paste a job description before analyzing.")
            return

        # Save to session
        st.session_state["job_description"] = job_desc.strip()
        st.session_state["global_job_description"] = job_desc.strip()

        with st.spinner("🛡️ Analyzing posting indicators with Groq AI + NLP heuristics..."):
            result, error = analyze_job_risk(job_desc.strip())

        if error:
            st.error(f"❌ Analysis error: {error}")
            return

        st.session_state["risk_result"] = result
        st.session_state["risk_analysis"] = result

    # ── Display Risk Results ───────────────────────────────────────────────────
    active_result = st.session_state.get("risk_analysis") or st.session_state.get("risk_result")
    if active_result:
        _display_risk_results(active_result)

        # ── Progression Step to Step 2 ────────────────────────────────────────
        st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
        col_flow1, col_flow2, col_flow3 = st.columns([1, 2, 1])
        with col_flow2:
            if st.button("Proceed to Resume Analyzer (Step 2) ➡️", type="primary", use_container_width=True, key="btn_risk_to_resume"):
                st.session_state["current_page"] = "Resume Analyzer"
                st.rerun()


def _display_risk_results(result: dict):
    """Render the structured risk analysis results in HireLens visual format."""
    risk_level = result.get("risk_level", "MEDIUM")
    risk_score = result.get("risk_score", 50)
    red_flags = result.get("red_flags", [])
    positive_indicators = result.get("positive_indicators", [])
    safety_recs = result.get("safety_recommendations", [])
    verification = result.get("verification_checklist", [])
    explanation = result.get("explanation", "")
    disclaimer = result.get("disclaimer", "")

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Risk Level Banner ──────────────────────────────────────────────────────
    level_config = {
        "LOW": {
            "icon": "🟢",
            "label": "LOW RISK",
            "title_color": "#065F46",
            "bg": "#ECFDF5",
            "border": "#A7F3D0",
            "badge_class": "badge-mint",
            "desc": "This posting appears mostly legitimate. Standard due diligence and company verification recommended."
        },
        "MEDIUM": {
            "icon": "🟡",
            "label": "NEEDS VERIFICATION",
            "title_color": "#92400E",
            "bg": "#FFFBEB",
            "border": "#FDE68A",
            "badge_class": "badge-amber",
            "desc": "This posting contains indicators that require verification before sharing personal details or applying."
        },
        "HIGH": {
            "icon": "🔴",
            "label": "HIGH RISK",
            "title_color": "#991B1B",
            "bg": "#FEF2F2",
            "border": "#FECACA",
            "badge_class": "badge-rose",
            "desc": "Potential risk detected. Multiple high-severity indicators found. Exercise extreme caution."
        }
    }

    cfg = level_config.get(risk_level, level_config["MEDIUM"])

    st.markdown(f"""
    <div style="background:{cfg['bg']}; border:2px solid {cfg['border']};
                border-radius:16px; padding:1.5rem 1.8rem; margin-bottom:1.4rem; text-align:center;">
        <div style="font-size:2.6rem; margin-bottom:0.25rem;">{cfg['icon']}</div>
        <div style="font-size:1.6rem; font-weight:800; color:{cfg['title_color']}; letter-spacing:0.02em;">{cfg['label']}</div>
        <div style="color:#475569; margin-top:0.4rem; font-size:0.95rem; max-width:650px; margin-left:auto; margin-right:auto;">
            {cfg['desc']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Score & Assessment Row ────────────────────────────────────────────────
    sc1, sc2 = st.columns([1, 2])

    with sc1:
        score_color = "#DC2626" if risk_score >= 60 else ("#D97706" if risk_score >= 30 else "#059669")
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px;
                    padding:1.4rem 1.2rem; text-align:center; height:100%; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
            <div style="color:#64748B; font-size:0.78rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.4rem;">
                Risk Score
            </div>
            <div style="font-size:3.2rem; font-weight:900; color:{score_color}; line-height:1;">{risk_score}</div>
            <div style="color:#94A3B8; font-size:0.75rem; margin-top:0.2rem;">out of 100</div>
            <div style="margin-top:0.8rem; height:8px; background:#F1F5F9; border-radius:4px; overflow:hidden;">
                <div style="width:{risk_score}%; height:100%; background:{score_color}; border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with sc2:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px;
                    padding:1.4rem 1.6rem; height:100%; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
            <div style="color:#64748B; font-size:0.78rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.5rem;">
                Why This Matters &bull; AI Assessment
            </div>
            <div style="color:#1E293B; font-size:0.92rem; line-height:1.65;">
                {explanation}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)

    # ── Detected Red Flags ────────────────────────────────────────────────────
    if red_flags:
        st.markdown(f"""
        <div style="margin-bottom:0.8rem;">
            <h3 style="font-size:1.15rem; font-weight:700; color:#0F241A; margin:0;">
                🚩 Detected Red Flags ({len(red_flags)})
            </h3>
            <p style="font-size:0.82rem; color:#64748B; margin:0.15rem 0 0;">
                Specific patterns requiring caution or independent verification.
            </p>
        </div>
        """, unsafe_allow_html=True)

        for flag in red_flags:
            sev = flag.get("severity", "MEDIUM")
            sev_color = {"HIGH": "#DC2626", "MEDIUM": "#D97706", "LOW": "#059669"}.get(sev, "#D97706")
            sev_bg = {"HIGH": "#FEF2F2", "MEDIUM": "#FFFBEB", "LOW": "#ECFDF5"}.get(sev, "#FFFBEB")
            sev_border = {"HIGH": "#FECACA", "MEDIUM": "#FDE68A", "LOW": "#A7F3D0"}.get(sev, "#FDE68A")

            matched = flag.get("matched_text", "")
            matched_html = f'<div style="color:#64748B; font-size:0.8rem; margin-top:0.4rem; font-style:italic;">Matched in posting: "{matched}"</div>' if matched else ""

            st.markdown(f"""
            <div style="background:{sev_bg}; border-left:4px solid {sev_color}; border-top:1px solid {sev_border};
                        border-right:1px solid {sev_border}; border-bottom:1px solid {sev_border};
                        border-radius:0 10px 10px 0; padding:0.9rem 1.1rem; margin-bottom:0.6rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong style="color:{sev_color}; font-size:0.92rem;">⚠️ {flag.get('category', 'Risk Detected')}</strong>
                    <span style="background:{sev_color}; color:#FFFFFF; font-size:0.68rem;
                                 padding:2px 8px; border-radius:4px; font-weight:700;">{sev} SEVERITY</span>
                </div>
                <div style="color:#334155; font-size:0.88rem; margin-top:0.35rem; line-height:1.5;">
                    {flag.get('description', '')}
                </div>
                {matched_html}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:10px; padding:1.1rem; text-align:center;">
            <strong style="color:#065F46; font-size:0.92rem;">✅ No suspicious indicators or red flags detected in this posting.</strong>
        </div>
        """, unsafe_allow_html=True)

    # ── Positive Indicators ────────────────────────────────────────────────────
    if positive_indicators:
        st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <h4 style="font-size:1rem; font-weight:700; color:#065F46; margin-bottom:0.5rem;">
            ✓ Positive & Legitimate Indicators
        </h4>
        """, unsafe_allow_html=True)

        for pi in positive_indicators:
            st.markdown(f"""
            <div style="display:flex; gap:0.5rem; align-items:flex-start; margin-bottom:0.35rem;">
                <span style="color:#059669; font-weight:700;">✓</span>
                <span style="color:#1E293B; font-size:0.88rem;">{pi}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Safety Recommendations & Verification Checklist ───────────────────────
    st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)
    rec_col, check_col = st.columns(2)

    with rec_col:
        st.markdown("""
        <h4 style="font-size:1rem; font-weight:700; color:#0F241A; margin-bottom:0.5rem;">
            💡 Safety Recommendations
        </h4>
        """, unsafe_allow_html=True)

        for rec in safety_recs:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:0.7rem 0.9rem;
                        margin-bottom:0.45rem; font-size:0.86rem; color:#1E293B; display:flex; gap:8px; align-items:flex-start;">
                <span style="color:#059669; font-weight:700; flex-shrink:0;">&bull;</span>
                <span>{rec}</span>
            </div>
            """, unsafe_allow_html=True)

    with check_col:
        st.markdown("""
        <h4 style="font-size:1rem; font-weight:700; color:#0F241A; margin-bottom:0.5rem;">
            📋 Verification Checklist
        </h4>
        """, unsafe_allow_html=True)

        for item in verification:
            st.markdown(f"""
            <div style="display:flex; gap:0.6rem; align-items:flex-start; margin-bottom:0.45rem;
                        background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:0.7rem 0.9rem;">
                <span style="color:#059669; font-weight:700; font-size:0.9rem;">&check;</span>
                <span style="color:#1E293B; font-size:0.86rem;">{item}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Disclaimer ─────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px;
                padding:0.85rem 1.1rem; color:#64748B; font-size:0.8rem; line-height:1.5;">
        {disclaimer}
    </div>
    """, unsafe_allow_html=True)

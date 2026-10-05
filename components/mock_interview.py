"""
components/mock_interview.py
Real-Time AI Video-Call Style Mock Interview with Hands-Free Voice Turn-Taking,
Dual Video Tiles (AI Interviewer Avatar + Live Candidate Webcam),
Browser Text-to-Speech (TTS), Groq Whisper STT, Dynamic Multi-Turn Follow-Ups,
and Comprehensive End-of-Interview Evaluation Report.
"""

import time
import json
import streamlit as st
import streamlit.components.v1 as components
from services.interview_service import (
    generate_initial_interview_question,
    generate_conversational_followup,
    generate_final_interview_evaluation,
    generate_interview_questions,
    evaluate_conversational_turn,
    generate_final_report
)
from services.groq_service import transcribe_audio_groq, is_api_configured


def render_mock_interview():
    """Main entry point for the Mock Interview feature."""

    st.markdown("""
    <div style="margin-bottom:1.2rem;">
        <h2 style="color:#0F241A; font-weight:800; font-size:1.8rem; margin-bottom:0.25rem;">
            🎥 AI Mock Interview (Live Video Call)
        </h2>
        <p style="color:#475569; font-size:0.95rem; margin-bottom:0.2rem;">
            Live interactive technical interview with real-time AI interviewer avatar, voice dialogue, and webcam preview.
        </p>
        <p style="color:#64748B; font-size:0.8rem; font-style:italic;">
            Hands-free voice turn-taking &bull; Spoken AI responses &bull; Adaptive follow-ups derived from what you say.
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
# NAVIGATION HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _nav(page: str):
    """Navigate between pages cleanly without touching widget-bound keys."""
    clean_page = page.replace("🏠 ", "").replace("🛡️ ", "").replace("👁️ ", "").replace("🎯 ", "").replace("🎥 ", "").strip()
    st.session_state["current_page"] = clean_page
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 1. SETUP / LOBBY SCREEN (Waiting Room Before Video Call Starts)
# ─────────────────────────────────────────────────────────────────────────────

def _render_setup():
    """Pre-interview lobby matching video-call check-in experience."""
    resume_info = st.session_state.get("resume_info") or st.session_state.get("resume_data") or st.session_state.get("resume_profile")
    job_description = st.session_state.get("job_description") or st.session_state.get("global_job_description", "")

    # Retrieve dynamic logged-in user name
    cand_name = st.session_state.get("user_name") or (resume_info.get("name") if resume_info else None) or "Candidate"

    # Reconstruct from extracted skills/text if resume was uploaded
    if not resume_info and (st.session_state.get("extracted_skills") or st.session_state.get("resume_text")):
        resume_info = {
            "name": cand_name,
            "skills": st.session_state.get("extracted_skills", ["Python", "Machine Learning", "SQL", "RAG"]),
            "projects": ["AI Contract Intelligence", "Real-Time Fraud Detection"],
            "experience": ["AI Research Intern"],
            "education": ["B.Tech Computer Science and Engineering"],
            "_raw_text": st.session_state.get("resume_text", "")
        }
        st.session_state["resume_info"] = resume_info
        st.session_state["resume_profile"] = resume_info

    # Keep candidate name synchronized
    if resume_info:
        resume_info["name"] = cand_name

    has_resume = bool(resume_info and (resume_info.get("skills") or resume_info.get("_raw_text")))
    has_jd = bool(job_description and job_description.strip())

    role_hint = _extract_role_hint(job_description)
    st.session_state["target_role"] = role_hint

    # Match Score context if arriving from Resume Match
    match_score = st.session_state.get("match_score")
    matching_skills = st.session_state.get("matching_skills", [])
    missing_skills = st.session_state.get("missing_skills", [])

    # ── Video Call Lobby Card ─────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1.5px solid #A7F3D0; border-top:4px solid #059669;
                border-radius:16px; padding:1.8rem 2rem; margin-bottom:1.5rem; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1.2rem; flex-wrap:wrap; gap:0.5rem;">
            <div>
                <div style="display:inline-flex; align-items:center; gap:6px; background:#ECFDF5; border:1px solid #A7F3D0;
                            padding:3px 12px; border-radius:14px; font-size:0.75rem; font-weight:700; color:#065F46; margin-bottom:0.4rem;">
                    <span>●</span> AI Video-Call Interview Room Ready
                </div>
                <h3 style="color:#0F241A; margin:0; font-size:1.45rem; font-weight:800;">Target Role: {role_hint}</h3>
                <p style="color:#475569; font-size:0.92rem; margin:0.3rem 0 0;">
                    Candidate: <strong>{cand_name}</strong> &bull; Interactive Conversational Technical Interview
                </p>
            </div>
            <span style="background:{'#ECFDF5' if (has_resume and has_jd) else '#FFFBEB'};
                         color:{'#065F46' if (has_resume and has_jd) else '#92400E'};
                         border:1px solid {'#A7F3D0' if (has_resume and has_jd) else '#FDE68A'};
                         font-size:0.8rem; font-weight:700; padding:5px 14px; border-radius:20px;">
                {'✓ Connected & Ready to Join' if (has_resume and has_jd) else '⚠️ Missing Inputs'}
            </span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:0.9rem; margin-top:1rem;">
            <div style="background:#F8FAF9; padding:0.9rem 1.1rem; border-radius:10px; border:1px solid #E2E8F0;">
                <div style="color:#64748B; font-size:0.72rem; font-weight:700; text-transform:uppercase;">Candidate</div>
                <div style="color:#0F241A; font-weight:700; font-size:1.05rem; margin-top:0.2rem;">{cand_name}</div>
            </div>
            <div style="background:#F8FAF9; padding:0.9rem 1.1rem; border-radius:10px; border:1px solid #E2E8F0;">
                <div style="color:#64748B; font-size:0.72rem; font-weight:700; text-transform:uppercase;">Resume Context</div>
                <div style="color:{'#059669' if has_resume else '#DC2626'}; font-weight:700; font-size:1.05rem; margin-top:0.2rem;">
                    {'✓ Loaded' if has_resume else '✕ Not Loaded'}
                </div>
            </div>
            <div style="background:#F8FAF9; padding:0.9rem 1.1rem; border-radius:10px; border:1px solid #E2E8F0;">
                <div style="color:#64748B; font-size:0.72rem; font-weight:700; text-transform:uppercase;">Job Description</div>
                <div style="color:{'#059669' if has_jd else '#DC2626'}; font-weight:700; font-size:1.05rem; margin-top:0.2rem;">
                    {'✓ Available' if has_jd else '✕ Missing'}
                </div>
            </div>
            {f'''<div style="background:#F0FDF4; padding:0.9rem 1.1rem; border-radius:10px; border:1px solid #A7F3D0;">
                <div style="color:#065F46; font-size:0.72rem; font-weight:700; text-transform:uppercase;">Match Score</div>
                <div style="color:#059669; font-weight:800; font-size:1.15rem; margin-top:0.2rem;">{match_score}%</div>
            </div>''' if match_score is not None else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Handle missing prerequisites ──────────────────────────────────────────
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
                    if st.button("👁️ Open Resume Analyzer", use_container_width=True, key="btn_goto_res_analyzer"):
                        _nav("Resume Analyzer")
                with col_sub2:
                    if st.button("⚡ Load Demo Profile", use_container_width=True, key="btn_load_demo_res"):
                        st.session_state["resume_info"] = {
                            "name": cand_name,
                            "skills": ["Python", "Machine Learning", "Streamlit", "RAG", "SQL", "NLP"],
                            "projects": ["AI Contract Intelligence", "Government Scheme RAG Assistant"],
                            "experience": ["AI Research Intern &bull; Tech Solutions"],
                            "education": ["B.Tech Computer Science and Engineering"]
                        }
                        st.session_state["extracted_skills"] = ["Python", "Machine Learning", "Streamlit", "RAG", "SQL", "NLP"]
                        st.rerun()

    # ── AV Device Preferences ─────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:1.4rem; margin-bottom:1.4rem;">
        <h4 style="margin:0 0 0.8rem; color:#0F241A; font-weight:700;">Video Call Device Settings</h4>
    """, unsafe_allow_html=True)

    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
    with col_cfg1:
        st.session_state["interview_camera_enabled"] = st.checkbox(
            "📹 Candidate Camera Preview",
            value=st.session_state.get("interview_camera_enabled", True),
            help="Displays your live webcam in the candidate video tile."
        )
    with col_cfg2:
        st.session_state["interview_tts_enabled"] = st.checkbox(
            "🔊 AI Voice Output (Speech)",
            value=st.session_state.get("interview_tts_enabled", True),
            help="AI interviewer speaks questions aloud via Text-to-Speech."
        )
    with col_cfg3:
        st.markdown("""
        <div style="font-size:0.85rem; color:#059669; font-weight:700; padding-top:4px;">
            🎤 Microphone: Hands-Free
        </div>
        <div style="font-size:0.75rem; color:#64748B;">
            Spoken answers are automatically sent to the AI without clicking 'Submit Answer'.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Launch Video Call Button ──────────────────────────────────────────────
    can_start = has_resume and has_jd
    if st.button(
        "🎙️ Start Live Video Interview →",
        type="primary",
        disabled=not can_start,
        use_container_width=True,
        key="btn_start_mock_interview"
    ):
        with st.spinner(f"🤖 Connecting to AI Video Call... Reviewing {cand_name}'s resume and formulating opening question..."):
            initial_q, err = generate_initial_interview_question(
                resume_info=resume_info,
                job_description=job_description,
                target_role=role_hint
            )

        if err or not initial_q:
            st.error(f"❌ Failed to connect: {err or 'Unknown error'}")
            return

        # Initialize conversation state
        st.session_state["conversation_history"] = [
            {"role": "interviewer", "content": initial_q["question"]}
        ]
        st.session_state["current_question_text"] = initial_q["question"]
        st.session_state["current_ai_message"] = initial_q["question"]
        st.session_state["current_question_category"] = initial_q.get("category", "Resume-Based")
        st.session_state["current_question_focus"] = initial_q.get("focus_area", "Project Overview")
        st.session_state["interview_turn"] = 1
        st.session_state["interview_answers"] = []
        st.session_state["interview_evaluations"] = []
        st.session_state["current_user_answer"] = ""
        st.session_state["current_transcript"] = ""
        st.session_state["last_acknowledgment"] = ""
        st.session_state["interview_started"] = True
        st.session_state["interview_completed"] = False
        st.session_state["interview_active"] = True
        st.session_state["interview_state"] = "interview"
        st.session_state["interview_start_time"] = time.time()
        st.session_state["ai_status"] = "speaking"  # 'speaking', 'listening', 'thinking'
        st.session_state["q_spoken_1"] = False

        # Backwards-compatibility keys for existing test suites
        st.session_state["interview_questions"] = [initial_q]
        st.session_state["interview_current_q"] = 0
        st.session_state["current_question"] = 0
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 2. ACTIVE LIVE AI VIDEO CALL SCREEN
# ─────────────────────────────────────────────────────────────────────────────

def _render_interview():
    """
    Real-Time AI Video-Call Style Mock Interview:
    - Dual Video Layout: AI Interviewer Tile (Avatar + Waveform) + Candidate Tile (Webcam).
    - AI speaks aloud through browser Text-to-Speech (TTS).
    - Candidate speaks via microphone:
        * Spoken answer is automatically transcribed and sent to AI.
        * NO 'Submit Answer' button required after speaking!
    - AI receives answer, analyzes claims, and generates dynamic follow-up.
    - Full conversational memory preserved.
    - End Interview button synthesizes final evaluation report.
    """
    conversation_history = st.session_state.get("conversation_history", [])
    current_q_text = st.session_state.get("current_question_text", "")
    current_category = st.session_state.get("current_question_category", "Technical")
    current_focus = st.session_state.get("current_question_focus", "")
    last_ack = st.session_state.get("last_acknowledgment", "")
    turn = st.session_state.get("interview_turn", 1)
    evaluations = st.session_state.get("interview_evaluations", [])
    resume_info = st.session_state.get("resume_info", {})
    job_description = st.session_state.get("job_description") or st.session_state.get("global_job_description", "")
    target_role = st.session_state.get("target_role", "Software Engineer")
    cand_name = st.session_state.get("user_name") or (resume_info.get("name") if resume_info else None) or "Candidate"
    ai_status = st.session_state.get("ai_status", "speaking")

    # Safety check: if question is empty, regenerate initial question
    if not current_q_text:
        initial_q, _ = generate_initial_interview_question(resume_info, job_description, target_role)
        current_q_text = initial_q["question"]
        st.session_state["current_question_text"] = current_q_text
        st.session_state["current_ai_message"] = current_q_text
        if not conversation_history:
            st.session_state["conversation_history"] = [{"role": "interviewer", "content": current_q_text}]

    # ── Check for incoming voice answer via URL Query Param (Web Speech API) ───
    if "voice_ans" in st.query_params and st.query_params["voice_ans"]:
        v_ans = st.query_params["voice_ans"]
        del st.query_params["voice_ans"]
        if "t" in st.query_params:
            del st.query_params["t"]
        if v_ans and v_ans.strip():
            _process_answer_and_advance(v_ans.strip())
            st.rerun()

    # ── Top Call Controls Bar ─────────────────────────────────────────────────
    elapsed_sec = int(time.time() - st.session_state.get("interview_start_time", time.time()))
    timer_str = f"{elapsed_sec // 60:02d}:{elapsed_sec % 60:02d}"

    st.markdown(f"""
    <div style="background:#0F172A; border-radius:14px; padding:0.85rem 1.4rem;
                display:flex; justify-content:space-between; align-items:center; margin-bottom:1.2rem;
                box-shadow:0 4px 12px rgba(0,0,0,0.15); flex-wrap:wrap; gap:0.8rem;">
        <div style="display:flex; align-items:center; gap:12px;">
            <span style="display:inline-flex; align-items:center; gap:6px; background:#065F46; color:#A7F3D0;
                         padding:4px 12px; border-radius:20px; font-size:0.78rem; font-weight:700;">
                <span style="color:#10B981; font-size:0.8rem; animation:pulse 1.5s infinite;">●</span> LIVE CALL ACTIVE
            </span>
            <span style="color:#F8FAFC; font-weight:700; font-size:0.95rem;">
                Target: {target_role}
            </span>
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
            <span style="background:#1E293B; border:1px solid #334155; color:#94A3B8; font-size:0.8rem; font-weight:700; padding:4px 12px; border-radius:14px;">
                💬 Turn {turn}
            </span>
            <span style="background:#1E293B; border:1px solid #334155; color:#38BDF8; font-size:0.8rem; font-weight:700; padding:4px 12px; border-radius:14px;">
                ⏱️ {timer_str}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # DUAL VIDEO-CALL TILES (AI Interviewer Avatar & Candidate Webcam)
    # ─────────────────────────────────────────────────────────────────────────
    v_col1, v_col2 = st.columns([1, 1])

    # ── TILE 1: AI Interviewer Video Avatar ──────────────────────────────────
    with v_col1:
        # Dynamic status banner
        if ai_status == "speaking":
            status_badge = '<span style="background:#065F46; color:#A7F3D0; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:700;">🔊 AI is speaking...</span>'
            avatar_glow = "box-shadow:0 0 25px rgba(16, 185, 129, 0.4); border:2.5px solid #10B981;"
            waveform_anim = """
            <div style="display:flex; align-items:center; justify-content:center; gap:4px; height:24px; margin-top:10px;">
                <div style="width:4px; height:18px; background:#10B981; border-radius:2px; animation:wave 0.8s ease-in-out infinite;"></div>
                <div style="width:4px; height:26px; background:#34D399; border-radius:2px; animation:wave 0.6s ease-in-out infinite 0.2s;"></div>
                <div style="width:4px; height:14px; background:#10B981; border-radius:2px; animation:wave 0.9s ease-in-out infinite 0.4s;"></div>
                <div style="width:4px; height:22px; background:#6EE7B7; border-radius:2px; animation:wave 0.7s ease-in-out infinite 0.1s;"></div>
                <div style="width:4px; height:16px; background:#10B981; border-radius:2px; animation:wave 0.8s ease-in-out infinite 0.3s;"></div>
            </div>
            """
        elif ai_status == "thinking":
            status_badge = '<span style="background:#78350F; color:#FDE68A; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:700;">🟡 AI Thinking...</span>'
            avatar_glow = "border:2px solid #F59E0B;"
            waveform_anim = '<div style="color:#FDE68A; font-size:11px; margin-top:8px;">Analyzing response...</div>'
        else:
            status_badge = '<span style="background:#1E293B; color:#94A3B8; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:700;">🟢 Listening to You...</span>'
            avatar_glow = "border:2px solid #334155;"
            waveform_anim = '<div style="color:#94A3B8; font-size:11px; margin-top:8px;">Ready for your answer</div>'

        st.markdown(f"""
        <style>
        @keyframes wave {{
            0%, 100% {{ transform: scaleY(0.4); }}
            50% {{ transform: scaleY(1.3); }}
        }}
        </style>
        <div style="background:#0B132B; border-radius:16px; padding:1.2rem; min-height:270px;
                    display:flex; flex-direction:column; justify-content:space-between; border:1px solid #1E293B;
                    box-shadow:0 8px 24px rgba(0,0,0,0.25); position:relative; overflow:hidden;">
            <!-- Top Overlay -->
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#E2E8F0; font-size:0.82rem; font-weight:700; display:flex; align-items:center; gap:6px;">
                    🤖 AI Technical Interviewer
                </span>
                {status_badge}
            </div>
            <!-- Center Avatar -->
            <div style="text-align:center; padding:1rem 0;">
                <div style="width:96px; height:96px; border-radius:50%; margin:0 auto;
                            background:radial-gradient(circle, #0F766E 0%, #042F2E 100%);
                            display:flex; align-items:center; justify-content:center;
                            font-size:2.8rem; {avatar_glow} transition:all 0.3s ease;">
                    🤖
                </div>
                {waveform_anim}
            </div>
            <!-- Bottom Overlay -->
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.08); padding-top:6px;">
                <span style="color:#94A3B8; font-size:0.75rem;">JobShield AI Engine &bull; Groq LLM</span>
                <span style="color:#A7F3D0; font-size:0.72rem; font-weight:600;">Audio Output: Active</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # AI Question Box directly under interviewer tile
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1.5px solid #A7F3D0; border-left:5px solid #059669;
                    border-radius:12px; padding:1rem 1.2rem; margin-top:0.8rem; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
                <span style="font-size:0.75rem; font-weight:800; color:#065F46; text-transform:uppercase;">
                    Question #{turn} &bull; {current_category}
                </span>
            </div>
            {f'''<div style="background:#F0FDF4; border:1px dashed #A7F3D0; border-radius:6px; padding:0.35rem 0.65rem; margin-bottom:0.5rem; font-size:0.82rem; color:#065F46;">
                <strong>AI Feedback:</strong> "{last_ack}"
            </div>''' if last_ack else ''}
            <div style="color:#0F241A; font-size:1.05rem; font-weight:700; line-height:1.45;">
                "{current_q_text}"
            </div>
            {f'<div style="color:#64748B; font-size:0.78rem; margin-top:0.35rem;">Focus: {current_focus}</div>' if current_focus else ''}
        </div>
        """, unsafe_allow_html=True)

        # ── Spoken AI Audio via Browser Text-to-Speech (TTS) ──────────────────
        if st.session_state.get("interview_tts_enabled", True) and not st.session_state.get(f"q_spoken_{turn}", False):
            safe_speech = current_q_text.replace('"', '\\"').replace('\n', ' ')
            components.html(f"""
            <script>
            function playAIVoice() {{
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    var utter = new SpeechSynthesisUtterance("{safe_speech}");
                    utter.rate = 1.02;
                    utter.pitch = 1.0;
                    var voices = window.speechSynthesis.getVoices();
                    for (var i = 0; i < voices.length; i++) {{
                        if (voices[i].lang.startsWith('en') && (voices[i].name.includes('Natural') || voices[i].name.includes('Google') || voices[i].name.includes('Neural') || voices[i].name.includes('Samantha') || voices[i].name.includes('David'))) {{
                            utter.voice = voices[i];
                            break;
                        }}
                    }}
                    window.speechSynthesis.speak(utter);
                }}
            }}
            if (window.speechSynthesis.getVoices().length > 0) {{
                playAIVoice();
            }} else {{
                window.speechSynthesis.onvoiceschanged = playAIVoice;
            }}
            </script>
            """, height=0)
            st.session_state[f"q_spoken_{turn}"] = True

        # Replay Voice button
        col_rep1, col_rep2 = st.columns([1, 1])
        with col_rep1:
            if st.button("🔊 Replay AI Voice", key=f"btn_replay_voice_{turn}", use_container_width=True):
                safe_speech = current_q_text.replace('"', '\\"').replace('\n', ' ')
                components.html(f"""
                <script>
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    var utter = new SpeechSynthesisUtterance("{safe_speech}");
                    utter.rate = 1.0;
                    window.speechSynthesis.speak(utter);
                }}
                </script>
                """, height=0)

    # ── TILE 2: Candidate Video / Webcam ─────────────────────────────────────
    with v_col2:
        cam_enabled = st.session_state.get("interview_camera_enabled", True)

        if cam_enabled:
            components.html(f"""
            <div style="background:#0B132B; border-radius:16px; padding:0.6rem; min-height:270px;
                        display:flex; flex-direction:column; justify-content:space-between; border:1px solid #1E293B;
                        box-shadow:0 8px 24px rgba(0,0,0,0.25); position:relative; overflow:hidden;">
                <!-- Top Overlay -->
                <div style="display:flex; justify-content:space-between; align-items:center; padding:4px 8px; z-index:2;">
                    <span style="color:#E2E8F0; font-size:0.82rem; font-weight:700; display:flex; align-items:center; gap:6px;">
                        👤 {cand_name} (You)
                    </span>
                    <span id="camBadge" style="background:#065F46; color:#A7F3D0; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:700;">
                        ● Camera Live
                    </span>
                </div>
                <!-- Video Stream -->
                <div style="display:flex; justify-content:center; align-items:center; width:100%; border-radius:10px; overflow:hidden;">
                    <video id="userCamFeed" autoplay playsinline muted style="width:100%; max-height:190px; object-fit:cover; border-radius:10px;"></video>
                </div>
                <!-- Bottom Overlay -->
                <div style="display:flex; justify-content:space-between; align-items:center; padding:4px 8px; border-top:1px solid rgba(255,255,255,0.08);">
                    <span style="color:#94A3B8; font-size:0.75rem;">Microphone: Ready to speak</span>
                    <span style="color:#38BDF8; font-size:0.72rem; font-weight:600;">1080p HD</span>
                </div>
            </div>
            <script>
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
                navigator.mediaDevices.getUserMedia({{ video: {{ width: 640, height: 480 }} }})
                    .then(function(stream) {{
                        var video = document.getElementById('userCamFeed');
                        video.srcObject = stream;
                        video.play();
                    }})
                    .catch(function(err) {{
                        var b = document.getElementById('camBadge');
                        if (b) {{
                            b.innerText = 'Preview Mode';
                            b.style.background = '#334155';
                            b.style.color = '#94A3B8';
                        }}
                    }});
            }}
            </script>
            """, height=280)
        else:
            st.markdown(f"""
            <div style="background:#0B132B; border-radius:16px; padding:1.2rem; min-height:270px;
                        display:flex; flex-direction:column; justify-content:space-between; border:1px solid #1E293B;
                        box-shadow:0 8px 24px rgba(0,0,0,0.25); text-align:center;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#E2E8F0; font-size:0.82rem; font-weight:700;">👤 {cand_name} (You)</span>
                    <span style="background:#334155; color:#94A3B8; padding:3px 10px; border-radius:12px; font-size:11px;">Camera Paused</span>
                </div>
                <div style="padding:1.5rem 0;">
                    <div style="font-size:3rem; margin-bottom:0.3rem;">👤</div>
                    <div style="color:#E2E8F0; font-weight:700; font-size:0.95rem;">Audio-Only Interview Mode</div>
                    <div style="color:#94A3B8; font-size:0.75rem; margin-top:0.2rem;">Speak naturally into your microphone below.</div>
                </div>
                <div style="color:#64748B; font-size:0.75rem;">Camera is turned off</div>
            </div>
            """, unsafe_allow_html=True)

        # Camera & Call Control Buttons
        cam_b1, cam_b2 = st.columns(2)
        with cam_b1:
            if cam_enabled:
                if st.button("⏹️ Pause Camera", key=f"btn_pause_cam_{turn}", use_container_width=True):
                    st.session_state["interview_camera_enabled"] = False
                    st.rerun()
            else:
                if st.button("📷 Enable Camera", key=f"btn_enable_cam_{turn}", use_container_width=True):
                    st.session_state["interview_camera_enabled"] = True
                    st.rerun()
        with cam_b2:
            if st.button("🏁 End Interview", key=f"btn_end_call_top_{turn}", type="secondary", use_container_width=True):
                _end_interview_flow()

    # ─────────────────────────────────────────────────────────────────────────
    # 3. HANDS-FREE VOICE INTERACTION (Primary Mode — No Submit Button)
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#FFFFFF; border:1.5px solid #A7F3D0; border-radius:14px; padding:1.2rem 1.4rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.02); margin-bottom:1rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.8rem; flex-wrap:wrap; gap:0.5rem;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="background:#ECFDF5; border:1px solid #A7F3D0; color:#065F46; font-size:0.8rem;
                             font-weight:800; padding:3px 10px; border-radius:14px; display:inline-flex; align-items:center; gap:5px;">
                    <span>🎤</span> VOICE MODE (PRIMARY)
                </span>
                <span style="color:#0F241A; font-weight:700; font-size:0.95rem;">
                    Speak Your Answer Naturally
                </span>
            </div>
            <div style="font-size:0.75rem; color:#059669; font-weight:600;">
                ✓ Automatic turn processing &bull; No 'Submit Answer' button needed
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 1. Native Streamlit Microphone Audio Input
    # When candidate finishes speaking and stops the mic, it automatically transcribes via Groq Whisper
    # and IMMEDIATELY advances the conversation turn! Zero manual submit clicks required.
    st.markdown("""
    <p style="color:#475569; font-size:0.85rem; margin-bottom:0.4rem;">
        <strong>Method 1: Direct Microphone Input</strong> &mdash; Click mic to record, speak your answer, then click stop. AI processes automatically:
    </p>
    """, unsafe_allow_html=True)

    audio_val = st.audio_input(
        "🎤 Record spoken answer (Click mic, speak, click stop)",
        key=f"audio_mic_turn_{turn}",
        label_visibility="collapsed"
    )

    if audio_val is not None:
        audio_bytes = audio_val.getvalue()
        audio_hash = hash(audio_bytes)
        if st.session_state.get(f"processed_audio_hash_{turn}") != audio_hash:
            st.session_state[f"processed_audio_hash_{turn}"] = audio_hash
            st.session_state["ai_status"] = "thinking"
            with st.spinner("🤖 Groq Whisper is transcribing your spoken answer and formulating interviewer follow-up..."):
                transcript, stt_err = transcribe_audio_groq(audio_val)
            if transcript and transcript.strip():
                st.session_state["current_user_answer"] = transcript.strip()
                st.session_state["current_transcript"] = transcript.strip()
                _process_answer_and_advance(transcript.strip())
                st.rerun()

    # 2. Browser Real-Time Web Speech Recognition Component
    # Live streaming words with instant auto-send on silence/finish speaking
    st.markdown("""
    <p style="color:#475569; font-size:0.85rem; margin:0.8rem 0 0.4rem;">
        <strong>Method 2: Hands-Free Browser Voice Streaming (Real-Time)</strong>:
    </p>
    """, unsafe_allow_html=True)

    components.html("""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:10px 14px; font-family:'Segoe UI', sans-serif;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <button id="streamRecBtn" onclick="toggleWebSpeech()" style="
                    background:linear-gradient(135deg, #059669, #10B981);
                    color:#FFFFFF; border:none; border-radius:8px; padding:7px 15px;
                    font-size:12.5px; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:6px;">
                    <span id="streamRecIcon">🎤</span> <span id="streamRecLabel">Start Speaking</span>
                </button>
                <span id="streamStatus" style="font-size:12px; color:#065F46; font-weight:600;">
                    Click to speak &bull; When done, click Finish to send automatically
                </span>
            </div>
            <button id="sendVoiceBtn" onclick="autoSendVoice()" style="
                background:#059669; color:#FFFFFF; border:none; border-radius:6px; padding:6px 14px;
                font-size:12px; font-weight:700; cursor:pointer; display:none;">
                ⚡ Send Answer Now
            </button>
        </div>
        <div id="liveTranscriptDisplay" style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px;
                    padding:8px 12px; min-height:42px; font-size:13px; color:#1E293B; line-height:1.4;">
            <em style="color:#94A3B8;">Live spoken words stream here...</em>
        </div>
    </div>

    <script>
    var rec = null;
    var isRec = false;
    var fullSpeech = '';

    function autoSendVoice() {
        var text = (fullSpeech || document.getElementById('liveTranscriptDisplay').innerText).trim();
        if (!text || text.includes('Live spoken words stream')) return;
        try {
            var url = new URL(window.parent.location.href);
            url.searchParams.set("voice_ans", text);
            url.searchParams.set("t", Date.now().toString());
            window.parent.location.replace(url.toString());
        } catch(e) {
            console.warn("Auto-submit frame navigation:", e);
        }
    }

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        rec = new SR();
        rec.continuous = true;
        rec.interimResults = true;
        rec.lang = 'en-US';

        rec.onstart = function() {
            isRec = true;
            document.getElementById('streamRecLabel').innerText = 'Finish Speaking';
            document.getElementById('streamRecIcon').innerText = '⏹';
            document.getElementById('streamRecBtn').style.background = '#DC2626';
            document.getElementById('streamStatus').innerHTML = '<span style="color:#DC2626;">● Listening... speak naturally</span>';
            document.getElementById('sendVoiceBtn').style.display = 'inline-block';
        };

        rec.onresult = function(e) {
            var interim = '';
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    fullSpeech += e.results[i][0].transcript + ' ';
                } else {
                    interim += e.results[i][0].transcript;
                }
            }
            var text = (fullSpeech + interim).trim();
            if (text.length > 0) {
                document.getElementById('liveTranscriptDisplay').innerText = text;
            }
        };

        rec.onerror = function(e) {
            document.getElementById('streamStatus').innerText = 'Microphone status: ' + e.error;
        };

        rec.onend = function() {
            isRec = false;
            document.getElementById('streamRecLabel').innerText = 'Start Speaking';
            document.getElementById('streamRecIcon').innerText = '🎤';
            document.getElementById('streamRecBtn').style.background = 'linear-gradient(135deg, #059669, #10B981)';
            document.getElementById('streamStatus').innerText = 'Speech captured. Sending to AI...';
            if (fullSpeech.trim()) {
                autoSendVoice();
            }
        };
    }

    function toggleWebSpeech() {
        if (!rec) return;
        if (isRec) {
            rec.stop();
        } else {
            fullSpeech = '';
            document.getElementById('liveTranscriptDisplay').innerText = 'Listening...';
            try {
                rec.start();
            } catch(err) {
                rec.stop();
                setTimeout(function(){ rec.start(); }, 200);
            }
        }
    }
    </script>
    """, height=105)

    st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # 4. FALLBACK TEXT ANSWER & SKIP CONTROLS
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("⌨️ Microphone unavailable? Type your answer instead", expanded=False):
        st.markdown("<p style='color:#64748B; font-size:0.82rem; margin-bottom:0.4rem;'>Text fallback for users with audio/mic constraints:</p>", unsafe_allow_html=True)
        typed_text = st.text_area(
            "Your Answer",
            height=110,
            placeholder="Type your technical response here...",
            key=f"typed_answer_input_{turn}",
            label_visibility="collapsed"
        )
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1:
            if st.button("📤 Send Typed Answer", key=f"btn_send_typed_{turn}", type="primary", use_container_width=True):
                if typed_text and typed_text.strip():
                    st.session_state["current_user_answer"] = typed_text.strip()
                    _process_answer_and_advance(typed_text.strip())
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter your answer before sending.")
        with col_t2:
            if st.button("⏭️ Skip Topic", key=f"btn_skip_topic_{turn}", use_container_width=True):
                _process_answer_and_advance("[Candidate skipped this question]", is_skip=True)
                st.rerun()

    # ─────────────────────────────────────────────────────────────────────────
    # 5. CHRONOLOGICAL INTERVIEW TRANSCRIPT (Below Video Tiles)
    # ─────────────────────────────────────────────────────────────────────────
    if conversation_history:
        st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.95rem; font-weight:800; color:#0F241A; margin-bottom:0.8rem; display:flex; align-items:center; gap:6px;">
            <span>💬</span> CONVERSATION TRANSCRIPT
        </div>
        """, unsafe_allow_html=True)

        turn_counter = 1
        for msg in conversation_history:
            role = msg.get("role")
            content = msg.get("content", "")

            if role in ["interviewer", "assistant"]:
                st.markdown(f"""
                <div style="background:#F0FDF4; border:1px solid #A7F3D0; border-left:4px solid #059669;
                            border-radius:12px; padding:0.85rem 1.15rem; margin-bottom:0.6rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
                        <span style="font-size:0.75rem; font-weight:800; color:#065F46; text-transform:uppercase;">
                            🤖 AI Interviewer
                        </span>
                        <span style="font-size:0.7rem; color:#64748B;">Turn {turn_counter}</span>
                    </div>
                    <div style="color:#0F241A; font-size:0.94rem; line-height:1.5; font-weight:600;">
                        {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #3B82F6;
                            border-radius:12px; padding:0.85rem 1.15rem; margin-bottom:0.6rem; margin-left:1.5rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
                        <span style="font-size:0.75rem; font-weight:800; color:#1D4ED8; text-transform:uppercase;">
                            👤 {cand_name} (Candidate)
                        </span>
                    </div>
                    <div style="color:#334155; font-size:0.92rem; line-height:1.5;">
                        {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                turn_counter += 1


# ─────────────────────────────────────────────────────────────────────────────
# ANSWER PROCESSING & CONVERSATIONAL TURN ADVANCE
# ─────────────────────────────────────────────────────────────────────────────

def _process_answer_and_advance(answer_text: str, is_skip: bool = False):
    """
    Core Turn Engine:
    1. Records candidate's answer into canonical current_user_answer and dialogue history.
    2. Sends full dialogue history to Groq LLM.
    3. AI understands technical claims and generates dynamic follow-up question.
    4. Follow-up is appended and spoken aloud via TTS.
    """
    st.session_state["current_user_answer"] = answer_text
    st.session_state["ai_status"] = "thinking"

    submitted_payload = answer_text if not is_skip else "[Candidate skipped this question]"

    history = st.session_state.get("conversation_history", [])
    history.append({
        "role": "user",
        "content": submitted_payload
    })
    st.session_state["conversation_history"] = history
    st.session_state.setdefault("interview_answers", []).append(submitted_payload)

    resume_info = st.session_state.get("resume_info", {})
    job_description = st.session_state.get("job_description") or st.session_state.get("global_job_description", "")
    target_role = st.session_state.get("target_role", "Software Engineer")

    # Call AI follow-up engine
    followup, err = generate_conversational_followup(
        conversation_history=history,
        latest_answer=submitted_payload,
        resume_info=resume_info,
        job_description=job_description,
        target_role=target_role
    )

    if err or not followup:
        # Fallback question if Groq had an error
        followup = {
            "next_question": "That's an interesting approach. How did you validate performance and ensure scalability in this system?",
            "category": "Technical",
            "focus_area": "System Scalability",
            "ai_acknowledgment": "Thank you for sharing those details."
        }

    next_q = followup.get("next_question", "")

    # Append interviewer's follow-up to dialogue history
    history.append({
        "role": "interviewer",
        "content": next_q
    })
    st.session_state["conversation_history"] = history

    new_turn = st.session_state.get("interview_turn", 1) + 1
    st.session_state["current_question_text"] = next_q
    st.session_state["current_ai_message"] = next_q
    st.session_state["current_question_category"] = followup.get("category", "Technical")
    st.session_state["current_question_focus"] = followup.get("focus_area", "")
    st.session_state["last_acknowledgment"] = followup.get("ai_acknowledgment", "")
    st.session_state.setdefault("interview_evaluations", []).append(followup)
    st.session_state["interview_turn"] = new_turn
    st.session_state["current_user_answer"] = ""
    st.session_state["current_transcript"] = ""
    st.session_state["ai_status"] = "speaking"
    st.session_state[f"q_spoken_{new_turn}"] = False

    # Legacy keys for test compatibility
    st.session_state.setdefault("interview_questions", []).append({
        "id": new_turn,
        "question": next_q,
        "category": followup.get("category", "Technical"),
        "focus_area": followup.get("focus_area", "")
    })
    st.session_state["interview_current_q"] = new_turn - 1


def _end_interview_flow():
    """Trigger the comprehensive evaluation and navigate to report screen."""
    conversation_history = st.session_state.get("conversation_history", [])
    evaluations = st.session_state.get("interview_evaluations", [])
    resume_info = st.session_state.get("resume_info", {})
    job_description = st.session_state.get("job_description") or st.session_state.get("global_job_description", "")
    target_role = st.session_state.get("target_role", "Software Engineer")

    with st.spinner("📊 Synthesizing comprehensive final evaluation across entire interview transcript..."):
        report, rep_err = generate_final_interview_evaluation(
            conversation_history=conversation_history,
            evaluations=evaluations,
            resume_info=resume_info,
            job_description=job_description,
            target_role=target_role
        )

    if rep_err or not report:
        report, _ = generate_final_report(
            questions=st.session_state.get("interview_questions", []),
            evaluations=evaluations,
            resume_info=resume_info,
            job_description=job_description
        )

    st.session_state["interview_report"] = report
    st.session_state["final_interview_report"] = report
    st.session_state["final_interview_score"] = report.get("overall_score", 0)
    st.session_state["interview_completed"] = True
    st.session_state["interview_active"] = False
    st.session_state["interview_finished"] = True
    st.session_state["interview_state"] = "report"
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 6. FINAL INTERVIEW PERFORMANCE REPORT CARD
# ─────────────────────────────────────────────────────────────────────────────

def _render_final_report():
    """Render comprehensive report card synthesizing the entire conversational interview transcript."""
    report = st.session_state.get("interview_report") or st.session_state.get("final_interview_report", {})
    conversation_history = st.session_state.get("conversation_history", [])

    if not report:
        st.error("❌ No report available. Please complete an interview first.")
        return

    overall = report.get("overall_score", 0)
    category_scores = report.get("category_scores", {})
    tech_score = report.get("technical_knowledge", category_scores.get("Technical Knowledge", overall))
    comm_score = report.get("communication", category_scores.get("Communication", overall))
    rel_score = report.get("relevance", category_scores.get("Relevance", overall))
    comp_score = report.get("completeness", category_scores.get("Completeness", overall))
    ps_score = report.get("problem_solving", category_scores.get("Problem Solving", overall))

    strong_areas = report.get("strong_areas", [])
    improvement_areas = report.get("improvement_areas", [])
    recommendations = report.get("topics_to_practice", report.get("recommendations", []))
    final_feedback = report.get("final_feedback", "")

    perf_label = "Excellent Match" if overall >= 80 else ("Good Alignment" if overall >= 65 else ("Fair Alignment" if overall >= 50 else "Needs Preparation"))
    perf_color = "#059669" if overall >= 80 else ("#D97706" if overall >= 65 else "#DC2626")
    perf_bg = "#ECFDF5" if overall >= 80 else ("#FFFBEB" if overall >= 65 else "#FEF2F2")
    perf_border = "#A7F3D0" if overall >= 80 else ("#FDE68A" if overall >= 65 else "#FECACA")

    # Overall Performance Header
    st.markdown(f"""
    <div style="background:{perf_bg}; border:2px solid {perf_border}; border-radius:18px;
                padding:2.2rem; text-align:center; margin-bottom:1.6rem; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
        <h2 style="color:#0F241A; margin-bottom:0.35rem; font-weight:800; font-size:1.8rem;">
            INTERVIEW COMPLETED
        </h2>
        <div style="font-size:0.9rem; color:#64748B; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">
            Overall Performance Score: {overall}/100
        </div>
        <div style="font-size:4.6rem; font-weight:900; color:{perf_color}; line-height:1; margin:0.4rem 0;">
            {overall}%
        </div>
        <div style="font-size:1.15rem; color:{perf_color}; font-weight:700;">
            {perf_label}
        </div>
        <div style="margin:1rem auto 0; max-width:400px; height:10px; background:#E2E8F0; border-radius:5px; overflow:hidden;">
            <div style="width:{overall}%; height:100%; background:{perf_color}; border-radius:5px;"></div>
        </div>
        <div style="color:#64748B; font-size:0.85rem; margin-top:0.8rem;">
            Based on {len(conversation_history) // 2} interactive dialogue turns synthesized by Groq AI
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5 Performance Pillar Cards
    pillars = [
        ("Technical Knowledge", tech_score),
        ("Communication", comm_score),
        ("Relevance", rel_score),
        ("Completeness", comp_score),
        ("Problem Solving", ps_score),
    ]

    cols = st.columns(5)
    for col, (p_name, p_score) in zip(cols, pillars):
        c_color = "#059669" if p_score >= 75 else ("#D97706" if p_score >= 55 else "#DC2626")
        with col:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px;
                        padding:1rem 0.6rem; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <div style="font-size:1.7rem; font-weight:900; color:{c_color};">{p_score}%</div>
                <div style="color:#0F241A; font-size:0.78rem; font-weight:700; margin-top:0.3rem;">{p_name}</div>
                <div style="height:6px; background:#F1F5F9; border-radius:3px; margin-top:0.55rem; overflow:hidden;">
                    <div style="width:{p_score}%; height:100%; background:{c_color}; border-radius:3px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)

    # Executive Coaching Feedback
    if final_feedback:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #A7F3D0; border-left:4px solid #059669;
                    border-radius:12px; padding:1.2rem 1.4rem; margin-bottom:1.4rem; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
            <div style="font-weight:700; color:#065F46; font-size:0.95rem; margin-bottom:0.35rem;">
                🎯 Executive Interview Summary &amp; Coaching Feedback
            </div>
            <div style="color:#1E293B; font-size:0.9rem; line-height:1.6;">
                {final_feedback}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Strong Areas & Areas to Improve
    sa_col, ia_col = st.columns(2)

    with sa_col:
        st.markdown("""
        <h4 style="font-size:1rem; font-weight:700; color:#065F46; margin-bottom:0.5rem;">
            ★ Key Strengths
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

    # Recommended Topics to Practice
    if recommendations:
        st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <h4 style="font-size:1rem; font-weight:700; color:#0F241A; margin-bottom:0.5rem;">
            📚 Recommended Topics to Practice
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

    # Action Buttons
    st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
    btn1, btn2, btn3 = st.columns(3)

    with btn1:
        if st.button("🔄 Start New Interview Session", type="primary", use_container_width=True, key="btn_restart_interview_final"):
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
        "interview_completed", "interview_active", "interview_finished",
        "speech_transcript", "conversation_history", "current_question_text",
        "current_ai_message", "current_question_category", "current_question_focus",
        "last_acknowledgment", "interview_turn", "current_user_answer", "current_transcript",
        "ai_status"
    ]
    for k in keys_to_reset:
        st.session_state.pop(k, None)

    for k in list(st.session_state.keys()):
        if any(k.startswith(p) for p in ["q_spoken_", "audio_mic_", "processed_audio_hash_"]):
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

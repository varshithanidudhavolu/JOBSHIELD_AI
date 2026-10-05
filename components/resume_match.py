"""
components/resume_match.py
UI for Feature 2 (Resume Analyzer with OpenCV + OCR) and Feature 3 (Resume–Job Match & Skill Gaps).
Styled with HireLens clean career platform aesthetic.
"""

import streamlit as st
from services.resume_service import process_resume_file, extract_resume_info
from services.matching_service import analyze_resume_job_match


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 2: RESUME ANALYZER (OpenCV + OCR + LLM PROFILE EXTRACTION)
# ─────────────────────────────────────────────────────────────────────────────

def render_resume_analyzer():
    """Feature 2: Resume Analyzer page with OpenCV document processing and OCR."""

    st.markdown("""
    <div style="margin-bottom:1.2rem;">
        <h2 style="color:#0F241A; font-weight:800; font-size:1.8rem; margin-bottom:0.25rem;">
            👁️ Resume Analyzer
        </h2>
        <p style="color:#475569; font-size:0.95rem; margin-bottom:0.2rem;">
            Extract resume information using document processing, OpenCV and OCR.
        </p>
        <p style="color:#64748B; font-size:0.8rem; font-style:italic;">
            Supports digital PDFs and scanned image resumes with automated computer vision image enhancement.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload Section ─────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF, PNG, JPG, JPEG)",
        type=["pdf", "png", "jpg", "jpeg", "bmp", "tiff", "webp"],
        key="resume_uploader",
        help="Upload your resume. For scanned images, OpenCV performs grayscale, Gaussian noise reduction, and adaptive thresholding prior to OCR."
    )

    # Quick demo sample profile button for Tech Expo demonstration
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin:0.8rem 0 0.4rem;">
        <span style="font-size:0.85rem; font-weight:600; color:#475569;">Don't have a resume file on hand?</span>
        <span style="font-size:0.75rem; color:#64748B;">Instant sample profile</span>
    </div>
    """, unsafe_allow_html=True)

    col_demo1, col_demo2 = st.columns([2, 3])
    with col_demo1:
        if st.button("📄 Load Naga Varshitha Profile (Sample)", key="btn_load_sample_profile", use_container_width=True):
            sample_text = (
                "Naga Varshitha\n"
                "naga.varshitha@example.edu | +91 98765 43210 | Bangalore, India\n"
                "LinkedIn: linkedin.com/in/nagavarshitha | GitHub: github.com/nagavarshitha\n\n"
                "EDUCATION:\n"
                "B.Tech in Artificial Intelligence & Machine Learning (2022 - 2026)\n"
                "B.M.S. College of Engineering, Bangalore | CGPA: 8.9/10\n\n"
                "SKILLS:\n"
                "Programming: Python, SQL, C++, JavaScript\n"
                "Machine Learning & AI: PyTorch, TensorFlow, Scikit-Learn, OpenCV, RAG, LangChain, NLP\n"
                "Data & Cloud: Pandas, NumPy, FastAPI, Docker, Git, MySQL\n\n"
                "PROJECTS:\n"
                "1. AI Contract Intelligence: Built an automated legal document analysis tool using RAG and vector search in Python with 92% retrieval accuracy.\n"
                "2. Real-Time Fraud & Anomaly Detection: Developed a streaming classification pipeline with Python and scikit-learn.\n"
                "3. Computer Vision Document Scanner: Implemented OpenCV document edge detection, thresholding, and OCR text extraction.\n\n"
                "EXPERIENCE:\n"
                "AI/ML Research Intern at Center for Applied Intelligence (Summer 2024): Developed text preprocessing pipelines and evaluated LLM benchmarks.\n\n"
                "CERTIFICATIONS:\n"
                "- DeepLearning.AI Machine Learning Specialization\n"
                "- AWS Certified Cloud Practitioner"
            )
            _apply_extracted_text(sample_text, "Naga_Varshitha_AI_ML_Resume.pdf", is_image=False)
            st.rerun()

    # If file uploaded, allow user to trigger processing
    if uploaded_file is not None:
        if st.button("⚙️ Process Resume Document", type="primary", key="btn_run_process_file", use_container_width=True):
            _process_uploaded_file(uploaded_file)
    elif st.session_state.get("resume_info"):
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        st.info("📋 Displaying active candidate profile. Upload a new file above to replace it.", icon=None)
        _display_resume_info(st.session_state["resume_info"])


def _process_uploaded_file(uploaded_file):
    """Execute complete file processing: PDF or OpenCV + OCR pipeline."""
    is_image = not uploaded_file.name.lower().endswith('.pdf')

    with st.spinner("Processing document through computer vision & OCR pipeline..."):
        raw_text, error, status = process_resume_file(uploaded_file)

    # Display OpenCV Preprocessed Image if an image was uploaded
    if status.get("processed_image") is not None:
        with st.expander("🖼️ View OpenCV Preprocessed Image (Grayscale, Filtered & Thresholded)", expanded=True):
            st.image(
                status["processed_image"],
                caption="OpenCV Preprocessing Output: Grayscale → Gaussian Blur → Adaptive Thresholding → Deskew",
                use_container_width=True
            )

    if error and not raw_text:
        st.warning("⚠️ Text could not be extracted reliably. Please upload a clearer resume.")
        st.info("💡 You can also paste resume text directly below:")
        manual_text = st.text_area(
            "Paste Resume Text directly:",
            height=140,
            key="manual_resume_text_area",
            placeholder="Paste candidate resume text here..."
        )
        if st.button("Process Pasted Text", type="primary", key="btn_proc_manual_text"):
            if manual_text.strip():
                _apply_extracted_text(manual_text.strip(), uploaded_file.name, is_image=is_image)
                st.rerun()
        return

    if raw_text:
        _apply_extracted_text(raw_text, uploaded_file.name, is_image=is_image, status=status)


def _apply_extracted_text(raw_text: str, filename: str, is_image: bool = False, status: dict = None):
    """Run structured extraction with Groq LLM and synchronize session state."""
    with st.spinner("🤖 Extracting candidate profile and skills with Groq AI..."):
        resume_info, extract_error = extract_resume_info(raw_text)

    if not resume_info:
        st.error("❌ Could not parse resume information. Please check file content.")
        return

    resume_info["_raw_text"] = raw_text

    # Synchronize all persistent session state keys
    st.session_state["resume_info"] = resume_info
    st.session_state["resume_data"] = resume_info
    st.session_state["resume_text"] = raw_text
    st.session_state["extracted_skills"] = resume_info.get("skills", [])
    st.session_state["resume_file"] = filename

    # Show 4-stage pipeline indicators
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    _show_pipeline_indicators(is_image)

    st.success("✅ Resume processed and skills extracted successfully!", icon=None)
    _display_resume_info(resume_info)

    # Progression to Step 3
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
    with col_f2:
        if st.button("Proceed to Resume Match (Step 3) ➡️", type="primary", use_container_width=True, key="btn_resume_to_match"):
            st.session_state["current_page"] = "Resume Match"
            st.rerun()


def _show_pipeline_indicators(is_image: bool):
    """Display the 4-stage pipeline status badges."""
    steps = [
        ("Resume Uploaded", True),
        ("Document Processed", True),
        ("Text Extracted", True),
        ("Skills Identified", True),
    ]
    cols = st.columns(4)
    for col, (label, done) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:10px;
                        padding:0.6rem 0.4rem; text-align:center;">
                <div style="color:#059669; font-weight:800; font-size:1.1rem;">✓</div>
                <div style="color:#065F46; font-size:0.75rem; font-weight:700; margin-top:0.2rem;">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def _display_resume_info(info: dict):
    """Render extracted resume profile cards in HireLens style."""
    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)

    name = info.get("name", "Candidate")
    email = info.get("email", "")
    phone = info.get("phone", "")
    education = info.get("education", [])
    skills = info.get("skills", [])
    projects = info.get("projects", [])
    experience = info.get("experience", [])
    certs = info.get("certifications", [])

    # Header Card
    contact_parts = []
    contact_parts.append(f"👤 <strong>Candidate:</strong> {name if name else 'Not detected'}")
    contact_parts.append(f"📧 <strong>Email:</strong> {email if email else 'Not detected'}")
    contact_parts.append(f"📞 <strong>Phone:</strong> {phone if phone else 'Not detected'}")

    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #059669;
                border-radius:12px; padding:1.1rem 1.4rem; margin-bottom:1.2rem; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
        <div style="font-size:1.05rem; color:#0F241A; margin-bottom:0.3rem;">
            {' &nbsp;|&nbsp; '.join(contact_parts)}
        </div>
        <div style="font-size:0.82rem; color:#64748B;">
            Verified and structured by JobShield AI Document Engine
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Skills
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:1.2rem;
                    margin-bottom:1rem; box-shadow:0 1px 3px rgba(0,0,0,0.02); min-height:220px;">
            <div style="font-size:0.95rem; font-weight:700; color:#0F241A; margin-bottom:0.7rem;">
                🛠️ Extracted Skills ({len(skills) if skills else 0})
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:6px;">
        """, unsafe_allow_html=True)

        if skills:
            skills_html = "".join([
                f'<span style="background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0;'
                f'font-size:0.78rem; font-weight:600; padding:3px 10px; border-radius:16px;">{s}</span>'
                for s in skills
            ])
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#94A3B8; font-size:0.85rem;'>Not detected</span>", unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

        # Projects
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:1.2rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.02); min-height:200px;">
            <div style="font-size:0.95rem; font-weight:700; color:#0F241A; margin-bottom:0.7rem;">
                💡 Projects ({len(projects) if projects else 0})
            </div>
        """, unsafe_allow_html=True)

        if projects:
            for p in projects:
                st.markdown(f"""
                <div style="padding:0.5rem 0.7rem; background:#F8FAF9; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:0.4rem; font-size:0.85rem; color:#1E293B;">
                    &bull; {p}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#94A3B8; font-size:0.85rem;'>Not detected</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Education
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:1.2rem;
                    margin-bottom:1rem; box-shadow:0 1px 3px rgba(0,0,0,0.02); min-height:220px;">
            <div style="font-size:0.95rem; font-weight:700; color:#0F241A; margin-bottom:0.7rem;">
                🎓 Education ({len(education) if education else 0})
            </div>
        """, unsafe_allow_html=True)

        if education:
            for edu in education:
                st.markdown(f"""
                <div style="padding:0.5rem 0.7rem; background:#F8FAF9; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:0.4rem; font-size:0.85rem; color:#1E293B;">
                    &bull; {edu}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#94A3B8; font-size:0.85rem;'>Not detected</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Experience & Certifications
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:1.2rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.02); min-height:200px;">
            <div style="font-size:0.95rem; font-weight:700; color:#0F241A; margin-bottom:0.7rem;">
                💼 Experience & Certifications
            </div>
        """, unsafe_allow_html=True)

        if experience:
            for exp in experience:
                st.markdown(f"""
                <div style="padding:0.4rem 0.6rem; background:#F8FAF9; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:0.35rem; font-size:0.85rem; color:#1E293B;">
                    🏢 {exp}
                </div>
                """, unsafe_allow_html=True)
        if certs:
            for c in certs:
                st.markdown(f"""
                <div style="padding:0.4rem 0.6rem; background:#ECFDF5; border-radius:8px; border:1px solid #A7F3D0; margin-bottom:0.35rem; font-size:0.82rem; color:#065F46;">
                    🏆 {c}
                </div>
                """, unsafe_allow_html=True)
        if not experience and not certs:
            st.markdown("<span style='color:#94A3B8; font-size:0.85rem;'>Not detected</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 3: RESUME–JOB MATCH & SKILL GAP ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def render_resume_match():
    """Feature 3: Resume–Job Match & Skill Gap Analysis page."""

    st.markdown("""
    <div style="margin-bottom:1.2rem;">
        <h2 style="color:#0F241A; font-weight:800; font-size:1.8rem; margin-bottom:0.25rem;">
            🎯 Resume Match
        </h2>
        <p style="color:#475569; font-size:0.95rem; margin-bottom:0.2rem;">
            Compare your resume with the target job and identify skill gaps.
        </p>
        <p style="color:#64748B; font-size:0.8rem; font-style:italic;">
            Calculates an objective match score, separates matching from missing skills, and prioritizes gaps with explanations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Automatically retrieve saved prerequisites from session state ──────────
    resume_info = st.session_state.get("resume_info") or st.session_state.get("resume_data")
    job_description = st.session_state.get("job_description") or st.session_state.get("global_job_description", "")

    has_resume = bool(resume_info and (resume_info.get("skills") or resume_info.get("_raw_text")))
    has_jd = bool(job_description and job_description.strip())

    # ── Status Banner Showing Saved Inputs (No repetitive data entry) ──────────
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:1.2rem 1.4rem;
                margin-bottom:1.4rem; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.8rem;">
            <div style="display:flex; align-items:center; gap:0.6rem;">
                <span style="background:{res_bg}; color:{res_color}; border:1px solid {res_border};
                             font-size:0.8rem; font-weight:700; padding:4px 12px; border-radius:20px;">
                    {res_icon} Resume: {res_status}
                </span>
                <span style="background:{jd_bg}; color:{jd_color}; border:1px solid {jd_border};
                             font-size:0.8rem; font-weight:700; padding:4px 12px; border-radius:20px;">
                    {jd_icon} Job Description: {jd_status}
                </span>
            </div>
            <div style="font-size:0.82rem; color:#64748B;">
                Automatically synchronized from session
            </div>
        </div>
    </div>
    """.format(
        res_bg="#ECFDF5" if has_resume else "#FEF2F2",
        res_color="#065F46" if has_resume else "#991B1B",
        res_border="#A7F3D0" if has_resume else "#FECACA",
        res_icon="✓" if has_resume else "○",
        res_status="Loaded" if has_resume else "Missing",
        jd_bg="#ECFDF5" if has_jd else "#FEF2F2",
        jd_color="#065F46" if has_jd else "#991B1B",
        jd_border="#A7F3D0" if has_jd else "#FECACA",
        jd_icon="✓" if has_jd else "○",
        jd_status="Loaded" if has_jd else "Missing",
    ), unsafe_allow_html=True)

    # Handle missing inputs gracefully with direct actions
    if not has_resume or not has_jd:
        col_m1, col_m2 = st.columns(2)
        if not has_resume:
            with col_m1:
                st.warning("⚠️ Resume not yet processed. Upload in Resume Analyzer or load demo profile.")
                if st.button("➕ Go to Resume Analyzer", key="btn_nav_res_from_match", type="primary"):
                    st.session_state["current_page"] = "Resume Analyzer"
                    st.rerun()
        if not has_jd:
            with col_m2:
                st.warning("⚠️ Job description not yet saved. Enter in Job Risk Detection or paste below.")
                jd_fallback = st.text_area("Quick Job Description input:", height=100, key="quick_match_jd")
                if st.button("Save Job Description", key="btn_save_fallback_jd"):
                    if jd_fallback.strip():
                        st.session_state["job_description"] = jd_fallback.strip()
                        st.session_state["global_job_description"] = jd_fallback.strip()
                        st.rerun()
        return

    # ── Both Available — Trigger Match ─────────────────────────────────────────
    cand_name = resume_info.get("name", "Candidate") or "Candidate"
    skills_count = len(resume_info.get("skills", []))
    jd_words = len(job_description.split())

    col_btn_m, col_btn_clear = st.columns([2, 5])
    with col_btn_m:
        analyze_btn = st.button("🎯 Analyze Match", type="primary", use_container_width=True)
    with col_btn_clear:
        if st.button("🗑️ Clear Match Result", use_container_width=False):
            st.session_state.pop("match_result", None)
            st.session_state.pop("match_analysis", None)
            st.session_state.pop("skill_gaps", None)
            st.rerun()

    if analyze_btn:
        with st.spinner("🎯 Evaluating resume–job match and identifying skill gaps with Groq AI..."):
            result, error = analyze_resume_job_match(resume_info, job_description)

        if error:
            st.error(f"❌ Match analysis error: {error}")
            return

        st.session_state["match_result"] = result
        st.session_state["match_analysis"] = result
        st.session_state["skill_gaps"] = result.get("missing_skills", [])

    active_match = st.session_state.get("match_analysis") or st.session_state.get("match_result")
    if active_match:
        _display_match_results(active_match, resume_info)

        # ── Progression to Step 4: AI Mock Interview ──────────────────────────
        st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
        col_im1, col_im2, col_im3 = st.columns([1, 2, 1])
        with col_im2:
            if st.button("Proceed to AI Mock Interview (Step 4) ➡️", type="primary", use_container_width=True, key="btn_match_to_interview"):
                st.session_state["current_page"] = "Mock Interview"
                st.rerun()


def _display_match_results(result: dict, resume_info: dict):
    """Render match score, matching skills, missing skills, and priority gap analysis."""
    match_score = result.get("match_score", 0)
    matching_skills = result.get("matching_skills", [])
    missing_skills = result.get("missing_skills", [])
    summary = result.get("summary", "")
    recommendations = result.get("recommendations", [])
    exp_match = result.get("experience_match", "")
    edu_match = result.get("education_match", "")

    st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)

    # ── Score Banner ──────────────────────────────────────────────────────────
    score_color = "#059669" if match_score >= 70 else ("#D97706" if match_score >= 45 else "#DC2626")
    score_bg = "#ECFDF5" if match_score >= 70 else ("#FFFBEB" if match_score >= 45 else "#FEF2F2")
    score_border = "#A7F3D0" if match_score >= 70 else ("#FDE68A" if match_score >= 45 else "#FECACA")

    st.markdown(f"""
    <div style="background:{score_bg}; border:2px solid {score_border}; border-radius:16px;
                padding:1.6rem; text-align:center; margin-bottom:1.4rem;">
        <div style="font-size:0.8rem; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.3rem;">
            Resume–Job Match Score
        </div>
        <div style="font-size:4rem; font-weight:900; color:{score_color}; line-height:1;">{match_score}%</div>
        <div style="margin:0.8rem auto 0; max-width:380px; height:10px; background:#E2E8F0; border-radius:5px; overflow:hidden;">
            <div style="width:{match_score}%; height:100%; background:{score_color}; border-radius:5px;"></div>
        </div>
        <div style="color:#1E293B; font-size:0.92rem; margin-top:0.9rem; max-width:650px; margin-left:auto; margin-right:auto; line-height:1.55;">
            {summary}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Matching Skills & Missing Skills Columns ──────────────────────────────
    mc, gc = st.columns(2)

    with mc:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:1.2rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.02); min-height:220px;">
            <div style="font-size:0.98rem; font-weight:700; color:#065F46; margin-bottom:0.7rem;">
                ✓ Matching Skills ({len(matching_skills)})
            </div>
        """, unsafe_allow_html=True)

        if matching_skills:
            for skill in matching_skills:
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:0.5rem; padding:0.45rem 0.75rem;
                            background:#ECFDF5; border:1px solid #A7F3D0; border-radius:8px; margin-bottom:0.35rem;">
                    <span style="color:#059669; font-weight:700;">✓</span>
                    <span style="color:#065F46; font-size:0.88rem; font-weight:600;">{skill}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#94A3B8; font-size:0.85rem;'>No direct skill matches detected.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with gc:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:1.2rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.02); min-height:220px;">
            <div style="font-size:0.98rem; font-weight:700; color:#991B1B; margin-bottom:0.7rem;">
                ✗ Missing Skills & Gaps ({len(missing_skills)})
            </div>
        """, unsafe_allow_html=True)

        if missing_skills:
            for item in missing_skills:
                skill = item.get("skill", "Skill") if isinstance(item, dict) else str(item)
                priority = item.get("learning_priority", "Medium") if isinstance(item, dict) else "Medium"
                p_color = {"High": "#DC2626", "Medium": "#D97706", "Low": "#059669"}.get(priority, "#D97706")

                st.markdown(f"""
                <div style="display:flex; align-items:center; justify-content:space-between; padding:0.45rem 0.75rem;
                            background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; margin-bottom:0.35rem;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span style="color:#DC2626; font-weight:700;">✗</span>
                        <span style="color:#991B1B; font-size:0.88rem; font-weight:600;">{skill}</span>
                    </div>
                    <span style="background:{p_color}; color:#FFFFFF; font-size:0.68rem; padding:2px 7px;
                                 border-radius:4px; font-weight:700;">{priority} Priority</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#059669; font-size:0.85rem;'>✓ No critical skill gaps found! Strong alignment.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Detailed Skill Gap Analysis (Explaining why each skill matters) ────────
    if missing_skills and any(isinstance(m, dict) for m in missing_skills):
        st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="margin-bottom:0.8rem;">
            <h3 style="font-size:1.15rem; font-weight:700; color:#0F241A; margin:0;">
                📊 Detailed Skill Gap Analysis
            </h3>
            <p style="font-size:0.82rem; color:#64748B; margin:0.15rem 0 0;">
                Explanation of why each missing capability matters for this role and how to bridge it.
            </p>
        </div>
        """, unsafe_allow_html=True)

        for item in missing_skills:
            if not isinstance(item, dict):
                continue
            skill = item.get("skill", "")
            reason = item.get("reason", "")
            is_essential = item.get("is_essential", False)
            priority = item.get("learning_priority", "Medium")
            resource = item.get("suggested_resource", "")

            p_color = {"High": "#DC2626", "Medium": "#D97706", "Low": "#059669"}.get(priority, "#D97706")
            badge = "🔴 Essential Requirement" if is_essential else "🟡 Preferred Requirement"

            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px;
                        padding:1rem 1.2rem; margin-bottom:0.7rem; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                    <strong style="color:#0F241A; font-size:0.95rem;">✗ {skill}</strong>
                    <div>
                        <span style="font-size:0.75rem; color:#64748B; margin-right:0.6rem;">{badge}</span>
                        <span style="background:{p_color}; color:#FFFFFF; font-size:0.7rem;
                                     padding:2px 8px; border-radius:4px; font-weight:700;">Priority: {priority}</span>
                    </div>
                </div>
                <div style="color:#475569; font-size:0.86rem; margin-bottom:0.35rem; line-height:1.5;">
                    <strong>Why it matters:</strong> {reason}
                </div>
                {"<div style='color:#059669; font-size:0.82rem; font-weight:600;'>💡 Recommended Action: " + resource + "</div>" if resource else ""}
            </div>
            """, unsafe_allow_html=True)

    # ── Experience & Education Alignment ───────────────────────────────────────
    if exp_match or edu_match:
        st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
        em1, em2 = st.columns(2)
        with em1:
            if exp_match:
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:1rem; height:100%;">
                    <div style="font-size:0.78rem; color:#64748B; font-weight:700; text-transform:uppercase; margin-bottom:0.3rem;">
                        Experience Alignment
                    </div>
                    <div style="color:#1E293B; font-size:0.88rem; line-height:1.5;">{exp_match}</div>
                </div>
                """, unsafe_allow_html=True)
        with em2:
            if edu_match:
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:1rem; height:100%;">
                    <div style="font-size:0.78rem; color:#64748B; font-weight:700; text-transform:uppercase; margin-bottom:0.3rem;">
                        Education Alignment
                    </div>
                    <div style="color:#1E293B; font-size:0.88rem; line-height:1.5;">{edu_match}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Recommendations ────────────────────────────────────────────────────────
    if recommendations:
        st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <h4 style="font-size:1rem; font-weight:700; color:#0F241A; margin-bottom:0.5rem;">
            💡 Application Recommendations
        </h4>
        """, unsafe_allow_html=True)

        for rec in recommendations:
            st.markdown(f"""
            <div style="display:flex; gap:0.6rem; align-items:flex-start; margin-bottom:0.4rem;
                        background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:0.65rem 0.9rem;">
                <span style="color:#059669; font-weight:700;">&rarr;</span>
                <span style="color:#1E293B; font-size:0.88rem;">{rec}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Next Action: Proceed to Mock Interview (Requirement 9 & 10) ───────────
    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%); border:1.5px solid #A7F3D0;
                border-left:5px solid #059669; border-radius:16px; padding:1.6rem 2rem; margin-bottom:1rem;
                box-shadow:0 2px 6px rgba(0,0,0,0.02);">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.8rem;">
            <div>
                <div style="display:inline-flex; align-items:center; gap:6px; background:#FFFFFF; border:1px solid #A7F3D0;
                            padding:3px 12px; border-radius:14px; font-size:0.75rem; font-weight:700; color:#065F46; margin-bottom:0.4rem;">
                    <span>🎥</span> Next Step: AI Video Mock Interview
                </div>
                <h3 style="color:#0F241A; margin:0 0 0.25rem; font-size:1.35rem; font-weight:800;">
                    Ready to practice for this role?
                </h3>
                <p style="color:#475569; font-size:0.88rem; margin:0; line-height:1.5;">
                    Transfer your resume profile, matching skills ({len(matching_skills)} skills), and target job description directly into a real-time conversational AI interview session.
                </p>
            </div>
            <span style="background:#059669; color:#FFFFFF; font-size:0.82rem; font-weight:700; padding:6px 14px; border-radius:12px;">
                Match Score: {match_score}%
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Proceed to Live AI Mock Interview →", type="primary", use_container_width=True, key="btn_proceed_to_mock_interview"):
        # Transfer all 9 context fields into session state
        st.session_state["resume_info"] = resume_info
        st.session_state["resume_data"] = resume_info
        st.session_state["resume_text"] = resume_info.get("_raw_text", "")
        st.session_state["extracted_skills"] = resume_info.get("skills", [])
        st.session_state["candidate_projects"] = resume_info.get("projects", [])
        st.session_state["job_description"] = job_description
        st.session_state["global_job_description"] = job_description
        st.session_state["target_role"] = role_title
        st.session_state["match_score"] = match_score
        st.session_state["match_analysis"] = match_result
        st.session_state["match_result"] = match_result
        st.session_state["matching_skills"] = matching_skills
        st.session_state["missing_skills"] = missing_skills
        st.session_state["skill_gaps"] = missing_skills
        st.session_state["current_page"] = "Mock Interview"
        st.session_state["interview_state"] = "setup"
        st.rerun()

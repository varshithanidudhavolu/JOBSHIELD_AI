"""
services/resume_service.py
Resume processing service: PDF/image loading, OpenCV preprocessing, OCR, and structured extraction via LLM.
"""

import io
from utils.opencv_utils import preprocess_resume_image
from utils.ocr_utils import extract_text_from_image
from utils.text_utils import clean_text, truncate_text, parse_json_from_llm
from services.groq_service import call_groq


# ─────────────────────────────────────────────────────────────────────────────
# File loading & OpenCV Preprocessing
# ─────────────────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, str | None, dict]:
    """
    Extract text from PDF using PyMuPDF and apply OpenCV preprocessing to page preview.
    
    Returns:
        (extracted_text, error_message, status_dict)
    """
    status = {
        "uploaded": True,
        "image_processed": False,
        "text_extracted": False,
        "skills_identified": False,
        "processed_image": None,
        "cv_status": None,
        "error": None
    }

    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError:
            status["error"] = "PyMuPDF not installed. Run: pip install PyMuPDF"
            return "", status["error"], status

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = []
        first_page_pix = None

        for idx, page in enumerate(doc):
            text_parts.append(page.get_text("text"))
            if idx == 0:
                first_page_pix = page.get_pixmap(dpi=150)

        doc.close()
        full_text = '\n'.join(text_parts).strip()

        # Run real OpenCV preprocessing on the first page pixmap for visual demonstration
        if first_page_pix is not None:
            png_bytes = first_page_pix.tobytes("png")
            processed_np, cv_status = preprocess_resume_image(png_bytes)
            status["cv_status"] = cv_status
            if processed_np is not None:
                status["image_processed"] = True
                status["processed_image"] = processed_np

        if not full_text:
            # If scanned PDF without selectable text, run OCR on the OpenCV processed image
            if status.get("processed_image") is not None:
                ocr_text, ocr_err = extract_text_from_image(status["processed_image"])
                if ocr_text:
                    status["text_extracted"] = True
                    return clean_text(ocr_text), None, status
            status["error"] = "Text could not be extracted reliably. Please upload a clearer resume."
            return "", status["error"], status

        status["text_extracted"] = True
        return clean_text(full_text), None, status

    except Exception as e:
        status["error"] = f"PDF extraction error: {str(e)}"
        return "", status["error"], status


def extract_text_from_image_file(file_bytes: bytes, filename: str) -> tuple[str, str | None, dict]:
    """
    Full image pipeline: load image → OpenCV preprocessing (Grayscale, Blur, Threshold, Morphology, Deskew) → OCR → text.

    Returns:
        (extracted_text, error_message, processing_status_dict)
    """
    from PIL import Image

    status = {
        "uploaded": True,
        "image_processed": False,
        "text_extracted": False,
        "skills_identified": False,
        "processed_image": None,
        "cv_status": None,
        "error": None
    }

    try:
        pil_image = Image.open(io.BytesIO(file_bytes))
        if pil_image.mode not in ('RGB', 'L'):
            pil_image = pil_image.convert('RGB')
    except Exception as e:
        status["error"] = f"Cannot open image: {str(e)}"
        return "", f"Cannot open image: {str(e)}", status

    # OpenCV preprocessing: grayscale, blur, threshold, morphology, deskew
    processed_np, cv_status = preprocess_resume_image(pil_image)
    status["cv_status"] = cv_status

    if processed_np is not None:
        status["image_processed"] = True
        status["processed_image"] = processed_np

    if cv_status.get("error"):
        status["error"] = cv_status["error"]

    # OCR extraction
    ocr_input = processed_np if processed_np is not None else pil_image
    text, ocr_error = extract_text_from_image(ocr_input)

    if ocr_error:
        status["error"] = ocr_error
        # Return what was processed so far with status
        return "", ocr_error, status

    if text:
        status["text_extracted"] = True

    return clean_text(text), None, status


def process_resume_file(uploaded_file) -> tuple[str, str | None, dict]:
    """
    Top-level resume processor. Handles PDF and image files.

    Returns:
        (raw_text, error_message, processing_status)
    """
    status = {
        "uploaded": True,
        "image_processed": False,
        "text_extracted": False,
        "skills_identified": False,
        "processed_image": None,
        "error": None
    }

    if uploaded_file is None:
        return "", "No file uploaded.", status

    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.read()

    if filename.endswith('.pdf'):
        text, error, pdf_status = extract_text_from_pdf(file_bytes)
        status.update(pdf_status)
        return text, error, status

    elif filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp')):
        text, error, img_status = extract_text_from_image_file(file_bytes, filename)
        status.update(img_status)
        return text, error, status

    else:
        status["error"] = f"Unsupported file type: {uploaded_file.name}. Please upload PDF or image."
        return "", status["error"], status


# ─────────────────────────────────────────────────────────────────────────────
# LLM-based structured extraction
# ─────────────────────────────────────────────────────────────────────────────

def extract_resume_info(resume_text: str) -> tuple[dict, str | None]:
    """
    Use Groq LLM to extract structured info from raw resume text without inventing details.

    Returns:
        (info_dict, error_message)
    """
    if not resume_text or not resume_text.strip():
        return {}, "Resume text is empty. Cannot extract information."

    truncated = truncate_text(resume_text, 3500)

    system_prompt = """You are an accurate technical resume parsing assistant. Extract structured candidate information.
Rules:
- Extract ONLY what is actually written in the resume text.
- Do NOT invent, assume, or fabricate any skills, jobs, or projects.
- Always respond with valid JSON only. No markdown fences, no extra commentary."""

    prompt = f"""Extract the following information from this resume and return as JSON:

{{
  "name": "Full name or empty string if not found",
  "email": "Email address or empty string",
  "phone": "Phone number or empty string",
  "education": ["Degree, institution, year/CGPA"],
  "skills": ["Skill1", "Skill2", ...],
  "experience": ["Role at Company (Duration): details"],
  "projects": ["Project Name: details"],
  "certifications": ["Certification name"]
}}

RESUME TEXT:
{truncated}

Return ONLY valid JSON."""

    response, error = call_groq(prompt, system_prompt, max_tokens=1600, temperature=0.2)
    if error:
        return _fallback_resume_info(resume_text), None

    parsed = parse_json_from_llm(response)
    if not parsed or not isinstance(parsed, dict):
        return _fallback_resume_info(resume_text), None

    # Ensure standard schema
    defaults = {
        "name": "", "email": "", "phone": "",
        "education": [], "skills": [], "experience": [],
        "projects": [], "certifications": []
    }
    for key, default in defaults.items():
        if key not in parsed:
            parsed[key] = default

    parsed["_raw_text"] = resume_text
    return parsed, None


def _fallback_resume_info(resume_text: str) -> dict:
    """Heuristic fallback extraction when LLM is unavailable."""
    return {
        "name": "Candidate",
        "email": "",
        "phone": "",
        "education": [],
        "skills": _extract_skills_heuristic(resume_text),
        "experience": [],
        "projects": [],
        "certifications": [],
        "_raw_text": resume_text
    }


def _extract_skills_heuristic(text: str) -> list[str]:
    """Extract known technical keywords when LLM is offline."""
    common_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "R", "Go", "Rust",
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "AI",
        "TensorFlow", "PyTorch", "Keras", "scikit-learn", "OpenCV",
        "Pandas", "NumPy", "Matplotlib", "Seaborn",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI",
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux",
        "Git", "GitHub", "CI/CD", "REST API", "Streamlit", "RAG", "LangChain"
    ]
    found = []
    text_lower = text.lower()
    for skill in common_skills:
        if skill.lower() in text_lower:
            found.append(skill)
    return found

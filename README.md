# JobShield AI

AI-powered job safety, resume analysis, resume-job matching and mock interview platform.

JobShield AI helps job seekers and college students verify the authenticity of job/internship postings, extract structured profiles from resumes using OpenCV and OCR, assess resume-job fit with prioritized skill gap analysis, and practice personalized AI mock interviews.

---

## Features

- **Secure Authentication & User Management**: Built-in local authentication with PBKDF2-HMAC-SHA256 password hashing and salt. Dynamic user profiles, protected routes, and session control.
- **Job Risk & Scam Detection**: Heuristic + Groq LLM evaluation of job postings to detect registration fees, payment requests, unrealistic salaries, urgent pressure, and contact fraud. Generates Risk Levels (LOW / MEDIUM / HIGH), 0–100 risk score, red flags, and verification checklists.
- **OpenCV + OCR Resume Analyzer**: Computer vision image preprocessing (Grayscale, Gaussian blur, adaptive thresholding, morphological operations, deskewing) and OCR extraction for PDF and image resumes. Extracts Candidate Name, Email, Phone, Skills, Education, Experience, Projects, and Certifications.
- **Resume–Job Match & Skill Gap Analysis**: Semantic comparison of candidate profiles against job specifications. Generates match scores (0–100%), matching skills, and prioritizes missing skill gaps (High / Medium / Low) with actionable learning recommendations.
- **Real Conversational AI Mock Interview**: 5-question dynamic technical interview powered by Groq LLM. Features live microphone speech-to-text, Groq Whisper STT fallback, browser text-to-speech (TTS), visual interview camera preview, real-time conversational feedback, and a comprehensive final performance report card.

---

## Technology Stack

- **Python 3.10+**
- **Streamlit** (Web Application & Session State Engine)
- **Groq API** (Llama 3.3 / Llama 3.1 LLM inference)
- **OpenCV (opencv-python-headless)** (Document image processing)
- **PyMuPDF (fitz)** (PDF document extraction)
- **Tesseract OCR (pytesseract)** (Optical Character Recognition)
- **Pillow (PIL)** (Image manipulation)
- **HTML5 Camera Input & Video Stream**

---

## Installation & Setup

### 1. Clone Repository & Install Dependencies

```bash
git clone https://github.com/varshithanidudhavolu/JOBSHIELD_AI.git
cd JOBSHIELD_AI
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

*(Never commit your `.env` file or expose your actual API key).*

### 3. Run the Application

```bash
streamlit run app.py
```

The application will launch on `http://localhost:8501`.

---

## Architecture & User Flow

```
1. Add Job Description ──► 2. Upload / Process Resume (OpenCV + OCR)
          │                                  │
          ▼                                  ▼
3. Job Risk Assessment             4. Resume–Job Match & Skill Gaps
                                             │
                                             ▼
                                  5. AI Mock Interview (Video + Groq)
                                             │
                                             ▼
                                  6. Performance Report & Scoring
```

---

## Security & Ethics Notice

- All API keys are loaded strictly via environment variables (`python-dotenv`) and are never exposed in UI or logs.
- Video and camera feeds are processed in the user's browser for interview practice atmosphere; no facial recognition, biometric categorization, or appearance judgment is ever performed.

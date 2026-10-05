import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load environment variables from project root ───────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

def load_project_env():
    """Explicitly load the .env file from the project root."""
    if ENV_FILE.exists():
        load_dotenv(dotenv_path=ENV_FILE, override=True)
    else:
        load_dotenv(override=True)

# Initial load
load_project_env()

# Preferred Groq models (modern, active models with automatic fallback)
DEFAULT_MODEL = "qwen/qwen3.8-27b"
FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]


def get_groq_api_key() -> str | None:
    """
    Safely retrieve and validate GROQ_API_KEY from environment.
    Handles whitespace and accidental quotes.
    Never logs or exposes the key value.
    """
    # Ensure fresh load on Streamlit reruns
    load_project_env()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    # Handle whitespace and accidental quotes
    cleaned = api_key.strip().strip("'\"").strip()
    if not cleaned or cleaned == "your_groq_api_key_here" or cleaned.lower() == "none":
        return None
    if len(cleaned) < 10:
        return None
    return cleaned


def is_api_configured() -> bool:
    """Check if API key is properly configured and valid."""
    return get_groq_api_key() is not None


def get_groq_client():
    """Initialize and return Groq client. Returns (client, error_message)."""
    api_key = get_groq_api_key()
    if not api_key:
        return None, "GROQ_API_KEY is not configured. Please add it to your .env file."
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        return client, None
    except ImportError:
        return None, "Groq library not installed. Run: pip install groq"
    except Exception as e:
        return None, f"Failed to initialize Groq client: {str(e)}"


def test_groq_connection() -> tuple[bool, str]:
    """
    Test Groq API connection with a minimal prompt.
    Returns (success: bool, message: str).
    Safe to call from UI — does NOT expose API key or raw stack traces.
    """
    if not is_api_configured():
        return False, "GROQ_API_KEY is not configured or is invalid in .env file."

    # Perform a minimal test call
    resp, err = call_groq(
        prompt="Reply with the single word: OK",
        max_tokens=20,
        temperature=0.0
    )
    if err:
        return False, f"Groq connection failed: {err}"
    if resp and resp.strip():
        return True, "Groq API connection successful"
    return False, "Groq API responded with an empty message."


def call_groq(prompt: str, system_prompt: str = "", model: str = DEFAULT_MODEL,
              max_tokens: int = 2048, temperature: float = 0.5) -> tuple[str | None, str | None]:
    """
    Make a call to Groq LLM with automatic model fallback for resilience.

    Args:
        prompt: User prompt content
        system_prompt: System-level instructions
        model: Primary Groq model to use
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature

    Returns:
        Tuple of (response_text, error_message)
    """
    client, error = get_groq_client()
    if error:
        return None, error

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # Prepare model candidate list starting with the requested/default model
    models_to_try = [model]
    for fallback in FALLBACK_MODELS:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_error = None
    for target_model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=target_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            content = response.choices[0].message.content
            if content is not None and content.strip():
                return content, None
            # If empty (e.g. reasoning model consumed short token budget), try next or return empty
            if content is not None:
                return content, None
        except Exception as e:
            error_msg = str(e)
            last_error = error_msg
            # If decommissioned or not found, try next candidate model
            if "decommissioned" in error_msg.lower() or "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                continue
            if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                return None, "Invalid Groq API key. Please verify your GROQ_API_KEY in .env file."
            elif "rate limit" in error_msg.lower():
                return None, "Groq API rate limit reached. Please wait a moment and try again."
            else:
                return None, f"Groq API error: {error_msg}"

    return None, f"Groq API error: {last_error or 'All candidate models failed'}"


def transcribe_audio_groq(audio_file) -> tuple[str | None, str | None]:
    """
    Transcribe audio recording using Groq's whisper-large-v3 model.
    Accepts file object, BytesIO, or path.
    Returns (transcript_text, error_message).
    """
    client, error = get_groq_client()
    if error:
        return None, error

    try:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
            response_format="text"
        )
        text = str(transcription).strip() if transcription else ""
        if text:
            return text, None
        return None, "No speech detected in audio."
    except Exception as e:
        return None, f"Speech-to-text error: {str(e)}"

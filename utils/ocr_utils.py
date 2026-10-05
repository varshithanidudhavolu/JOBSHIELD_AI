"""
utils/ocr_utils.py
OCR text extraction from resume images using Tesseract.
Works in tandem with opencv_utils.py for image preprocessing.
"""

import os
import numpy as np
from PIL import Image


def extract_text_from_image(processed_image) -> tuple[str, str | None]:
    """
    Run Tesseract OCR on a preprocessed image.

    Args:
        processed_image: numpy array (from opencv_utils) or PIL Image

    Returns:
        Tuple (extracted_text, error_message)
    """
    try:
        import pytesseract
    except ImportError:
        return "", "pytesseract not installed. Run: pip install pytesseract"

    # Configure Tesseract path for Windows if needed
    _configure_tesseract_path()

    try:
        if isinstance(processed_image, np.ndarray):
            pil_image = Image.fromarray(processed_image)
        elif isinstance(processed_image, Image.Image):
            pil_image = processed_image
        else:
            return "", "Unsupported image format for OCR."

        # Use page segmentation mode 1 (auto with OSD) for full page documents
        custom_config = r'--oem 3 --psm 1'
        text = pytesseract.image_to_string(pil_image, config=custom_config)

        if not text or not text.strip():
            return "", "OCR returned empty text. The image may be too blurry or low-resolution."

        return text.strip(), None

    except Exception as e:
        error_str = str(e)
        if "tesseract" in error_str.lower() and "not found" in error_str.lower():
            return "", (
                "Tesseract OCR engine not found on this system. "
                "Please install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki"
            )
        return "", f"OCR error: {error_str}"


def _configure_tesseract_path():
    """Set Tesseract executable path for Windows installations."""
    try:
        import pytesseract
        # Common Windows Tesseract install paths
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\HP\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
        ]
        # Only override if tesseract isn't already on PATH
        current = pytesseract.pytesseract.tesseract_cmd
        if current == "tesseract" or not os.path.exists(current):
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
    except Exception:
        pass  # Let pytesseract use its default path

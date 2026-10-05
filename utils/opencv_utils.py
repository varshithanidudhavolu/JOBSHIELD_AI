"""
utils/opencv_utils.py
OpenCV-based image preprocessing for resume images/scanned documents.
Applies real computer vision techniques before OCR.
"""

import numpy as np
from PIL import Image
import io


def preprocess_resume_image(image_input) -> tuple:
    """
    Apply OpenCV preprocessing pipeline to a resume image.

    Pipeline:
        1. Load image (from bytes, PIL Image, or numpy array)
        2. Convert to grayscale
        3. Noise reduction (Gaussian blur)
        4. Adaptive thresholding (binarization)
        5. Morphological operations (dilation to close gaps)
        6. Deskewing (straighten tilted scans)

    Args:
        image_input: bytes | PIL.Image | numpy array

    Returns:
        Tuple (processed_numpy_array, status_dict)
    """
    try:
        import cv2
    except ImportError:
        return None, {"error": "OpenCV not installed. Run: pip install opencv-python-headless"}

    status = {
        "uploaded": True,
        "grayscale": False,
        "noise_reduced": False,
        "threshold_applied": False,
        "processed": False,
        "error": None
    }

    try:
        # ── Step 1: Load into numpy array ────────────────────────────────────
        if isinstance(image_input, bytes):
            nparr = np.frombuffer(image_input, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(image_input, Image.Image):
            img = cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, np.ndarray):
            img = image_input.copy()
        else:
            status["error"] = "Unsupported image input type."
            return None, status

        if img is None:
            status["error"] = "Could not decode image."
            return None, status

        # ── Step 2: Grayscale conversion ──────────────────────────────────────
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        status["grayscale"] = True

        # ── Step 3: Noise reduction with Gaussian blur ────────────────────────
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        status["noise_reduced"] = True

        # ── Step 4: Adaptive thresholding (handles uneven lighting) ──────────
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        status["threshold_applied"] = True

        # ── Step 5: Morphological dilation to connect broken text ─────────────
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        dilated = cv2.dilate(thresh, kernel, iterations=1)

        # ── Step 6: Deskew (correct tilt if needed) ──────────────────────────
        deskewed = _deskew(dilated)

        status["processed"] = True
        return deskewed, status

    except Exception as e:
        status["error"] = f"OpenCV processing error: {str(e)}"
        return None, status


def _deskew(image: np.ndarray) -> np.ndarray:
    """
    Detect and correct skew in a binarized image using moments.
    Falls back to original image if deskewing fails.
    """
    try:
        import cv2
        coords = np.column_stack(np.where(image > 0))
        if len(coords) < 10:
            return image

        angle = cv2.minAreaRect(coords)[-1]

        # Normalize angle to (-45, 45) range
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Only deskew if the tilt is meaningful (> 0.5 degrees)
        if abs(angle) < 0.5:
            return image

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        return rotated
    except Exception:
        return image  # Return original if deskew fails


def numpy_to_pil(np_image: np.ndarray) -> Image.Image:
    """Convert a numpy grayscale image back to PIL Image for display/OCR."""
    return Image.fromarray(np_image)


def get_image_info(image_input) -> dict:
    """Return basic image metadata (size, channels) for display."""
    try:
        import cv2
        if isinstance(image_input, bytes):
            nparr = np.frombuffer(image_input, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(image_input, np.ndarray):
            img = image_input
        else:
            return {}

        if img is None:
            return {}

        h, w = img.shape[:2]
        channels = img.shape[2] if len(img.shape) == 3 else 1
        return {"width": w, "height": h, "channels": channels}
    except Exception:
        return {}

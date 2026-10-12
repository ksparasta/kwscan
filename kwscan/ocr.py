"""Optical Character Recognition (OCR) integration module.

Provides utilities to locate the Tesseract OCR engine binary, initialize configuration,
and extract textual data from images using PyTesseract.
"""

import pytesseract

import sys
import shutil
from pathlib import Path

def read_image_text(image):
    """Extract and lowercase text from an image object using Tesseract OCR.

    Args:
        image (PIL.Image.Image): The opened image object to process.

    Returns:
        str: The extracted text converted to lowercase.
    """

    text = pytesseract.image_to_string(
        image,
        lang="ell+eng"
    ).lower()

    return text

def find_tesseract():
    """Locate the Tesseract executable path in bundled application directories or system PATH.

    Returns:
        Path or None: Path object pointing to the Tesseract executable if found, otherwise None.
    """
    # Check bundled Tesseract first
    if getattr(sys, "frozen", False):
        bundled = (
            Path(sys.executable).parent
            / "tesseract"
            / "tesseract.exe"
        )

        if bundled.exists():
            return bundled

    # Check system PATH
    system = shutil.which("tesseract")

    if system:
        return Path(system)

    return None

def init_ocr():
    """Initialize Tesseract OCR by configuring the command path, raising an error if unavailable.

    Raises:
        RuntimeError: If Tesseract executable cannot be located on the system.
    """
    tesseract = find_tesseract()

    if tesseract is None:
        raise RuntimeError(
            "OCR requested, but Tesseract was not found."
        )

    pytesseract.pytesseract.tesseract_cmd = str(tesseract)
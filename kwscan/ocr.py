"""Optical Character Recognition (OCR) integration module.

Provides utilities to locate the Tesseract OCR engine binary, initialize configuration,
and extract textual data from images using PyTesseract.
"""
import sys
import shutil
import platform
from pathlib import Path

import pytesseract
from PIL import Image

def read_image_text(image: Image.Image) -> str:
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

def find_tesseract() -> Path | None:
    """Locate the Tesseract executable path in bundled application directories or system PATH.

    Returns:
        Path | None: Path object pointing to the Tesseract executable if found, otherwise None.
    """
    # Check bundled Tesseract first
    if getattr(sys, "frozen", False):

        # Determine the correct binary name depending on the OS
        exe_name = "tesseract.exe" if platform.system() == "Windows" else "tesseract"

        bundled = (
            Path(sys.executable).parent
            / "tesseract"
            / exe_name
        )

        if bundled.exists():
            return bundled

    # Check system PATH
    system = shutil.which("tesseract")

    if system:
        return Path(system)

    return None

def init_ocr() -> None:
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
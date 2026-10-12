"""File parsing and text extraction module.

Handles reading text contents from various file formats including plain text (.txt),
Microsoft Word documents (.docx), Portable Document Files (.pdf), and image files (.jpg, .png).
"""
from docx import Document
import pypdf
from PIL import Image, UnidentifiedImageError
from .ocr import read_image_text

from io import BytesIO

def read_txt(path):
    """Read and return lowercase text from a plain text file, handling UTF-8 and CP1252 encodings.

    Args:
        path (str or Path): Path to the text file.

    Returns:
        str: The file contents converted to lowercase.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read().lower()
    except UnicodeDecodeError:
        with open(path, "r", encoding="cp1252") as file:
            return file.read().lower()

def read_image(path):
    """Read and extract text from a standalone image file using OCR.

    Args:
        path (str or Path): Path to the image file.

    Returns:
        str: The extracted lowercase text from the image.

    Raises:
        RuntimeError: If the image cannot be opened or parsed.
    """
    try:
        with Image.open(path) as image:
            return read_image_text(image)
    except (UnidentifiedImageError, OSError) as error:
        raise RuntimeError(
            f"Could not open image: {error}"
        ) from error

def read_pdf_image(pdf_image):
    """Extract text from an image embedded within a PDF file using OCR.

    Args:
        pdf_image: The embedded PDF image object containing raw data bytes.

    Returns:
        str: The extracted lowercase text from the embedded image.

    Raises:
        RuntimeError: If the embedded image data cannot be opened or parsed.
    """
    try:
        with  Image.open(BytesIO(pdf_image.data)) as image:
            return read_image_text(image)
    except (UnidentifiedImageError, OSError) as error:
        raise RuntimeError(
            f"Could not open embedded image: {error}"
        ) from error

    
def read_pdf(path, ocr):
    """Extract text from all pages and optionally embedded images of a PDF document.

    Args:
        path (str or Path): Path to the PDF file.
        ocr (bool): Flag indicating whether to process embedded images with OCR.

    Returns:
        str: Combined lowercase text extracted from the document.

    Raises:
        RuntimeError: If the PDF cannot be opened or page text extraction fails.
    """
    try:
        reader = pypdf.PdfReader(path)
    except (OSError, pypdf.errors.PdfReadError) as error:
        raise RuntimeError(
            f"Could not open PDF: {error}"
        ) from error

    text = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text.append((page.extract_text() or "").lower())
        except Exception as error:
                raise RuntimeError(
                    f"Could not extract text from page {page_number}: {error}"
            ) from error

        if not ocr:
            continue

        for image_number, image in enumerate(page.images, start=1):
            try:
                text.append(read_pdf_image(image))
            except Exception as error:
                print(
                    f"\nWarning: could not process image "
                    f"{image_number} on page {page_number} "
                    f"of '{path}': {error}"
                )
    
    return "\n".join(text)

def read_docx(path, ocr=False):
    """Extract text from paragraphs, headers, footers, tables, and optionally images of a Word document.

    Args:
        path (str or Path): Path to the Word document (.docx).
        ocr (bool, optional): Flag indicating whether to process document images with OCR. Defaults to False.

    Returns:
        str: Combined lowercase text extracted from all parts of the document.
    """
    document = Document(path)
    text_paragraphs = "\n".join(paragraph.text.lower() for paragraph in document.paragraphs)

    header_text = ""
    footer_text = ""
    for section in document.sections:
        header_text += "\n".join(p.text.lower()
                                for p in section.header.paragraphs
                            )
        footer_text += "\n".join(p.text.lower()
                                 for p in section.footer.paragraphs
                            )

    table_text = "\n".join(cell.text.lower()
                           for table in document.tables
                           for row in table.rows
                           for cell in row.cells
                        )

    image_text = ""
    if ocr:
        for rel in document.part.rels.values():
            if "image" in rel.reltype:
                with Image.open(BytesIO(rel.target_part.blob)) as image:
                    image_text += "\n" + read_image_text(image)
            

            
    return text_paragraphs + header_text + footer_text + table_text + image_text

READERS = {
    "txt": read_txt,
    "pdf": read_pdf,
    "docx": read_docx,
    "jpg": read_image,
    "jpeg": read_image,
    "png": read_image
}
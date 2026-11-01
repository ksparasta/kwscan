"""File scanning and keyword search engine module.

Provides folder mapping, multi-threaded file traversal, and keyword matching functionalities.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from .readers import READERS

SUPPORTED_TYPES = (".txt", ".pdf", ".docx")
SUPPORTED_IMAGE_TYPES = (".jpg", ".jpeg", ".png")
IGNORED = ("~$",)


def get_file_info(path: Path)-> dict:
    """Extract normalized file metadata including absolute path string and file type extension.

    Args:
        path (Path): Path object for the target file.

    Returns:
        dict: Dictionary containing 'file' absolute path string and 'type' extension.
    """
    file_type = path.suffix.replace('.', '')

    return {'file': str(path.resolve()), 'type': file_type.lower()}

def scan_folder(folder_path: Path, ocr: bool) -> list[dict]:
    """Recursively traverse a directory to locate supported files while ignoring temporary files.

    Args:
        folder_path (Path): Directory Path object to scan.
        ocr (bool): Flag indicating whether image file types should be included.

    Returns:
        list[dict]: List of file metadata dictionaries found in the folder.
    """
    file_list = []

    supported_types = SUPPORTED_TYPES + (SUPPORTED_IMAGE_TYPES if ocr else ())

    for (root, dirs, files) in folder_path.walk():
        for file in files:
            if file.lower().startswith(IGNORED):
                continue
            if file.lower().endswith(supported_types):
                file_list.append(get_file_info(root / file))
    return file_list

def search_needles(file_info: dict, needles: list[str], ocr: bool) -> bool:
    """Check if any of the target keywords exist within the text content of a file.

    Args:
        file_info (dict): File metadata dictionary containing path and type.
        needles (list[str]): Lowercase keywords to search for.
        ocr (bool): Flag indicating whether OCR should be passed to the reader.

    Returns:
        bool: True if any keyword matches the file content, otherwise False.
    """
    reader = READERS[file_info['type']]
    
    text = reader(
        file_info['file'],
        *(ocr,) if file_info["type"] in ("pdf", "docx") else ()
    )

    return any(word in text for word in needles)

def scan_file(file_info: dict, needles: list[str], ocr: bool) -> dict | None:
    """Scan a single file for keywords and handle any exceptions that occur during processing.

    Args:
        file_info (dict): File metadata dictionary.
        needles (list[str]): Lowercase keywords to search for.
        ocr (bool): Flag indicating whether OCR is enabled.

    Returns:
        dict | None: Result dictionary with file path and error status if matched or failed, else None.
    """
    try:
        if search_needles(file_info, needles, ocr):
            return {
                "file": file_info['file'],
                "error": None
            }
    except Exception as error:
        return {
            "file": file_info["file"],
            "error": error
        }

    return None

def map_folder(path: Path, ocr: bool) -> list[dict]:
    """Map a given path target (file or directory) into a list of file metadata items to scan.

    Args:
        path (Path): Target file or directory Path object.
        ocr (bool): Flag indicating whether OCR is enabled.

    Returns:
        list[dict]: List of file metadata entries.
    """
    if path.is_file():
        return [get_file_info(path)]

    return scan_folder(path, ocr)

def scan_files(files: list[dict], needles: list[str], workers: int, ocr: bool) -> tuple:
    """Scan a list of files concurrently using a thread pool and track progress with a progress bar.

    Args:
        files (list[dict]): List of file metadata entries to process.
        needles (list[str]): Keywords to search for.
        workers (int): Maximum number of concurrent thread workers.
        ocr (bool): Flag indicating whether OCR is enabled.

    Returns:
        tuple: A tuple containing (matching_files list, errors list).
    """
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                scan_file,
                file,
                needles,
                ocr
            )
            for file in files
        ]

        matching_files = []
        errors = []
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Scanning"
        ):
            result = future.result()

            if result is None:
                continue

            if result["error"] is not None:
                errors.append(result)
            else:
                matching_files.append(result)

    return matching_files, errors
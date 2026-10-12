"""Command Line Interface for the kwscan utility.

Handles command-line argument parsing, user input validation, OCR initialization,
and result logging for the keyword scanner application.
"""

import argparse
from pathlib import Path

from .readers import READERS
from .ocr import init_ocr
from .scanner import map_folder, scan_files, SUPPORTED_TYPES, SUPPORTED_IMAGE_TYPES


def existing_path(value):
    """Validate that the provided path exists and is a directory or a supported filetype.

    Args:
        value (str): The path string provided via the command line.

    Returns:
        Path: The validated Path object.

    Raises:
        argparse.ArgumentTypeError: If the path does not exist or the file type is unsupported.
    """
    path = Path(value)

    if not path.exists():
        raise argparse.ArgumentTypeError(
            f"path does not exist: {value}"
        )

    total_supported_types = SUPPORTED_TYPES + SUPPORTED_IMAGE_TYPES
    if path.is_file() and path.suffix.lower() not in total_supported_types:
        raise argparse.ArgumentTypeError(
            f"Not supported file"
        )
    return path 

def workers_number(value):
    """Validate that the worker count argument is a positive integer.

    Args:
        value (str): The worker count string provided via the command line.

    Returns:
        int: The validated number of workers.

    Raises:
        argparse.ArgumentTypeError: If the value cannot be parsed as an integer or is less than 1.
    """
    try:
        value = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "workers must be an integer"
        )

    if value < 1:
        raise argparse.ArgumentTypeError(
            f"workers must be greater than 0"
        )

    return value

def parse_args():
    """Parse command-line arguments for the kwscan tool.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(
        prog = "kwscan",
        description = "Search files for specified keywords."
    )

    parser.add_argument(
        "path",
        type = existing_path,
        help = "File or directory to scan."
    )

    parser.add_argument(
        "--contains",
        nargs = "+",
        required = True,
        help = "Keywords to search for."
    )

    parser.add_argument(
        "--workers",
        type = workers_number,
        default = 4,
        help = "Number of concurrent workers (default: 4)."
    )

    parser.add_argument(
        "--ocr",
        action = "store_true",
        help = "Enable OCR for images and scanned PDFs (default: False)."
    )

    return parser.parse_args()

def log_results(matching_files):
    """Log files that successfully matched the keyword search criteria.

    Args:
        matching_files (list of dict): List containing file metadata dictionaries for matches.
    """

    print(f"{len(matching_files)} matching files found:\n")
    for file in matching_files:
        print(f"{file['file']}")

def log_errors(errors):
    """Log errors encountered during file scanning and processing.

    Args:
        errors (list of dict): List containing file path and error details for failed files.
    """

    if not errors:
        return

    print(f"\n{len(errors)} files could not be processed:\n")
    for error in errors:
        print(f"{error['file']}")
        print(f"  Error: {error['error']}\n")

def main():
    """Execute the primary execution flow of the kwscan CLI tool."""

    args = parse_args()

    if args.ocr:
        try:
            init_ocr()
        except RuntimeError as error:
            print(f"Error: {error}")
            return

    print("Looking for files...")
    files = map_folder(args.path, args.ocr)
    print(f"{len(files)} files found")
    needles = [word.lower() for word in args.contains]

    matching_files, errors = scan_files(
        files,
        needles,
        args.workers,
        args.ocr
    )

    log_results(matching_files)

    log_errors(errors)

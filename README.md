# kwscan

`kwscan` is a command-line utility built to scan directories and document files for specific keywords. It combines native document parsers with OCR capabilities to locate text across modern file formats and images.

## Features

* **Multi-Threaded Processing:** Parallelized file scanning using concurrent workers for fast directory traversal.
* **Multi-Format Document Parsing:**
  * **PDF Documents:** Page-by-page text parsing via `pypdf`.
  * **Microsoft Word (`.docx`):** Structural text parsing via `python-docx`.
  * **Microsoft Excel (`.xlsx`, `.xls`):** Sheet and cell text extraction.
  * **Images & Scanned Documents:** Automated text extraction via `pillow` and `pytesseract`.
* **Live Progress Tracking:** Visual feedback powered by `tqdm`.

## Prerequisites

* **Python:** Version `3.10` or higher.
* **Tesseract OCR Engine:** (Optional, required only when using the `--ocr` flag)
  * **macOS:** `brew install tesseract`
  * **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
  * **Windows:** Install via the [Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki) and ensure it is added to your system `PATH`.

## Installation

Clone the repository and install it locally:

```bash
git clone https://github.com/ksparasta/kwscan.git
cd kwscan
pip install .
```

## Usage

Once installed, invoke `kwscan` directly from your terminal:

```bash
usage: kwscan [-h] --contains CONTAINS [CONTAINS ...] [--workers WORKERS] [--ocr] path
```

### Positional Arguments

| Argument | Description |
| --- | --- |
| `path` | File or directory to scan. |

### Options

| Flag / Option | Description | Default |
| --- | --- | --- |
| `-h`, `--help` | Show the help message and exit. | — |
| `--contains CONTAINS [CONTAINS ...]` | One or more keywords to search for (required). | — |
| `--workers WORKERS` | Number of concurrent workers. | `4` |
| `--ocr` | Enable OCR for images and scanned PDFs. | `False` |

### Examples

**Basic Keyword Search:**

```bash
kwscan /path/to/documents --contains "invoice"
```

**Search for Multiple Keywords:**

```bash
kwscan ./reports --contains "invoice" "total" "due date"
```

**Search with Custom Worker Count:**

```bash
kwscan ~/Documents/Archive --contains "urgent" --workers 8
```

**Enable OCR Scanning for Images and Scanned PDFs:**

```bash
kwscan ./scans --contains "receipt" --ocr --workers 6
```

## License

This project is open-source software licensed under the **MIT License**.
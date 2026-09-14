from pathlib import Path
import re

import fitz
import pytesseract
from PIL import Image


# Locate the project folders.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "data" / "raw" / "cdf" / "source_documents"
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "cdf" / "ocr_text"

# Location of Tesseract on Windows.
TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Use OCR if normal extraction finds less than 100 characters.
MINIMUM_TEXT_CHARACTERS = 100

# Higher DPI improves recognition of small table text.
OCR_DPI = 250


def safe_filename(filename: str) -> str:
    """Convert a PDF filename into a consistent text filename."""
    name = Path(filename).stem.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def page_to_image(page: fitz.Page) -> Image.Image:
    """Render one PDF page as a high-resolution image."""
    scale = OCR_DPI / 72
    matrix = fitz.Matrix(scale, scale)

    pixmap = page.get_pixmap(
        matrix=matrix,
        colorspace=fitz.csRGB,
        alpha=False,
    )

    image = Image.frombytes(
        "RGB",
        (pixmap.width, pixmap.height),
        pixmap.samples,
    )

    return image


def extract_page_text(page: fitz.Page) -> tuple[str, str]:
    """
    Use the PDF's embedded text when sufficient text exists.
    Otherwise, use OCR and preserve spacing between table columns.
    """
    normal_text = page.get_text("text").strip()

    if len(normal_text) >= MINIMUM_TEXT_CHARACTERS:
        return normal_text, "normal extraction"

    image = page_to_image(page)

    ocr_text = pytesseract.image_to_string(
        image,
        lang="eng",
        config="--oem 3 --psm 4 -c preserve_interword_spaces=1",
    ).strip()

    return ocr_text, "OCR"


def process_pdf(pdf_path: Path) -> None:
    """Extract readable text from every page in one PDF."""
    output_name = f"{safe_filename(pdf_path.name)}_ocr.txt"
    output_path = OUTPUT_DIR / output_name

    document = fitz.open(pdf_path)
    extracted_pages = []

    print(f"\nProcessing: {pdf_path.name}")
    print(f"Pages: {document.page_count}")

    try:
        for page_number, page in enumerate(document, start=1):
            text, method = extract_page_text(page)

            page_output = (
                f"===== PAGE {page_number} =====\n"
                f"Extraction method: {method}\n\n"
                f"{text}\n"
            )

            extracted_pages.append(page_output)

            print(
                f"  Page {page_number} of {document.page_count}: "
                f"{method} ({len(text)} characters)"
            )
    finally:
        document.close()

    output_path.write_text(
        "\n".join(extracted_pages),
        encoding="utf-8",
    )

    print(f"Saved: {output_path}")


def main() -> None:
    """Process all PDF source documents."""
    if not TESSERACT_PATH.exists():
        raise FileNotFoundError(
            f"Tesseract was not found at: {TESSERACT_PATH}"
        )

    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)

    if not SOURCE_DIR.exists():
        raise FileNotFoundError(
            f"Source-document directory was not found: {SOURCE_DIR}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(
        SOURCE_DIR.glob("*.pdf"),
        key=lambda path: path.name.lower(),
    )

    if not pdf_files:
        print(f"No PDF files were found in: {SOURCE_DIR}")
        return

    print("Starting CDF document OCR...")
    print(f"PDF documents found: {len(pdf_files)}")
    print(f"OCR output directory: {OUTPUT_DIR}")

    completed = 0
    failed = 0

    for pdf_path in pdf_files:
        try:
            process_pdf(pdf_path)
            completed += 1
        except Exception as error:
            failed += 1
            print(f"\nFAILED: {pdf_path.name}")
            print(f"Reason: {error}")

    print("\nOCR processing finished.")
    print(f"Successfully processed: {completed}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
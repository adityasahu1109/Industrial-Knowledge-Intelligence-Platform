import pytesseract
from pdf2image import convert_from_path

def parse_ocr_pdf(file_path: str) -> list[dict]:
    """
    Extracts text from a scanned PDF or image using Tesseract OCR.
    Returns: list of dicts {"text": str, "page": int, "section": str}
    """
    pages = []
    try:
        # Convert PDF to list of images
        images = convert_from_path(file_path)
        
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            if text.strip():
                pages.append({
                    "text": text.strip(),
                    "page": i + 1,
                    "section": f"Scanned Page {i + 1}"
                })
    except Exception as e:
        print(f"OCR Error processing {file_path}: {e}")
        # Return empty list on failure so the pipeline can gracefully fail or retry
        
    return pages

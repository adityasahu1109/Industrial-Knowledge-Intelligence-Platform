import fitz  # PyMuPDF

def parse_pdf(file_path: str) -> list[dict]:
    """
    Extracts text from a digital PDF page by page.
    Returns: list of dicts {"text": str, "page": int, "section": str}
    """
    pages = []
    doc = fitz.open(file_path)
    
    current_section = ""
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Simple heuristic for section headers: find largest font size
        blocks = page.get_text("dict").get("blocks", [])
        max_size = 0
        potential_header = ""
        
        for b in blocks:
            if b.get("type") == 0: # text block
                for line in b.get("lines", []):
                    for span in line.get("spans", []):
                        if span.get("size", 0) > max_size:
                            max_size = span.get("size")
                            potential_header = span.get("text", "").strip()
        
        if potential_header and max_size > 12: # assuming > 12pt is a header
            current_section = potential_header
            
        text = page.get_text("text")
        
        if text.strip():
            pages.append({
                "text": text.strip(),
                "page": page_num + 1,
                "section": current_section
            })
            
    return pages

def is_scanned(file_path: str) -> bool:
    """
    Simple check: if pages have very little text but have images, it might be scanned.
    For Phase 1, we just return False and assume digital PDFs.
    """
    doc = fitz.open(file_path)
    if len(doc) == 0:
        return False
        
    page = doc[0]
    text_len = len(page.get_text("text").strip())
    has_images = len(page.get_images()) > 0
    
    # If first page has < 50 chars but has images, likely scanned
    return text_len < 50 and has_images

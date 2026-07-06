import docx

def parse_docx(file_path: str) -> list[dict]:
    """
    Extracts text from a DOCX file.
    Returns: list of dicts {"text": str, "page": int, "section": str}
    Note: DOCX doesn't have a strict concept of 'pages' like PDF, 
    so we chunk by paragraphs or sections.
    """
    pages = []
    doc = docx.Document(file_path)
    
    current_section = ""
    current_text = []
    page_num = 1
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        # Very simple heuristic: if it's a heading style, treat as section
        if para.style.name.startswith('Heading'):
            # Save previous chunk
            if current_text:
                pages.append({
                    "text": "\n".join(current_text),
                    "page": page_num,
                    "section": current_section
                })
                current_text = []
                page_num += 1
            current_section = text
        else:
            current_text.append(text)
            
        # Arbitrary chunking if text gets too long
        if len("\n".join(current_text)) > 1500:
            pages.append({
                "text": "\n".join(current_text),
                "page": page_num,
                "section": current_section
            })
            current_text = []
            page_num += 1
            
    if current_text:
        pages.append({
            "text": "\n".join(current_text),
            "page": page_num,
            "section": current_section
        })
        
    return pages

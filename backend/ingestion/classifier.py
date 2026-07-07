import base64
import os
from core.ollama_client import vision_analyze, chat_json

VALID_DOC_TYPES = ["p&id", "pfd", "manual", "sop", "inspection_report", "other"]

def classify_document(file_path: str, filename: str) -> str:
    """
    Automatically classifies a document into one of the known doc_types.
    Uses Qwen-VL for images/PDFs and Llama 3.1 for text files.
    """
    ext = file_path.lower().split('.')[-1]
    
    try:
        # Vision-based classification for images and PDFs
        if ext in ['png', 'jpg', 'jpeg', 'pdf']:
            if ext == 'pdf':
                import fitz
                doc = fitz.open(file_path)
                if len(doc) == 0:
                    return "other"
                page = doc[0]
                # Lower DPI for classification is fine to save processing time
                pix = page.get_pixmap(dpi=72)
                temp_img_path = file_path + ".thumb.png"
                pix.save(temp_img_path)
                with open(temp_img_path, "rb") as f:
                    base64_image = base64.b64encode(f.read()).decode('utf-8')
                os.remove(temp_img_path)
            else:
                with open(file_path, "rb") as f:
                    base64_image = base64.b64encode(f.read()).decode('utf-8')
                    
            vision_prompt = f"""
            Analyze the first page of this industrial document (filename: {filename}).
            Categorize this document exactly as ONE of the following categories:
            - p&id (Piping and Instrumentation Diagram / Schematic)
            - pfd (Process Flow Diagram)
            - manual (Equipment Manual / Datasheet)
            - sop (Standard Operating Procedure)
            - inspection_report (Maintenance or Inspection Report)
            - other (Any other document)
            
            Return ONLY the category name exactly as written above, with no additional text or punctuation.
            """
            
            result = vision_analyze(vision_prompt, base64_image).strip().lower()
            # Clean up the output in case it wrapped in quotes or added periods
            result = ''.join(c for c in result if c.isalnum() or c in ['&', '_'])
            
            # Map back to valid types
            if "p&id" in result or "pid" in result:
                return "p&id"
            if "pfd" in result:
                return "pfd"
            if "manual" in result:
                return "manual"
            if "sop" in result:
                return "sop"
            if "inspection" in result or "report" in result:
                return "inspection_report"
            return "other"
            
        # Text-based classification for Word / Excel
        elif ext in ['docx', 'xlsx']:
            snippet = ""
            if ext == 'docx':
                from ingestion.parsers.docx_parser import parse_docx
                pages = parse_docx(file_path)
                snippet = pages[0]["text"][:1000] if pages else ""
            elif ext == 'xlsx':
                from ingestion.parsers.excel_parser import parse_excel
                pages = parse_excel(file_path)
                snippet = pages[0]["text"][:1000] if pages else ""
                
            text_prompt = f"""
            Analyze the first few lines of this industrial document (filename: {filename}).
            Content:
            {snippet}
            
            Categorize this document exactly as ONE of the following categories:
            - manual (Equipment Manual / Datasheet)
            - sop (Standard Operating Procedure)
            - inspection_report (Maintenance or Inspection Report)
            - other (Any other document)
            
            Return ONLY a JSON object like this: {{"category": "manual"}}
            """
            
            result = chat_json(
                system="You are an industrial document classifier.", 
                user=text_prompt,
                schema={"type": "object", "properties": {"category": {"type": "string"}}}
            )
            
            cat = result.get("category", "other").strip().lower()
            if cat in VALID_DOC_TYPES:
                return cat
            return "other"
            
    except Exception as e:
        print(f"Failed to auto-classify document {filename}: {e}")
        
    return "other"

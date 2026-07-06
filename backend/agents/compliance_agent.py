from retrieval.vector_store import get_collection
from core.ollama_client import chat_json
from core.database import SessionLocal, Document
from datetime import datetime

def run_compliance_scan(standard_name: str, doc_type: str = "all") -> dict:
    """
    Scans the database of documents against a provided compliance standard (e.g. OSHA 1910.119).
    Returns a compliance report.
    """
    collection = get_collection()
    
    # 1. Fetch relevant documents
    # Filter by doc_type if specified
    where_clause = None
    if doc_type and doc_type != "all":
        where_clause = {"doc_type": doc_type}
        
    results = collection.get(where=where_clause, limit=20, include=["documents", "metadatas"])
    
    if not results or not results["documents"]:
        return {
            "status": "error", 
            "message": "No documents available in the knowledge base to scan."
        }
        
    import json
    
    def extract_text_only(obj):
        if isinstance(obj, dict):
            return " ".join(extract_text_only(v) for v in obj.values())
        elif isinstance(obj, list):
            return " ".join(extract_text_only(i) for i in obj)
        elif isinstance(obj, str):
            return obj
        else:
            return str(obj)

    clean_docs = []
    for doc_str in results["documents"]:
        try:
            doc_obj = json.loads(doc_str)
            clean_docs.append(extract_text_only(doc_obj))
        except:
            clean_docs.append(doc_str.replace("{", "").replace("}", ""))
            
    context_text = "\n\n---\n\n".join(clean_docs)
    
    # Check if we have regulatory text
    import os
    reg_text = ""
    # backend is run from the backend directory, so data is one level up
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # this gets to backend
    project_root = os.path.dirname(base_dir) # this gets to project root
    
    if "OISD" in standard_name:
        reg_file = os.path.join(project_root, "data", "regulatory", "oisd_117_excerpt.md")
        if os.path.exists(reg_file):
            with open(reg_file, 'r', encoding='utf-8') as f:
                reg_text = f.read()
    elif "Factory Act" in standard_name or "Factory" in standard_name:
        reg_file = os.path.join(project_root, "data", "regulatory", "factory_act_excerpt.md")
        if os.path.exists(reg_file):
            with open(reg_file, 'r', encoding='utf-8') as f:
                reg_text = f.read()
                
    reg_context = f"\n\nRegulatory Standard Text ({standard_name}):\n{reg_text}\n" if reg_text else ""
    
    # Extract unique filenames for transparency
    scanned_files = list(set([meta.get("filename", "Unknown") for meta in results.get("metadatas", [])]))
    
    # 2. Ask LLM to find gaps
    system_prompt = f"""
    You are an expert industrial compliance auditor.
    CRITICAL INSTRUCTION: You MUST evaluate the facility documents STRICTLY against the rules in {standard_name}.
    Do NOT report generic maintenance issues (like leaks, vibration, or wear) UNLESS they explicitly violate a clause in the standard text provided below!
    
    {reg_context}
    """
    
    user_prompt = f"""
    Here is the facility documentation to audit:
    
    {context_text}
    
    Generate the compliance audit report JSON now.
    You MUST reply with ONLY a valid JSON object matching this exact structure. Replace the bracketed text with your actual analysis. Do not include markdown formatting:
    {{
        "overall_score": <integer from 0 to 100>,
        "summary": "<your executive summary>",
        "gaps": [
            {{
                "severity": "<CRITICAL, HIGH, MEDIUM, or LOW>",
                "finding": "<describe the specific violation of the standard>",
                "recommendation": "<how to fix it>"
            }}
        ]
    }}
    If there are no gaps that violate {standard_name}, return an empty list for "gaps" and an overall_score of 100.
    """
    
    try:
        report = chat_json(system_prompt, user_prompt)
        print(f"RAW LLM REPORT: {report}")
        
        # Validation Fallback
        if not isinstance(report, dict) or "overall_score" not in report or "gaps" not in report:
            print("Warning: LLM returned malformed compliance report. Using fallback.")
            report = {
                "overall_score": 0,
                "summary": "Failed to parse compliance data from LLM. Please try scanning again.",
                "gaps": []
            }
            
        report["standard_name"] = standard_name
        report["scan_date"] = datetime.utcnow().isoformat()
        report["scanned_files"] = scanned_files
        
        # Save to database
        db = SessionLocal()
        from core.database import ComplianceReport
        import json
        db_report = ComplianceReport(
            regulation_id=standard_name,
            doc_type_filter=doc_type,
            overall_score=report.get("overall_score", 0),
            report_data=json.dumps(report)
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        report_id = db_report.id
        db.close()
        
        report["report_id"] = report_id
        return report
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Compliance scan failed: {e}")
        return {
            "status": "error",
            "message": "Failed to generate compliance report due to LLM error."
        }

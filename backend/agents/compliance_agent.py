import os
import json
import yaml
from datetime import datetime
from retrieval.vector_store import get_collection
from core.ollama_client import chat_json
from core.database import SessionLocal, ComplianceReport

def run_compliance_scan(standard_name: str, doc_type: str = "all") -> dict:
    """
    Scans the database of documents against a provided compliance standard (e.g. OSHA 1910.119).
    Performs a clause-by-clause evaluation and returns a structured compliance report.
    """
    collection = get_collection()
    
    # 1. Load the Regulatory Text
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(base_dir)
    
    reg_file = None
    if "OISD" in standard_name:
        reg_file = os.path.join(project_root, "data", "regulatory", "oisd_117_excerpt.md")
    elif "Factory Act" in standard_name or "Factory" in standard_name:
        reg_file = os.path.join(project_root, "data", "regulatory", "factory_act_excerpt.md")
        
    if not reg_file or not os.path.exists(reg_file):
        return {"status": "error", "message": "Regulatory standard not found."}
        
    with open(reg_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 2. Parse Frontmatter and Clauses
    applies_to = ["sop", "manual", "inspection_report", "p&id", "pfd"]
    if content.startswith('---'):
        parts = content.split('---', 2)
        try:
            frontmatter = yaml.safe_load(parts[1])
            if frontmatter and "applies_to" in frontmatter:
                applies_to = frontmatter["applies_to"]
        except Exception as e:
            print(f"YAML Parse Error: {e}")
        content = parts[2].strip()
        
    clauses = []
    blocks = content.split('\n## ')
    for i, block in enumerate(blocks):
        if i == 0 and not content.startswith('## '):
            continue
        c = '## ' + block if i > 0 else block
        title = c.split('\n')[0].replace('## ', '').strip()
        clauses.append({'title': title, 'text': c})
        
    if not clauses:
        # Fallback if no specific clauses found
        clauses = [{'title': standard_name, 'text': content}]
        
    # Incorporate user-specified document filter (from UI dropdown) if any
    if doc_type and doc_type != "all":
        user_types = [doc_type]
        if doc_type == "report": user_types = ["inspection_report"]
        if doc_type == "procedure": user_types = ["sop"]
        # Intersect standard's applies_to with user's filter
        applies_to = [t for t in applies_to if t in user_types]
        
    where_clause = {"doc_type": {"$in": applies_to}} if applies_to else None
    
    # 3. Clause-by-Clause Scanning
    all_clauses_report = []
    total_score = 0
    scanned_files = set()
    
    for clause in clauses:
        print(f"Scanning Clause: {clause['title']}")
        
        # Embed the clause text using Ollama
        from core.ollama_client import embed
        query_embedding = embed(clause['text'])
        
        # Semantic search for documents relevant strictly to THIS clause
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=10,
            where=where_clause,
            include=["documents", "metadatas"]
        )
        
        if not results or not results["documents"] or not results["documents"][0]:
            all_clauses_report.append({
                "clause_number": clause['title'],
                "clause_text_summary": clause['text'][:100] + "...",
                "status": "not-applicable",
                "evidence": [],
                "gap_description": "No relevant operational or inspection documents found in the database to evaluate against this clause.",
                "remediation": "N/A"
            })
            total_score += 100
            continue
            
        clean_docs = []
        for i, doc_str in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            filename = meta.get("filename", "Unknown")
            scanned_files.add(filename)
            try:
                doc_obj = json.loads(doc_str)
                text = " ".join([str(v) for v in doc_obj.values() if isinstance(v, str)])
                clean_docs.append(f"Document: {filename}\nExcerpt: {text}")
            except:
                clean_docs.append(f"Document: {filename}\nExcerpt: {doc_str}")
                
        context_text = "\n\n---\n\n".join(clean_docs)
        
        system_prompt = f"""
        You are an expert industrial compliance auditor.
        CRITICAL INSTRUCTION: You MUST evaluate the facility documents STRICTLY against the following regulation clause.
        Do NOT report generic issues unless they explicitly violate the clause.
        
        REGULATION CLAUSE ({clause['title']}):
        {clause['text']}
        """
        
        user_prompt = f"""
        Here is the facility documentation evidence retrieved for this clause:
        
        {context_text}
        
        Evaluate the facility's compliance with THIS CLAUSE ONLY.
        Reply with a valid JSON object matching this exact structure:
        {{
            "clause_number": "{clause['title']}",
            "clause_text_summary": "<One sentence summary of the clause's main requirement>",
            "status": "<compliant, partial, gap, or not-applicable>",
            "finding_title": "<A very brief, 5-10 word title summarizing the finding.>",
            "detailed_gap_analysis": "<A comprehensive, highly detailed analysis of exactly how the facility fails or meets this clause. Minimum 3 sentences. Explain the technical implications.>",
            "evidence": [
                {{
                    "document": "<filename of evidence document>",
                    "exact_quote": "<exact quote from the document if available>",
                    "explanation": "<detailed explanation of how this evidence proves compliance or non-compliance>"
                }}
            ],
            "remediation_action": "<A brief 1-sentence summary of the required fix.>",
            "detailed_remediation_plan": "<A comprehensive, step-by-step engineering or administrative remediation plan to achieve full compliance. Minimum 3 sentences.>"
        }}
        """
        
        try:
            report = chat_json(system_prompt, user_prompt)
            print(f"RAW LLM REPORT for {clause['title']}: {report}")
            
            all_clauses_report.append(report)
            
            status = report.get("status", "gap").lower()
            if status in ["compliant", "not-applicable"]:
                total_score += 100
            elif status == "partial":
                total_score += 50
            else:
                total_score += 0
                
        except Exception as e:
            print(f"Error scanning clause {clause['title']}: {e}")
            all_clauses_report.append({
                "clause_number": clause['title'],
                "clause_text_summary": clause['text'][:100] + "...",
                "status": "error",
                "evidence": [],
                "gap_description": "Failed to analyze this clause due to an AI processing error.",
                "remediation": "Retry scan."
            })
            total_score += 0
            
    final_score = int(total_score / len(clauses)) if clauses else 100
    
    gap_count = sum(1 for g in all_clauses_report if g.get("status", "").lower() in ["gap", "partial"])
    
    summary = f"Audit complete. Evaluated {len(clauses)} clauses against {len(scanned_files)} relevant documents. Identified {gap_count} areas requiring attention."
    
    final_report = {
        "overall_score": final_score,
        "summary": summary,
        "gaps": all_clauses_report, # we keep the key 'gaps' for backwards compatibility in the UI, but it now contains all clauses
        "standard_name": standard_name,
        "scan_date": datetime.utcnow().isoformat(),
        "scanned_files": list(scanned_files)
    }
    
    # Save to database
    db = SessionLocal()
    db_report = ComplianceReport(
        regulation_id=standard_name,
        doc_type_filter=doc_type,
        overall_score=final_score,
        report_data=json.dumps(final_report)
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    report_id = db_report.id
    db.close()
    
    final_report["report_id"] = report_id
    return final_report

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents.compliance_agent import run_compliance_scan
from core.database import get_db, ComplianceReport, Job
from sqlalchemy.orm import Session
import json
import io
import uuid
from routers.jobs import publish_sync

router = APIRouter(prefix="/api/compliance", tags=["compliance"])

class ScanRequest(BaseModel):
    standard_name: str
    doc_type: str = "all"

def run_compliance_job(job_id: str, standard_name: str, doc_type: str):
    from core.database import SessionLocal
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    try:
        result = run_compliance_scan(standard_name, doc_type)
        if "status" in result and result["status"] == "error":
            raise Exception(result["message"])
            
        job.status = "done"
        job.result_json = json.dumps(result)
        db.commit()
        publish_sync(job_id, {"type": "done", "result": result})
    except Exception as e:
        error_payload = {"type": "error", "error": str(e)}
        job.status = "failed"
        job.result_json = json.dumps(error_payload)
        db.commit()
        publish_sync(job_id, error_payload)
    finally:
        db.close()

@router.post("/scan")
def scan_documents(req: ScanRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    job = Job(id=job_id, type="compliance_scan", status="running")
    db.add(job)
    db.commit()
    
    background_tasks.add_task(run_compliance_job, job_id, req.standard_name, req.doc_type)
    return {"job_id": job_id}

from fastapi.responses import HTMLResponse

@router.get("/report/{report_id}/pdf")
def get_report_pdf(report_id: int, db: Session = Depends(get_db)):
    report = db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
    if not report or not report.report_data:
        raise HTTPException(status_code=404, detail="Report not found")
        
    try:
        data = json.loads(report.report_data)
        
        # Count stats for summary
        compliant = sum(1 for c in data.get('gaps', []) if c.get('status', '').lower() in ['compliant', 'not-applicable'])
        gaps = sum(1 for c in data.get('gaps', []) if c.get('status', '').lower() in ['gap', 'partial'])
        total = len(data.get('gaps', []))
        
        # Build HTML content
        score_color = "text-red-600"
        bg_score = "bg-red-50 border-red-200"
        score_val = data.get('overall_score', 0)
        if score_val >= 85: 
            score_color = "text-emerald-600"
            bg_score = "bg-emerald-50 border-emerald-200"
        elif score_val >= 60: 
            score_color = "text-amber-600"
            bg_score = "bg-amber-50 border-amber-200"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Audit Report - {data.get('standard_name', 'Standard')}</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Merriweather:ital,wght@0,300;0,700;1,300&display=swap" rel="stylesheet">
            <style>
                body {{ font-family: 'Inter', sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; background: #fff; }}
                .serif {{ font-family: 'Merriweather', serif; }}
                @media print {{
                    @page {{ margin: 1.5cm; size: A4; }}
                    .page-break {{ page-break-before: always; }}
                    .no-break {{ page-break-inside: avoid; }}
                    .shadow-sm {{ box-shadow: none !important; border: 1px solid #e5e7eb; }}
                }}
                .cover-page {{ height: 25cm; display: flex; flex-direction: column; justify-content: center; }}
            </style>
        </head>
        <body class="text-gray-900 max-w-4xl mx-auto">
            
            <!-- Cover Page -->
            <div class="cover-page">
                <div class="border-b-4 border-gray-900 pb-6 mb-12">
                    <h1 class="text-5xl font-black tracking-tight text-gray-900 mb-4">REGULATORY<br/>COMPLIANCE AUDIT</h1>
                    <h2 class="text-2xl text-gray-500 font-light">{data.get('standard_name', 'Unknown Standard')}</h2>
                </div>
                
                <div class="grid grid-cols-2 gap-12 mb-16">
                    <div>
                        <h3 class="text-sm font-bold uppercase tracking-widest text-gray-400 mb-2">Audit Date</h3>
                        <p class="text-lg font-medium">{data.get('scan_date', 'Unknown')[:10]}</p>
                    </div>
                    <div>
                        <h3 class="text-sm font-bold uppercase tracking-widest text-gray-400 mb-2">Scope</h3>
                        <p class="text-lg font-medium">{len(data.get('scanned_files', []))} Documents Analyzed</p>
                    </div>
                </div>
                
                <div class="{bg_score} border rounded-2xl p-10 flex items-center justify-between no-break">
                    <div>
                        <h3 class="text-sm font-bold uppercase tracking-widest text-gray-500 mb-1">Final Compliance Score</h3>
                        <p class="text-gray-600 text-sm">Aggregate score based on {total} evaluated clauses.</p>
                    </div>
                    <div class="text-6xl font-black {score_color} font-mono">{score_val}%</div>
                </div>
            </div>
            
            <!-- Executive Summary -->
            <div class="page-break pt-10">
                <div class="flex items-center gap-4 mb-8">
                    <div class="h-8 w-2 bg-blue-600 rounded"></div>
                    <h2 class="text-3xl font-bold tracking-tight">Executive Summary</h2>
                </div>
                
                <div class="prose max-w-none serif text-gray-700 text-lg leading-relaxed mb-12">
                    {data.get('summary', '')}
                </div>
                
                <div class="grid grid-cols-3 gap-6 mb-12">
                    <div class="bg-gray-50 border border-gray-200 rounded-xl p-6 text-center">
                        <div class="text-4xl font-black text-gray-800 mb-2">{total}</div>
                        <div class="text-xs font-bold uppercase tracking-wider text-gray-500">Clauses Scanned</div>
                    </div>
                    <div class="bg-emerald-50 border border-emerald-200 rounded-xl p-6 text-center">
                        <div class="text-4xl font-black text-emerald-700 mb-2">{compliant}</div>
                        <div class="text-xs font-bold uppercase tracking-wider text-emerald-600">Compliant / N/A</div>
                    </div>
                    <div class="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
                        <div class="text-4xl font-black text-red-700 mb-2">{gaps}</div>
                        <div class="text-xs font-bold uppercase tracking-wider text-red-600">Identified Gaps</div>
                    </div>
                </div>
            </div>
            
            <!-- Detailed Findings -->
            <div class="page-break pt-10">
                <div class="flex items-center gap-4 mb-8 border-b pb-6">
                    <div class="h-8 w-2 bg-gray-900 rounded"></div>
                    <h2 class="text-3xl font-bold tracking-tight">Detailed Findings & Remediation</h2>
                </div>
                
                <div class="space-y-10">
        """
        
        for clause in data.get('gaps', []):
            status = clause.get('status', 'gap').lower()
            
            # Styling based on status
            border_color = "border-red-300"
            bg_header = "bg-red-50 text-red-900"
            badge = "bg-red-200 text-red-900"
            icon = "✕ NON-COMPLIANT"
            
            if status in ['compliant', 'not-applicable']:
                border_color = "border-gray-200"
                bg_header = "bg-gray-50 text-gray-800"
                badge = "bg-emerald-100 text-emerald-800"
                icon = "✓ COMPLIANT"
                if status == 'not-applicable': icon = "- NOT APPLICABLE"
            elif status == 'partial':
                border_color = "border-amber-300"
                bg_header = "bg-amber-50 text-amber-900"
                badge = "bg-amber-200 text-amber-900"
                icon = "! PARTIAL COMPLIANCE"
                
            html += f"""
            <div class="no-break border-2 {border_color} rounded-xl overflow-hidden shadow-sm">
                <!-- Clause Header -->
                <div class="{bg_header} px-6 py-4 flex items-center justify-between border-b {border_color}">
                    <h4 class="font-bold text-lg">{clause.get('clause_number', 'Unknown Clause')}</h4>
                    <span class="px-3 py-1 rounded text-xs font-bold uppercase tracking-wider {badge}">
                        {icon}
                    </span>
                </div>
                
                <div class="p-6 bg-white">
                    <div class="mb-6">
                        <h5 class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-2">Standard Requirement</h5>
                        <p class="text-gray-700 text-sm italic border-l-2 border-gray-300 pl-4 py-1">{clause.get('clause_text_summary', '')}</p>
                    </div>
            """
            
            if status in ['gap', 'partial']:
                html += f"""
                    <div class="mb-6">
                        <h5 class="text-[10px] font-bold uppercase tracking-widest text-red-500 mb-2 flex items-center gap-2">
                            Detected Violation / Gap
                        </h5>
                        <p class="text-gray-900 font-medium leading-relaxed">{clause.get('detailed_gap_analysis', clause.get('gap_description', ''))}</p>
                    </div>
                """
            else:
                html += f"""
                    <div class="mb-6">
                        <h5 class="text-[10px] font-bold uppercase tracking-widest text-emerald-500 mb-2">Audit Status</h5>
                        <p class="text-gray-900 leading-relaxed">{clause.get('detailed_gap_analysis', clause.get('gap_description', ''))}</p>
                    </div>
                """
            
            evidence = clause.get('evidence', [])
            if evidence:
                html += """<div class="mb-6">
                    <h5 class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-3">Cited Evidence Logs</h5>
                    <div class="grid gap-4">"""
                for ev in evidence:
                    html += f"""
                        <div class="bg-gray-50 p-5 rounded-lg border border-gray-200 text-sm">
                            <div class="font-mono text-xs text-blue-700 font-semibold mb-2 flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                                {ev.get('document', '')}
                            </div>
                            <div class="text-gray-600 serif mb-3 italic">"{ev.get('exact_quote', ev.get('excerpt_summary', ''))}"</div>
                            <div class="text-gray-800 text-sm">{ev.get('explanation', '')}</div>
                        </div>
                    """
                html += """</div></div>"""
                    
            remediation = clause.get('detailed_remediation_plan', clause.get('remediation', ''))
            if status in ['gap', 'partial'] and remediation and remediation != 'N/A':
                html += f"""
                    <div class="bg-amber-50 border-l-4 border-amber-400 p-6 rounded-r-lg mt-4">
                        <h5 class="text-[10px] font-bold uppercase tracking-widest text-amber-800 mb-3">Required Remediation Plan</h5>
                        <p class="text-amber-900 font-medium leading-relaxed">{remediation}</p>
                    </div>
                """
                
            html += """
                </div>
            </div>
            """
            
        html += """
                </div>
            </div>
            <script>
                // Slight delay to ensure fonts load before printing
                window.onload = function() { 
                    setTimeout(() => { window.print(); }, 500);
                }
            </script>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents.compliance_agent import run_compliance_scan
from core.database import get_db, ComplianceReport
from sqlalchemy.orm import Session
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

router = APIRouter(prefix="/api/compliance", tags=["compliance"])

class ScanRequest(BaseModel):
    standard_name: str
    doc_type: str = "all"

@router.post("/scan")
def scan_documents(req: ScanRequest):
    result = run_compliance_scan(req.standard_name, req.doc_type)
    if "status" in result and result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/report/{report_id}/pdf")
def get_report_pdf(report_id: int, db: Session = Depends(get_db)):
    report = db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
    if not report or not report.report_data:
        raise HTTPException(status_code=404, detail="Report not found")
        
    try:
        data = json.loads(report.report_data)
        
        # Generate PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        elements.append(Paragraph(f"Compliance Audit Report: {data.get('standard_name', 'Unknown')}", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Date: {data.get('scan_date', 'Unknown')}", styles['Normal']))
        elements.append(Paragraph(f"Overall Score: {data.get('overall_score', 'N/A')}", styles['Normal']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Summary", styles['Heading2']))
        elements.append(Paragraph(data.get('summary', ''), styles['Normal']))
        elements.append(Spacer(1, 12))
        
        elements.append(Paragraph("Identified Gaps", styles['Heading2']))
        for gap in data.get('gaps', []):
            elements.append(Paragraph(f"<b>Severity: {gap.get('severity', '').upper()}</b>", styles['Normal']))
            elements.append(Paragraph(f"Finding: {gap.get('finding', '')}", styles['Normal']))
            elements.append(Paragraph(f"Recommendation: {gap.get('recommendation', '')}", styles['Normal']))
            elements.append(Spacer(1, 12))
            
        doc.build(elements)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=audit_report_{report_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

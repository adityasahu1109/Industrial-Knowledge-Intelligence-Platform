import { useState, useEffect } from 'react';
import { ShieldAlert, CheckCircle, AlertTriangle, Loader2, Play, FileText, Download } from 'lucide-react';
import { fetchJson } from '../../api/client';

export function ComplianceDashboard() {
  const [standard, setStandard] = useState("OSHA 1910.119 - Process Safety Management");
  const [docType, setDocType] = useState("all");
  const [scanning, setScanning] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [recentScans, setRecentScans] = useState<any[]>([]);

  // Load recent scans from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('recent_compliance_scans');
      if (saved) {
        setRecentScans(JSON.parse(saved));
      }
    } catch (e) {
      console.error("Could not load recent scans", e);
    }
  }, []);

  const runScan = async () => {
    setScanning(true);
    setError(null);
    setReport(null);
    
    try {
      const data = await fetchJson('/compliance/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ standard_name: standard, doc_type: docType })
      });
      setReport(data);
      
      // Save to recent scans
      const newScan = {
        standard_name: standard,
        date: new Date().toISOString(),
        score: data.overall_score
      };
      
      setRecentScans(prev => {
        const updated = [newScan, ...prev].slice(0, 5); // Keep last 5
        localStorage.setItem('recent_compliance_scans', JSON.stringify(updated));
        return updated;
      });
      
    } catch (err: any) {
      setError(err.message || "Scan failed");
    } finally {
      setScanning(false);
    }
  };

  const handleExport = () => {
    if (!report) return;
    
    if (report.report_id) {
      // Open PDF in new tab, bypassing fetch/CORS blob issues
      window.open(`http://localhost:8000/api/compliance/report/${report.report_id}/pdf`, '_blank');
    } else {
      // Fallback for older reports
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
      const downloadAnchorNode = document.createElement('a');
      downloadAnchorNode.setAttribute("href", dataStr);
      downloadAnchorNode.setAttribute("download", `compliance_report_${new Date().getTime()}.json`);
      document.body.appendChild(downloadAnchorNode);
      downloadAnchorNode.click();
      downloadAnchorNode.remove();
    }
  };

  const scoreColor = report?.overall_score >= 90 ? 'text-operational' : 
                     report?.overall_score >= 70 ? 'text-warning' : 'text-critical';

  return (
    <div className="max-w-7xl mx-auto h-full flex flex-col p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold mb-1">Compliance Gap Scanner</h1>
          <p className="text-text-muted text-sm">
            Audit the facility's knowledge base against regulatory frameworks.
          </p>
        </div>
        
        {report && (
          <button 
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 bg-surface-alt border border-border rounded-lg text-sm font-medium hover:bg-surface-hover transition-colors"
          >
            <Download size={16} /> Export Report
          </button>
        )}
      </div>

      <div className="flex gap-6 flex-1 min-h-0">
        {/* Left Side: Setup */}
        <div className="w-1/3 flex flex-col gap-6">
          <div className="bg-surface-alt border border-border rounded-xl p-5">
            <h3 className="font-semibold flex items-center gap-2 mb-4">
              <ShieldAlert size={18} className="text-primary" />
              Scan Configuration
            </h3>
            
            <div className="mb-4">
              <label className="block text-xs font-medium text-text-dim uppercase tracking-wider mb-2">Target Standard</label>
              <select 
                value={standard} 
                onChange={(e) => setStandard(e.target.value)}
                className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text focus:outline-none focus:border-primary/50 transition-colors"
                disabled={scanning}
              >
                <option value="OISD Standard 117">OISD Standard 117 (Pressure Vessels)</option>
                <option value="Factory Act 1948">Factory Act 1948 (Hazardous Processes)</option>
                <option value="OSHA 1910.119 - Process Safety Management">OSHA 1910.119 (PSM)</option>
                <option value="ISO 9001:2015 - Quality Management">ISO 9001:2015</option>
                <option value="API 570 - Piping Inspection Code">API 570</option>
                <option value="EPA RMP - Risk Management Plan">EPA RMP</option>
              </select>
            </div>

            <div className="mb-6">
              <label className="block text-xs font-medium text-text-dim uppercase tracking-wider mb-2">Document Filter</label>
              <select 
                value={docType} 
                onChange={(e) => setDocType(e.target.value)}
                className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text focus:outline-none focus:border-primary/50 transition-colors"
                disabled={scanning}
              >
                <option value="all">All Documents</option>
                <option value="manual">Manuals</option>
                <option value="procedure">Procedures / SOPs</option>
                <option value="report">Inspection Reports</option>
              </select>
            </div>
            
            <button 
              onClick={runScan}
              disabled={scanning}
              className="w-full py-2.5 bg-primary/10 text-primary border border-primary/20 rounded-lg font-medium text-sm flex items-center justify-center gap-2 hover:bg-primary hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {scanning ? (
                <><Loader2 size={16} className="animate-spin" /> Scanning KB...</>
              ) : (
                <><Play size={16} /> Run Full Scan</>
              )}
            </button>
          </div>
          
          <div className="bg-surface-alt border border-border rounded-xl p-5 flex-1 overflow-y-auto">
             <h3 className="font-semibold text-sm mb-3">Recent Scans</h3>
             <div className="space-y-3">
               {recentScans.length === 0 ? (
                 <div className="text-sm text-text-dim opacity-60 italic">No recent scans.</div>
               ) : (
                 recentScans.map((scan, i) => (
                   <div key={i} className="flex flex-col gap-1 text-sm p-3 bg-surface rounded border border-border/50 hover:border-primary/30 transition-colors">
                     <div className="flex items-center justify-between">
                       <div className="flex items-center gap-2">
                         <FileText size={14} className="text-text-muted" />
                         <span className="truncate max-w-[150px] font-medium" title={scan.standard_name}>
                           {scan.standard_name.split('-')[0].trim()}
                         </span>
                       </div>
                       <span className={`text-xs font-bold font-mono ${
                         scan.score >= 90 ? 'text-operational' : 
                         scan.score >= 70 ? 'text-warning' : 'text-critical'
                       }`}>
                         {scan.score !== undefined ? `${scan.score}%` : 'N/A'}
                       </span>
                     </div>
                     <span className="text-[10px] text-text-dim ml-5">
                       {new Date(scan.date).toLocaleDateString()}
                     </span>
                   </div>
                 ))
               )}
             </div>
          </div>
        </div>

        {/* Right Side: Results */}
        <div className="w-2/3 bg-surface-alt border border-border rounded-xl overflow-hidden flex flex-col relative">
          {!report && !scanning && !error ? (
            <div className="flex-1 flex flex-col items-center justify-center text-text-dim p-10 text-center">
              <ShieldAlert size={48} className="mb-4 opacity-20" />
              <h3 className="text-lg font-medium text-text mb-2">No Active Report</h3>
              <p className="text-sm max-w-sm">Select a standard on the left and run a scan to identify compliance gaps in the current document base.</p>
            </div>
          ) : scanning ? (
             <div className="flex-1 flex flex-col items-center justify-center text-text-dim p-10 text-center space-y-4">
              <Loader2 size={48} className="animate-spin text-primary opacity-80" />
              <div>
                <h3 className="text-lg font-medium text-text mb-1">Auditing Documentation...</h3>
                <p className="text-sm">The compliance agent is scanning vector embeddings against {standard}.</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex-1 flex items-center justify-center p-10">
              <div className="bg-critical/10 text-critical border border-critical/20 rounded-xl p-6 max-w-md text-center">
                <AlertTriangle size={32} className="mx-auto mb-3" />
                <h3 className="font-semibold mb-2">Scan Failed</h3>
                <p className="text-sm opacity-90">{error}</p>
              </div>
            </div>
          ) : report && (
            <div className="flex-1 overflow-y-auto">
              {/* Header */}
              <div className="p-6 border-b border-border bg-surface-alt/50 flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold mb-1">{report.standard_name}</h2>
                  <p className="text-sm text-text-muted flex items-center gap-2">
                    <span>Scan Date: {new Date(report.scan_date).toLocaleDateString()}</span>
                  </p>
                </div>
                <div className="text-right">
                  <div className={`text-4xl font-bold font-mono ${scoreColor}`}>
                    {report.overall_score !== undefined ? `${report.overall_score}%` : 'N/A'}
                  </div>
                  <div className="text-[10px] uppercase tracking-wider text-text-dim mt-1 font-semibold">Compliance Score</div>
                </div>
              </div>

              {/* Scanned Documents Info */}
              {report.scanned_files && report.scanned_files.length > 0 && (
                <div className="p-6 border-b border-border bg-primary/5">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-text-dim mb-2">Knowledge Base Scope</h3>
                  <p className="text-sm text-text-muted mb-2">This audit scanned {report.scanned_files.length} document(s) from the facility database:</p>
                  <ul className="text-sm font-mono text-text-dim list-disc pl-5">
                    {report.scanned_files.map((file: string, idx: number) => (
                      <li key={idx}>{file}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Summary */}
              <div className="p-6 border-b border-border">
                <h3 className="text-xs font-bold uppercase tracking-wider text-text-dim mb-3">Executive Summary</h3>
                <p className="text-sm text-text-muted leading-relaxed">{report.summary}</p>
              </div>
              
              {/* Gaps */}
              <div className="p-6">
                <h3 className="text-xs font-bold uppercase tracking-wider text-text-dim mb-4 flex items-center justify-between">
                  <span>Identified Gaps ({report.gaps?.length || 0})</span>
                </h3>
                
                <div className="space-y-4">
                  {report.gaps?.length === 0 ? (
                    <div className="p-6 text-center border border-border rounded-xl bg-operational/5 text-operational flex flex-col items-center gap-2">
                      <CheckCircle size={24} />
                      <span className="font-medium">No gaps found. Full compliance detected!</span>
                    </div>
                  ) : (
                    report.gaps?.map((gap: any, i: number) => (
                      <div key={i} className="border border-border rounded-xl p-4 bg-surface hover:border-primary/30 transition-colors">
                        <div className="flex items-start justify-between mb-3">
                          <h4 className="font-semibold text-text flex-1 pr-4">{gap.finding}</h4>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider shrink-0 ${
                            gap.severity === 'high' ? 'bg-critical/10 text-critical border border-critical/20' :
                            gap.severity === 'medium' ? 'bg-warning/10 text-warning border border-warning/20' :
                            'bg-surface-raised text-text-muted border border-border'
                          }`}>
                            {gap.severity} Priority
                          </span>
                        </div>
                        <div className="bg-surface-raised border border-border/50 rounded p-3 mt-2">
                          <span className="text-[10px] font-semibold uppercase tracking-wider text-primary mb-1 block">Recommendation</span>
                          <p className="text-xs text-text-muted">{gap.recommendation}</p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { ShieldAlert, AlertTriangle, Loader2, FileText, ChevronDown, ChevronRight, CheckCircle2, XCircle, AlertCircle, Download, Play } from 'lucide-react';
import { fetchJson } from '../../api/client';

export function ComplianceDashboard() {
  const [standard, setStandard] = useState("OISD Standard 117");
  const [docType, setDocType] = useState("all");
  const [scanning, setScanning] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploadedStandards, setUploadedStandards] = useState<any[]>([]);

  const [recentScans, setRecentScans] = useState<any[]>([]);
  const [expandedClauses, setExpandedClauses] = useState<Record<number, boolean>>({});

  useEffect(() => {
    try {
      const saved = localStorage.getItem('recent_compliance_scans');
      if (saved) {
        setRecentScans(JSON.parse(saved));
      }
    } catch (e) {
      console.error("Could not load recent scans", e);
    }

    const activeJob = sessionStorage.getItem('active_compliance_job');
    if (activeJob) {
      pollJob(activeJob);
    }
    
    // Fetch dynamic standards
    fetchJson('/documents?category=standard')
      .then(data => setUploadedStandards(data))
      .catch(e => console.error("Failed to load standards", e));
  }, []);

  const pollJob = async (jobId: string) => {
    setScanning(true);
    setError(null);
    setReport(null);
    setExpandedClauses({});

    try {
      const resp = await fetch(`http://localhost:8000/api/jobs/${jobId}/stream`);
      if (!resp.ok) throw new Error("Stream failed");
      
      const reader = resp.body!.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const lines = decoder.decode(value).split("\n");
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payloadStr = line.slice(6).trim();
          if (!payloadStr) continue;
          
          try {
            const payload = JSON.parse(payloadStr);
            if (payload.type === 'done') {
              const data = payload.result;
              setReport(data);
              
              const newScan = {
                standard_name: data.standard_name || standard,
                date: new Date().toISOString(),
                score: data.overall_score
              };
              
              setRecentScans(prev => {
                const updated = [newScan, ...prev].slice(0, 5);
                localStorage.setItem('recent_compliance_scans', JSON.stringify(updated));
                return updated;
              });
            } else if (payload.type === 'error') {
              setError(payload.error || "Scan failed");
            }
          } catch (e) {
            console.error("Error parsing compliance stream", e);
          }
        }
      }
    } catch (e: any) {
      setError(e.message || "Connection lost");
    } finally {
      setScanning(false);
      sessionStorage.removeItem('active_compliance_job');
    }
  };

  const runScan = async () => {
    setScanning(true);
    setError(null);
    setReport(null);
    setExpandedClauses({});
    
    try {
      const data = await fetchJson('/compliance/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ standard_name: standard, doc_type: docType })
      });
      
      if (data.job_id) {
        sessionStorage.setItem('active_compliance_job', data.job_id);
        pollJob(data.job_id);
      }
    } catch (err: any) {
      setError(err.message || "Failed to start scan");
      setScanning(false);
    }
  };

  const handleExport = () => {
    if (!report) return;
    
    if (report.report_id) {
      window.open(`http://localhost:8000/api/compliance/report/${report.report_id}/pdf`, '_blank');
    }
  };

  const toggleClause = (idx: number) => {
    setExpandedClauses(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return '#10b981'; // green (operational)
    if (score >= 60) return '#f59e0b'; // amber (warning)
    return '#ef4444'; // red (critical)
  };

  const getScoreColorClass = (score: number) => {
    if (score >= 85) return 'text-status-success';
    if (score >= 60) return 'text-amber-500';
    return 'text-status-error';
  };

  const getStatusIcon = (status: string) => {
    const s = status?.toLowerCase();
    if (s === 'compliant' || s === 'not-applicable') return <CheckCircle2 size={16} className="text-status-success" />;
    if (s === 'partial') return <AlertCircle size={16} className="text-amber-500" />;
    return <XCircle size={16} className="text-status-error" />;
  };

  const scoreColorStr = report?.overall_score !== undefined ? getScoreColor(report.overall_score) : '#94a3b8';

  return (
    <div className="max-w-[1400px] mx-auto h-full flex flex-col p-[28px] md:p-[32px]">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold mb-1 text-text">Compliance Gap Scanner</h1>
          <p className="text-text-muted text-[13px]">
            Audit the facility's knowledge base against regulatory frameworks clause-by-clause.
          </p>
        </div>
        
        {report && (
          <button 
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-border rounded text-[13px] font-medium hover:bg-slate-50 transition-colors shadow-sm"
          >
            <Download size={16} />
            Export PDF Report
          </button>
        )}
      </div>

      <div className="r-grid-3 flex-1 min-h-0">
        {/* Left Side: Setup */}
        <div className="dash-stack col-span-1">
          <div className="card p-5">
            <h3 className="font-semibold flex items-center gap-2 mb-4 text-[13px]">
              <ShieldAlert size={16} className="text-primary" />
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
                <optgroup label="Default Standards">
                  <option value="OISD Standard 117">OISD Standard 117 (Pressure Vessels)</option>
                  <option value="Factory Act 1948">Factory Act 1948 (Hazardous Processes)</option>
                </optgroup>
                {uploadedStandards.length > 0 && (
                  <optgroup label="Uploaded Standards">
                    {uploadedStandards.map(std => (
                      <option key={std.doc_id} value={std.doc_id}>{std.filename}</option>
                    ))}
                  </optgroup>
                )}
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
                <option value="all">Auto-detect Applicable Documents</option>
                <option value="manual">Manuals Only</option>
                <option value="procedure">Procedures / SOPs Only</option>
                <option value="report">Inspection Reports Only</option>
              </select>
            </div>
            
            <button 
              onClick={runScan}
              disabled={scanning}
              className="w-full py-2.5 bg-primary text-white rounded font-medium text-[13px] flex items-center justify-center gap-2 hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
            >
              {scanning ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
              {scanning ? "Scanning KB..." : "Run Clause-by-Clause Scan"}
            </button>
          </div>
          
          <div className="card p-5 flex-1 overflow-y-auto">
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
                       <span className={`text-xs font-bold font-mono ${getScoreColorClass(scan.score)}`}>
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
        <div className="card col-span-1 md:col-span-2 overflow-hidden flex flex-col relative">
          {!report && !scanning && !error ? (
            <div className="flex-1 flex flex-col items-center justify-center text-text-dim p-10 text-center">
              <ShieldAlert size={48} className="mb-4 opacity-20" />
              <h3 className="text-lg font-medium text-text mb-2">No Active Report</h3>
              <p className="text-sm max-w-sm">Select a standard on the left and run a scan to perform a clause-by-clause audit of your document base.</p>
            </div>
          ) : scanning ? (
             <div className="flex-1 flex flex-col items-center justify-center text-text-dim p-10 text-center space-y-4">
              <Loader2 size={48} className="animate-spin text-primary opacity-80" />
              <div>
                <h3 className="text-lg font-medium text-text mb-1">Auditing Documentation...</h3>
                <p className="text-sm">Retrieving evidence and evaluating {standard} clause-by-clause.</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex-1 flex items-center justify-center p-10">
              <div className="bg-status-error/10 text-status-error border-status-error/20 rounded-xl p-6 max-w-md text-center">
                <AlertTriangle size={32} className="mx-auto mb-3" />
                <h3 className="font-semibold mb-2">Scan Failed</h3>
                <p className="text-sm opacity-90">{error}</p>
              </div>
            </div>
          ) : report && (
            <div className="flex-1 overflow-y-auto flex flex-col animate-fade-in">
              {/* Header & Radial Dial */}
              <div className="p-6 border-b border-border bg-white flex items-center justify-between">
                <div className="flex-1 pr-6">
                  <h2 className="text-xl font-bold mb-1">{report.standard_name}</h2>
                  <p className="text-[13px] text-text-muted leading-relaxed mb-4">{report.summary}</p>
                  
                  <div className="flex gap-4">
                    <div className="bg-surface-alt px-3 py-1.5 rounded-lg border border-border">
                      <span className="text-[10px] uppercase text-text-dim font-bold block mb-0.5">Scanned</span>
                      <span className="text-sm font-medium">{report.scanned_files?.length || 0} Documents</span>
                    </div>
                    <div className="bg-surface-alt px-3 py-1.5 rounded-lg border border-border">
                      <span className="text-[10px] uppercase text-text-dim font-bold block mb-0.5">Date</span>
                      <span className="text-sm font-medium">{new Date(report.scan_date).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
                
                {/* Radial Dial */}
                <div className="relative w-32 h-32 flex-shrink-0 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    {/* Background Ring */}
                    <circle cx="50" cy="50" r="40" fill="transparent" stroke="currentColor" strokeWidth="8" className="text-border" />
                    {/* Progress Ring */}
                    <circle 
                      cx="50" cy="50" r="40" 
                      fill="transparent" 
                      stroke={scoreColorStr} 
                      strokeWidth="8" 
                      strokeDasharray={`${(report.overall_score / 100) * 251.2} 251.2`}
                      strokeLinecap="round"
                      className="transition-all duration-1000 ease-out"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-3xl font-bold font-mono ${getScoreColorClass(report.overall_score)}`}>{report.overall_score}%</span>
                  </div>
                </div>
              </div>
              
              {/* Detailed Findings - Clauses */}
              <div className="p-6 bg-surface flex-1">
                <h3 className="text-xs font-bold uppercase tracking-wider text-text-dim mb-4">Clause-by-Clause Findings</h3>
                
                <div className="space-y-3">
                  {(!report.gaps || report.gaps.length === 0) ? (
                     <div className="text-sm text-text-dim italic text-center p-6 bg-surface border border-border rounded-lg">No clauses found in report.</div>
                  ) : (
                    report.gaps.map((clause: any, i: number) => {
                      const isExpanded = !!expandedClauses[i];
                      const statusLower = clause.status?.toLowerCase();
                      
                      const badgeClass = statusLower === 'compliant' || statusLower === 'not-applicable' 
                        ? 'bg-status-success/10 text-status-success border-status-success/20' 
                        : statusLower === 'partial' 
                        ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' 
                        : 'bg-status-error/10 text-status-error border-status-error/20';

                      return (
                        <div key={i} className="border border-border rounded-xl bg-surface overflow-hidden transition-all shadow-sm hover:shadow-md">
                          {/* Card Header (Always Visible) */}
                          <div 
                            className="p-4 flex items-center cursor-pointer hover:bg-surface-raised/30 transition-colors"
                            onClick={() => toggleClause(i)}
                          >
                            <div className="mr-3 text-text-muted">
                              {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                            </div>
                            <div className="flex-1 min-w-0 pr-4">
                              <div className="flex items-center gap-3 mb-1">
                                <h4 className="font-semibold text-sm truncate">{clause.clause_number}</h4>
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border flex items-center gap-1 ${badgeClass}`}>
                                  {getStatusIcon(clause.status)}
                                  {clause.status}
                                </span>
                              </div>
                              <p className="text-xs text-text-dim truncate">{clause.clause_text_summary}</p>
                            </div>
                          </div>
                          
                          {/* Expanded Content */}
                          {isExpanded && (
                            <div className="p-4 pt-0 border-t border-border/50 bg-surface-raised/10">
                              <div className="mt-4 grid grid-cols-1 gap-4">
                                <div>
                                  <h5 className="text-[10px] font-bold uppercase tracking-wider text-text-dim mb-2">Finding Summary</h5>
                                  <p className="text-sm text-text leading-relaxed bg-surface p-3 rounded border border-border">{clause.finding_title || clause.ui_summary || clause.gap_description}</p>
                                </div>
                                
                                {clause.evidence && clause.evidence.length > 0 && (
                                  <div>
                                    <h5 className="text-[10px] font-bold uppercase tracking-wider text-text-dim mb-2">Cited Evidence</h5>
                                    <div className="space-y-2">
                                      {clause.evidence.map((ev: any, j: number) => (
                                        <div key={j} className="bg-surface p-3 rounded border border-border flex flex-col gap-1">
                                          <div className="flex items-center gap-2 text-xs font-mono text-primary">
                                            <FileText size={12} /> {ev.document}
                                          </div>
                                          <p className="text-xs text-text-muted italic">"{ev.exact_quote || ev.excerpt_summary}"</p>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                
                                {(statusLower === 'gap' || statusLower === 'partial') && (clause.remediation_action || clause.remediation_summary || clause.remediation) && clause.remediation !== 'N/A' && (
                                  <div>
                                    <h5 className="text-[10px] font-bold uppercase tracking-wider text-text-dim mb-2">Required Action</h5>
                                    <div className="bg-amber-500/10 text-amber-600 p-3 rounded border border-amber-500/20 text-sm flex items-start gap-2">
                                      <AlertTriangle size={16} className="shrink-0 mt-0.5" />
                                      <p>{clause.remediation_action || clause.remediation_summary || clause.remediation}</p>
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })
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

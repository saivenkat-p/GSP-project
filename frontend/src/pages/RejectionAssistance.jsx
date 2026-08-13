import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import { AlertOctagon, CheckCircle2, FileText, ArrowLeft, RefreshCw, Scale, ExternalLink, ShieldCheck } from 'lucide-react';

export const RejectionAssistance = () => {
  const { id } = useParams();
  const [rejection, setRejection] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRejectionDiagnostic();
  }, [id]);

  const fetchRejectionDiagnostic = async () => {
    try {
      setLoading(true);
      const res = await apiService.getRejectionDiagnostic(id);
      setRejection(res.data);
    } catch (err) {
      console.error('Error fetching rejection diagnostic:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="max-w-4xl mx-auto py-12 animate-pulse h-96 bg-slate-900 rounded-3xl border border-slate-800" />;
  }

  if (!rejection) {
    return (
      <div className="max-w-md mx-auto py-12 text-center space-y-4">
        <p className="text-slate-400">Rejection diagnostic report not found.</p>
        <Link to="/dashboard" className="text-saffron-400 text-xs font-semibold hover:underline">Return to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-20">
      <Link to="/dashboard" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to My Dashboard</span>
      </Link>

      {/* Header Alert Card */}
      <div className="glass-panel p-8 rounded-3xl border border-red-500/30 bg-red-950/20 space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/20 border border-red-500/30 text-red-400 text-xs font-semibold">
          <AlertOctagon className="w-4 h-4" />
          <span>Application Rejection Diagnostic & Remedy</span>
        </div>

        <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">
          Understanding Your Application Rejection
        </h1>

        <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs space-y-1">
          <span className="text-slate-500 font-bold uppercase text-[10px]">Official Rejection Reason</span>
          <p className="text-red-300 font-mono leading-relaxed">{rejection.rejection_reason}</p>
        </div>
      </div>

      {/* 4 CORE CITIZEN DIAGNOSTIC QUESTIONS */}
      <div className="space-y-6">
        {/* 1. WHY WAS IT REJECTED? */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2">
          <h3 className="text-sm font-bold text-saffron-400 uppercase tracking-wide flex items-center gap-2">
            <span>1. Simple Explanation ("Why?")</span>
          </h3>
          <p className="text-sm text-slate-200 leading-relaxed font-sans">{rejection.simple_explanation}</p>
        </div>

        {/* 2. WHAT WENT WRONG? */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2">
          <h3 className="text-sm font-bold text-saffron-400 uppercase tracking-wide">
            2. Root Cause Breakdown ("What went wrong?")
          </h3>
          <div className="text-xs text-slate-300 whitespace-pre-line leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800">
            {rejection.what_went_wrong}
          </div>
        </div>

        {/* 3. RECOMMENDED CORRECTIVE ACTION CHECKLIST */}
        <div className="glass-panel p-6 rounded-2xl border border-emerald-500/30 bg-emerald-950/10 space-y-4">
          <h3 className="text-sm font-bold text-emerald-400 uppercase tracking-wide flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>3. Recommended Action Checklist ("What can you correct?")</span>
          </h3>
          <div className="space-y-2.5">
            {rejection.corrective_actions.map((act, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 flex items-start gap-2.5">
                <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-[11px] flex items-center justify-center shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <span className="leading-relaxed">{act}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 4. REQUIRED REPLACEMENT DOCUMENTS */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide flex items-center gap-2">
            <FileText className="w-4 h-4 text-saffron-400" />
            <span>Required Replacement Documents</span>
          </h3>
          <div className="space-y-2">
            {rejection.required_replacement_documents.map((doc, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 flex items-center justify-between">
                <span>{doc}</span>
                <span className="text-[10px] uppercase font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                  Required Replacement
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* VERIFIED STATUTORY CLAUSE & RE-APPLICATION LINK */}
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="text-xs text-slate-300 leading-relaxed p-3 rounded-xl bg-slate-950 border border-slate-800 font-sans">
            <strong className="text-emerald-400 block mb-1">Official Statutory Rule:</strong>
            {rejection.verified_info}
          </div>

          {rejection.needs_legal_help && (
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-3">
              <Scale className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-sm block">Legal Advisory Recommendation</span>
                <p className="mt-0.5">
                  This case involves complex land title dispute or court injunctions. We recommend consulting a qualified legal practitioner enrolled with the Bar Council of Andhra Pradesh.
                </p>
              </div>
            </div>
          )}

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
            <Link
              to="/assistance"
              className="w-full sm:w-auto px-6 py-3 rounded-xl bg-sky-500 hover:bg-sky-600 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg transition-colors"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Get Verified Partner Assistance for Re-application</span>
            </Link>

            {rejection.official_reapplication_url && (
              <a
                href={rejection.official_reapplication_url}
                target="_blank"
                rel="noreferrer"
                className="w-full sm:w-auto px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 shadow-lg transition-colors"
              >
                <span>Re-apply Directly on Official Portal</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

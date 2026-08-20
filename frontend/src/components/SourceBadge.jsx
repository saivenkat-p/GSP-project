import React from 'react';
import { ExternalLink, ShieldCheck, Clock, AlertTriangle } from 'lucide-react';

export const SourceBadge = ({ status = 'VERIFIED', lastVerified, sourceUrl, version = 'V1.0' }) => {
  // CRITICAL UI TRUST FIX (Section 16): Do NOT render badge if status is NOT_FOUND or empty
  if (!status || status === 'NOT_FOUND') {
    return null;
  }

  let badgeStyle = 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400';
  let statusText = `VERIFIED (${version})`;
  let Icon = ShieldCheck;

  if (status === 'VERIFICATION_PENDING') {
    badgeStyle = 'bg-amber-500/10 border-amber-500/30 text-amber-400';
    statusText = `VERIFICATION PENDING (${version})`;
    Icon = Clock;
  } else if (status === 'OUTDATED') {
    badgeStyle = 'bg-red-500/10 border-red-500/30 text-red-400';
    statusText = `OUTDATED (${version})`;
    Icon = AlertTriangle;
  }

  return (
    <div className="flex flex-wrap items-center gap-2 text-xs">
      <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-semibold border ${badgeStyle}`}>
        <Icon className="w-3.5 h-3.5" />
        <span>Official Source — {statusText}</span>
        {lastVerified && (
          <span className="opacity-70 border-l border-current/20 pl-1.5 ml-0.5">
            Verified: {lastVerified}
          </span>
        )}
      </div>

      {sourceUrl && (
        <a
          href={sourceUrl}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 text-[11px] text-slate-400 hover:text-saffron-400 transition-colors bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800"
        >
          <span>View Official Source</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      )}
    </div>
  );
};

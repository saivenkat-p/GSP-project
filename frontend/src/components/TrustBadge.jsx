import React from 'react';
import { ShieldCheck, Landmark, Bot, AlertTriangle } from 'lucide-react';

export const TrustBadge = ({ type, lastVerified, isDemo = false }) => {
  if (type === 'official') {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
        <Landmark className="w-3.5 h-3.5" />
        <span>Official Government Source</span>
        {lastVerified && (
          <span className="text-emerald-300/70 border-l border-emerald-500/20 pl-1.5 ml-0.5">
            Verified: {lastVerified}
          </span>
        )}
        {isDemo && (
          <span className="bg-amber-500/20 text-amber-300 text-[10px] px-1.5 py-0.5 rounded ml-1 uppercase font-bold">
            DEMO DATA
          </span>
        )}
      </div>
    );
  }

  if (type === 'partner') {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sky-500/10 border border-sky-500/30 text-sky-400">
        <ShieldCheck className="w-3.5 h-3.5" />
        <span>Verified Partner Center 🛡️</span>
      </div>
    );
  }

  if (type === 'ai') {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-saffron-500/10 border border-saffron-500/30 text-saffron-400">
        <Bot className="w-3.5 h-3.5" />
        <span>Grounded AI Guidance</span>
      </div>
    );
  }

  return null;
};

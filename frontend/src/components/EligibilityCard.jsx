import React from 'react';
import { CheckCircle2, UserCheck } from 'lucide-react';

export const EligibilityCard = ({ criteria = [] }) => {
  return (
    <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-800 space-y-3">
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
        <UserCheck className="w-5 h-5 text-emerald-400" />
        <h3 className="text-base font-bold text-slate-100 font-heading">Eligibility Requirements Matrix</h3>
      </div>
      <div className="space-y-2.5">
        {criteria.map((item, idx) => (
          <div key={idx} className="flex items-start gap-2.5 p-2.5 rounded-lg bg-slate-950/50 border border-slate-800/80">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
            <span className="text-xs text-slate-300 leading-relaxed">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

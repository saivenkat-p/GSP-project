import React from 'react';
import { UserCheck, AlertTriangle, CheckCircle, MapPin } from 'lucide-react';

export const PhysicalPresenceCard = ({ requirement = 'MAY_BE_REQUIRED', reason = null }) => {
  let badgeStyle = 'bg-amber-500/10 border-amber-500/30 text-amber-400';
  let title = '🟡 Physical Presence May Be Required';
  let defaultReason = 'Counter visit, original document verification, signature, or VRO field inspection may be required by official government authorities.';
  let Icon = AlertTriangle;

  if (requirement === 'NOT_REQUIRED') {
    badgeStyle = 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400';
    title = '🟢 No Physical Presence Required (100% Online)';
    defaultReason = 'Application and document submission can be completed 100% online through official government portals without visiting an office.';
    Icon = CheckCircle;
  } else if (requirement === 'REQUIRED') {
    badgeStyle = 'bg-red-500/10 border-red-500/30 text-red-400';
    title = '🔴 Mandatory Personal Presence Required';
    defaultReason = 'Biometric fingerprint authentication, personal appearance, signature, or original document verification is mandatory by law.';
    Icon = UserCheck;
  }

  return (
    <div className={`p-4 rounded-2xl border ${badgeStyle} space-y-2 text-xs`}>
      <div className="flex items-center gap-2 font-bold text-sm">
        <Icon className="w-4 h-4" />
        <span>{title}</span>
      </div>
      <p className="text-slate-300 leading-relaxed font-sans">
        {reason || defaultReason}
      </p>
      {requirement !== 'NOT_REQUIRED' && (
        <div className="pt-1 text-[11px] opacity-80 flex items-center gap-1 font-medium">
          <MapPin className="w-3.5 h-3.5" />
          <span>GSP team will guide you on exact office location, working hours, and what original documents to carry.</span>
        </div>
      )}
    </div>
  );
};

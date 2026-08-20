import React from 'react';
import { User, FileText, Compass, ShieldCheck, Check, AlertCircle, Info } from 'lucide-react';

export const AssistanceTierSelector = ({
  selectedTier = 'LEVEL_B_FORM_HELP',
  onSelectTier,
  officialFee = 50,
  physicalPresence = 'MAY_BE_REQUIRED'
}) => {
  const tiers = [
    {
      id: 'LEVEL_A_DIY',
      code: '🟢 A',
      title: 'DIY / Free Information',
      subtitle: 'Free Step-by-Step Guide & Portal Link',
      gspFee: 0,
      icon: User,
      explanation: 'You complete the application yourself. GSP provides verified instructions, documents checklist, and official portal link.',
      whatGspDoes: 'Provides verified statutory information, step-by-step procedure, required document list, and direct official government website link.',
      whatCitizenDoes: 'Scans documents, fills form online or at counter, pays official government fee directly, and tracks status.'
    },
    {
      id: 'LEVEL_B_FORM_HELP',
      code: '🔵 B',
      title: 'Form & Document Assistance',
      subtitle: 'Form Filling & Document Preparation',
      gspFee: 150,
      icon: FileText,
      explanation: 'A GSP team member or verified partner helps you understand the form, fill details accurately, and prepare required documents.',
      whatGspDoes: 'Reviews document scans for common rejection mistakes, assists with form filling, and drafts required notarized affidavits.',
      whatCitizenDoes: 'Provides clear document scans/copies, verifies filled details, and submits application on official portal or at local center.'
    },
    {
      id: 'LEVEL_C_PROCESS_HELP',
      code: '🟣 C',
      title: 'Process Assistance',
      subtitle: 'Office Navigation & Submission Guidance',
      gspFee: 300,
      icon: Compass,
      explanation: 'GSP guides you through the complete application process, including exact government office location, counter visits, and tracking.',
      whatGspDoes: 'Provides personalized guidance on office hours, officer interaction, submission procedure, fee payment receipt, and active tracking.',
      whatCitizenDoes: 'Attends mandatory counter visits (if required), presents original documents for verification, and signs official register.'
    },
    {
      id: 'LEVEL_D_FULL_HELP',
      code: '🟠 D',
      title: 'Full Permitted Assistance',
      subtitle: 'End-to-End Permitted Coordination',
      gspFee: 500,
      icon: ShieldCheck,
      explanation: 'A verified GSP partner assists with the maximum legally permitted parts of the process. Mandatory personal appearance must still be done by you.',
      whatGspDoes: 'Coordinates document collection, form submission, partner assignment, and continuous follow-up until certificate completion.',
      whatCitizenDoes: 'Appears personally for biometric capture, original document inspection, or signature whenever mandated by government rules.'
    }
  ];

  return (
    <div className="space-y-4">
      <div className="border-b border-slate-800 pb-2">
        <h3 className="text-base font-bold text-white font-heading">How can we help you?</h3>
        <p className="text-xs text-slate-400">Select your preferred level of assistance below.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {tiers.map((t) => {
          const isSelected = selectedTier === t.id;
          const Icon = t.icon;
          const totalFee = officialFee + t.gspFee;

          return (
            <div
              key={t.id}
              onClick={() => onSelectTier(t.id)}
              className={`p-5 rounded-2xl border cursor-pointer transition-all space-y-3 relative ${
                isSelected
                  ? 'bg-saffron-500/10 border-saffron-500 ring-2 ring-saffron-500/30 text-white shadow-xl'
                  : 'bg-slate-900 border-slate-800 hover:border-slate-700 text-slate-300'
              }`}
            >
              {isSelected && (
                <div className="absolute top-4 right-4 w-6 h-6 rounded-full bg-saffron-500 text-white flex items-center justify-center text-xs shadow-md">
                  <Check className="w-4 h-4" />
                </div>
              )}

              {/* Header */}
              <div className="flex items-center gap-2">
                <Icon className={`w-5 h-5 ${isSelected ? 'text-saffron-400' : 'text-slate-400'}`} />
                <div>
                  <span className="font-extrabold text-sm text-white block">
                    {t.code} — {t.title}
                  </span>
                  <span className="text-[11px] text-slate-400 block">{t.subtitle}</span>
                </div>
              </div>

              {/* Transparent Fee Breakdown */}
              <div className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs flex items-center justify-between">
                <div>
                  <span className="text-slate-400 text-[10px] block font-medium">Fee Breakdown</span>
                  <span className="text-slate-300 font-medium">
                    Govt Fee: <strong className="text-emerald-400">₹{officialFee.toFixed(0)}</strong> + GSP Fee: <strong className="text-saffron-400">₹{t.gspFee}</strong>
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-slate-500 text-[10px] block uppercase font-semibold">Total</span>
                  <span className="text-white font-extrabold text-sm">₹{totalFee.toFixed(0)}</span>
                </div>
              </div>

              {/* Scope & Role Descriptions */}
              <p className="text-xs text-slate-300 leading-relaxed font-sans">{t.explanation}</p>

              <div className="space-y-1.5 text-[11px] pt-1 border-t border-slate-800/80">
                <div className="flex items-start gap-1.5 text-slate-300">
                  <strong className="text-saffron-400 shrink-0">What GSP Does:</strong>
                  <span>{t.whatGspDoes}</span>
                </div>
                <div className="flex items-start gap-1.5 text-slate-300">
                  <strong className="text-sky-400 shrink-0">What You Do:</strong>
                  <span>{t.whatCitizenDoes}</span>
                </div>
              </div>

              {/* Physical Presence Note */}
              {physicalPresence !== 'NOT_REQUIRED' && t.id !== 'LEVEL_A_DIY' && (
                <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-[10px] text-amber-300 flex items-center gap-1.5 font-medium">
                  <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                  <span>Mandatory personal appearance or biometric verification must still be completed by you.</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

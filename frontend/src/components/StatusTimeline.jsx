import React from 'react';
import { CheckCircle2, Clock, FileCheck, Landmark, Award, AlertOctagon } from 'lucide-react';

export const StatusTimeline = ({ currentStatus = 'requirement_identified', officialAppNo = null, notes = null }) => {
  const steps = [
    {
      id: 'requirement_identified',
      label: 'Requirement Identified',
      description: 'Service identified via AI Navigator. Documents checklist ready.',
      icon: CheckCircle2,
    },
    {
      id: 'documents_prepared',
      label: 'Documents Prepared',
      description: 'Checklist completed & scanned documents verified.',
      icon: FileCheck,
    },
    {
      id: 'submitted_to_official_portal',
      label: 'Submitted to Official Portal',
      description: officialAppNo ? `Application submitted (App No: ${officialAppNo})` : 'Submitted to MeeSeva / Grama Sachivalayam portal.',
      icon: Landmark,
    },
    {
      id: 'government_verification',
      label: 'Government Verification',
      description: 'Field inspection by VRO / Revenue Inspector in progress.',
      icon: Clock,
    },
    {
      id: 'certificate_generated',
      label: 'Certificate Generated',
      description: 'Digitally signed official certificate ready for download.',
      icon: Award,
    },
  ];

  const getStepIndex = (status) => {
    if (status === 'rejected') return 3; // Halts at verification step
    const idx = steps.findIndex((s) => s.id === status);
    return idx >= 0 ? idx : 0;
  };

  const activeIdx = getStepIndex(currentStatus);
  const isRejected = currentStatus === 'rejected';

  return (
    <div className="bg-slate-900/90 rounded-2xl p-6 border border-slate-800 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-base font-bold text-slate-100 font-heading">Application Status Timeline</h3>
          <p className="text-xs text-slate-400">Verified progress timeline for official government processing</p>
        </div>
        {officialAppNo && (
          <span className="text-xs font-mono font-semibold bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800 text-saffron-400">
            App #: {officialAppNo}
          </span>
        )}
      </div>

      {isRejected && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 flex items-start gap-3 text-xs">
          <AlertOctagon className="w-5 h-5 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-sm block text-red-300">Application Status: REJECTED</span>
            <p className="text-red-400/90 mt-0.5">{notes || 'Tahsildar office rejected document. Access Rejection Diagnostic for corrective guidance.'}</p>
          </div>
        </div>
      )}

      {/* Vertical / Horizontal Timeline */}
      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
        {steps.map((step, idx) => {
          const isCompleted = idx <= activeIdx && !isRejected;
          const isCurrent = idx === activeIdx && !isRejected;
          const Icon = step.icon;

          let iconBg = 'bg-slate-900 border-slate-800 text-slate-500';
          if (isCompleted) {
            iconBg = 'bg-emerald-500 text-slate-950 border-emerald-400 ring-4 ring-emerald-500/10';
          } else if (isCurrent) {
            iconBg = 'bg-saffron-500 text-white border-saffron-400 animate-pulse ring-4 ring-saffron-500/20';
          } else if (isRejected && idx === activeIdx) {
            iconBg = 'bg-red-500 text-white border-red-400';
          }

          return (
            <div key={step.id} className="relative flex items-start gap-4">
              <div className={`absolute -left-6 top-0.5 w-5 h-5 rounded-full border-2 flex items-center justify-center text-[10px] ${iconBg}`}>
                {isCompleted ? '✓' : idx + 1}
              </div>
              <div>
                <span className={`text-xs font-semibold ${isCompleted ? 'text-emerald-400' : isCurrent ? 'text-saffron-400' : 'text-slate-400'}`}>
                  {step.label}
                </span>
                <p className="text-[11px] text-slate-400 mt-0.5">{step.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

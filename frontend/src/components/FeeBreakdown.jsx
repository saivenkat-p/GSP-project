import React from 'react';
import { Landmark, ShieldCheck, IndianRupee, Info } from 'lucide-react';

export const FeeBreakdown = ({ officialFee = 50, partnerFee = 0, showPartner = false }) => {
  const official = parseFloat(officialFee) || 0;
  const partner = showPartner ? (parseFloat(partnerFee) || 0) : 0;
  const total = official + partner;

  return (
    <div className="bg-slate-900/90 rounded-xl p-5 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <IndianRupee className="w-4 h-4 text-saffron-500" />
          Transparent Fee Breakdown
        </h4>
        <span className="text-xs text-slate-400 flex items-center gap-1">
          <Info className="w-3.5 h-3.5 text-slate-500" />
          Mandatory Price Transparency
        </span>
      </div>

      <div className="space-y-2.5 text-sm">
        {/* Official Statutory Fee */}
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
          <div className="flex items-center gap-2">
            <Landmark className="w-4 h-4 text-emerald-400" />
            <div>
              <span className="font-medium text-slate-200">Official Government Fee</span>
              <p className="text-[11px] text-slate-400">Statutory portal / Treasury receipt fee</p>
            </div>
          </div>
          <span className="font-bold text-emerald-400">₹{official.toFixed(0)}</span>
        </div>

        {/* Partner Assistance Fee (Only if partner assistance chosen) */}
        {showPartner && (
          <div className="flex items-center justify-between p-2.5 rounded-lg bg-sky-500/5 border border-sky-500/20">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-sky-400" />
              <div>
                <span className="font-medium text-slate-200">Verified Partner Service Fee</span>
                <p className="text-[11px] text-slate-400">Form filing, document scan & facilitation</p>
              </div>
            </div>
            <span className="font-bold text-sky-400">₹{partner.toFixed(0)}</span>
          </div>
        )}

        {/* Total Cost */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-800 font-semibold text-base">
          <span className="text-slate-100">Total Payable Amount</span>
          <span className="text-saffron-400 text-lg font-bold">₹{total.toFixed(0)}</span>
        </div>
      </div>
    </div>
  );
};

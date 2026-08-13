import React from 'react';
import { Link } from 'react-router-dom';
import { Landmark, Clock, IndianRupee, ArrowRight, ShieldCheck } from 'lucide-react';
import { TrustBadge } from './TrustBadge';

export const ServiceCard = ({ service }) => {
  return (
    <div className="glass-card rounded-2xl p-6 flex flex-col justify-between space-y-4 group">
      <div>
        {/* Header badges */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-saffron-400 bg-saffron-500/10 px-2.5 py-1 rounded-md border border-saffron-500/20">
            {service.category}
          </span>
          <TrustBadge type="official" lastVerified={service.source_last_verified} isDemo={service.is_demo_data} />
        </div>

        {/* Title */}
        <h3 className="text-lg font-bold text-slate-100 group-hover:text-saffron-400 transition-colors font-heading leading-snug">
          {service.official_name}
        </h3>

        {/* Department & State */}
        <p className="text-xs text-slate-400 mt-1.5 flex items-center gap-1.5">
          <Landmark className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <span>{service.department}</span>
        </p>

        {/* Description snippet */}
        <p className="text-xs text-slate-300 mt-3 line-clamp-2 leading-relaxed">
          {service.description}
        </p>
      </div>

      {/* Key Details */}
      <div className="pt-4 border-t border-slate-800/80 space-y-3">
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800 flex items-center gap-2">
            <Clock className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <div>
              <span className="text-[10px] text-slate-500 block">Processing</span>
              <span className="font-semibold text-slate-200">{service.processing_time}</span>
            </div>
          </div>

          <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800 flex items-center gap-2">
            <IndianRupee className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <div>
              <span className="text-[10px] text-slate-500 block">Official Fee</span>
              <span className="font-semibold text-emerald-400">₹{service.official_fee}</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <Link
          to={`/services/${service.id}`}
          className="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-saffron-600 text-slate-200 hover:text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all border border-slate-800 hover:border-saffron-500/50 shadow-sm"
        >
          <span>View Verified Requirements</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
};

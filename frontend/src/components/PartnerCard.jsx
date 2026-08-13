import React from 'react';
import { ShieldCheck, MapPin, Phone, Star, ArrowRight } from 'lucide-react';
import { TrustBadge } from './TrustBadge';

export const PartnerCard = ({ partner, onSelect }) => {
  return (
    <div className="glass-card rounded-2xl p-6 flex flex-col justify-between space-y-4">
      <div>
        <div className="flex items-center justify-between gap-2 mb-2">
          <TrustBadge type="partner" />
          <span className="text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
            📍 {partner.distance_km} km away
          </span>
        </div>

        <h3 className="text-lg font-bold text-slate-100 font-heading">{partner.business_name}</h3>
        <p className="text-xs text-slate-400 mt-0.5">{partner.center_type}</p>

        <div className="flex items-center gap-3 mt-3 text-xs text-slate-300">
          <div className="flex items-center gap-1 text-amber-400 font-semibold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
            <Star className="w-3.5 h-3.5 fill-amber-400" />
            <span>{partner.rating}</span>
            <span className="text-[10px] text-amber-300/70">({partner.reviews_count} reviews)</span>
          </div>

          <div className="flex items-center gap-1 text-slate-400">
            <MapPin className="w-3.5 h-3.5 text-saffron-400" />
            <span className="truncate max-w-[180px]">{partner.district}</span>
          </div>
        </div>

        <p className="text-xs text-slate-400 mt-2 line-clamp-2">{partner.address}</p>
      </div>

      <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-2">
        <div>
          <span className="text-[10px] text-slate-500 block uppercase font-semibold">Assistance Fee</span>
          <span className="text-sm font-bold text-sky-400">₹{partner.partner_assistance_fee}</span>
        </div>

        <button
          onClick={() => onSelect && onSelect(partner)}
          className="px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-600 text-white font-semibold text-xs flex items-center gap-1.5 transition-colors shadow-md shadow-sky-500/20"
        >
          <span>Request Assistance</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

import React from 'react';
import { Compass, Landmark, ShieldCheck, ExternalLink, Heart } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-slate-950 border-t border-slate-800 text-slate-400 text-xs py-10 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Main Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand & Mandate */}
          <div className="space-y-3 md:col-span-2">
            <div className="flex items-center gap-2 text-white font-bold text-base font-heading">
              <div className="w-7 h-7 rounded-lg bg-saffron-500 flex items-center justify-center text-white">
                <Compass className="w-4 h-4" />
              </div>
              <span>Government Services Navigator</span>
            </div>
            <p className="text-slate-400 leading-relaxed max-w-md">
              An intelligent navigation, discovery, eligibility evaluation, and verified assistance layer. 
              Helping citizens understand: <em className="text-saffron-400">"I need to get this done. What exactly should I do?"</em>
            </p>

            {/* Non-negotiable product rule disclaimer box */}
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-300 space-y-1">
              <div className="flex items-center gap-1.5 text-amber-400 font-semibold uppercase">
                <Landmark className="w-3.5 h-3.5" />
                <span>Non-Negotiable Platform Boundary</span>
              </div>
              <p className="text-slate-400">
                This platform does NOT replace government departments or official government portals. 
                All official applications remain executed directly on official government authority websites (AP MeeSeva, Meebhoomi, IGRS AP, Parivahan).
              </p>
            </div>
          </div>

          {/* Official AP Government Portals */}
          <div className="space-y-3">
            <h4 className="text-slate-200 font-bold uppercase tracking-wider text-[11px] font-heading">Official AP Government Portals</h4>
            <ul className="space-y-2 text-slate-400">
              <li>
                <a href="https://ap.meeseva.gov.in" target="_blank" rel="noreferrer" className="hover:text-saffron-400 transition-colors flex items-center gap-1">
                  <span>AP MeeSeva Portal</span>
                  <ExternalLink className="w-3 h-3 text-slate-600" />
                </a>
              </li>
              <li>
                <a href="http://meebhoomi.ap.gov.in" target="_blank" rel="noreferrer" className="hover:text-saffron-400 transition-colors flex items-center gap-1">
                  <span>Meebhoomi AP Land Records</span>
                  <ExternalLink className="w-3 h-3 text-slate-600" />
                </a>
              </li>
              <li>
                <a href="https://registration.ap.gov.in" target="_blank" rel="noreferrer" className="hover:text-saffron-400 transition-colors flex items-center gap-1">
                  <span>IGRS AP Encumbrance Portal</span>
                  <ExternalLink className="w-3 h-3 text-slate-600" />
                </a>
              </li>
              <li>
                <a href="https://sarathi.parivahan.gov.in" target="_blank" rel="noreferrer" className="hover:text-saffron-400 transition-colors flex items-center gap-1">
                  <span>Parivahan Transport Portal</span>
                  <ExternalLink className="w-3 h-3 text-slate-600" />
                </a>
              </li>
            </ul>
          </div>

          {/* Verification & Trust Standards */}
          <div className="space-y-3">
            <h4 className="text-slate-200 font-bold uppercase tracking-wider text-[11px] font-heading">Trust & Verification</h4>
            <ul className="space-y-2 text-slate-400">
              <li className="flex items-center gap-1.5 text-emerald-400">
                <ShieldCheck className="w-4 h-4" />
                <span>Verified Source Metadata</span>
              </li>
              <li>Official Fee vs Partner Fee Separation</li>
              <li>Grounded RAG (No AI Hallucinations)</li>
              <li>Andhra Pradesh & National Scope</li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-6 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-500">
          <p>© 2026 Government Services Navigator. Built for Indian Citizen Empowerment.</p>
          <div className="flex items-center gap-4">
            <span className="text-slate-400">Official Source Audit: <strong className="text-slate-300">2026-08-10</strong></span>
            <span>•</span>
            <span>Version 1.0.0</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

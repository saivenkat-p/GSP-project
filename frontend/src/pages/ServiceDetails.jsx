import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { TrustBadge } from '../components/TrustBadge';
import { DocumentChecklist } from '../components/DocumentChecklist';
import { EligibilityCard } from '../components/EligibilityCard';
import { FeeBreakdown } from '../components/FeeBreakdown';
import { PartnerCard } from '../components/PartnerCard';
import { Landmark, ExternalLink, ShieldCheck, CheckCircle2, AlertTriangle, ArrowRight, User, Sparkles } from 'lucide-react';

export const ServiceDetails = () => {
  const { id } = useParams();
  const [service, setService] = useState(null);
  const [partners, setPartners] = useState([]);
  const [activeTab, setActiveTab] = useState('diy'); // 'diy' | 'assistance'
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    fetchServiceData();
  }, [id]);

  const fetchServiceData = async () => {
    try {
      setLoading(true);
      const [srvRes, prtRes] = await Promise.all([
        apiService.getServiceById(id),
        apiService.getPartners('NTR / Vijayawada', id),
      ]);
      setService(srvRes.data);
      setPartners(prtRes.data);
    } catch (err) {
      console.error('Error loading service details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRequest = async (partnerId = null) => {
    try {
      const res = await apiService.createRequest(service.id, partnerId, 'Request initiated from Service Details page.');
      navigate(`/dashboard`);
    } catch (err) {
      console.error('Error creating request:', err);
      // If unauthorized, redirect to login
      navigate('/login');
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto py-12 animate-pulse space-y-6">
        <div className="h-48 bg-slate-900 rounded-3xl border border-slate-800" />
        <div className="h-64 bg-slate-900 rounded-3xl border border-slate-800" />
      </div>
    );
  }

  if (!service) {
    return (
      <div className="max-w-md mx-auto py-12 text-center space-y-4">
        <p className="text-slate-400">Service not found.</p>
        <Link to="/" className="text-saffron-400 font-semibold hover:underline text-sm">Return Home</Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-20">
      {/* Top Breadcrumb & Metadata Card */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span className="text-xs font-bold uppercase tracking-wider text-saffron-400 bg-saffron-500/10 px-3 py-1 rounded-full border border-saffron-500/20">
            {service.category}
          </span>
          <TrustBadge type="official" lastVerified={service.source_last_verified} isDemo={service.is_demo_data} />
        </div>

        <div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">{service.official_name}</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-2 flex items-center gap-2">
            <Landmark className="w-4 h-4 text-slate-500" />
            <span>{service.department}</span>
            <span>•</span>
            <span className="text-slate-300 font-semibold">{service.state}</span>
          </p>
        </div>

        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans">{service.description}</p>

        {/* Statutory Metrics Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <span className="text-slate-500 block uppercase font-semibold text-[10px]">Statutory Fee</span>
            <span className="text-emerald-400 font-bold text-base">₹{service.official_fee}</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <span className="text-slate-500 block uppercase font-semibold text-[10px]">Processing Days</span>
            <span className="text-slate-200 font-bold text-base">{service.processing_time}</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs sm:col-span-2">
            <span className="text-slate-500 block uppercase font-semibold text-[10px]">Official Submission Channel</span>
            <span className="text-slate-200 font-medium text-xs truncate block">{service.application_method}</span>
          </div>
        </div>
      </div>

      {/* Grid of Eligibility & Document Checklist */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <EligibilityCard criteria={service.eligibility_criteria} />
        <FeeBreakdown officialFee={service.official_fee} partnerFee={partners[0]?.partner_assistance_fee || 100} showPartner={activeTab === 'assistance'} />
      </div>

      <DocumentChecklist documents={service.required_documents} serviceName={service.official_name} />

      {/* ACTION PATH SWITCHER: [DIY] VS [FIND ASSISTANCE] */}
      <div className="space-y-6">
        <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab('diy')}
            className={`px-6 py-3 rounded-xl font-bold text-sm transition-all flex items-center gap-2 ${
              activeTab === 'diy'
                ? 'bg-saffron-500 text-white shadow-lg shadow-saffron-500/20'
                : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <User className="w-4 h-4" />
            <span>Option A: Do It Yourself (DIY Guide)</span>
          </button>

          <button
            onClick={() => setActiveTab('assistance')}
            className={`px-6 py-3 rounded-xl font-bold text-sm transition-all flex items-center gap-2 ${
              activeTab === 'assistance'
                ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20'
                : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Option B: Find Verified Assistance</span>
          </button>
        </div>

        {/* TAB 1: DIY STEP-BY-STEP WORKFLOW */}
        {activeTab === 'diy' && (
          <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white font-heading">Step-by-Step Official Application Guide</h3>
                <p className="text-xs text-slate-400">Complete these steps on the official government website</p>
              </div>
              <a
                href={service.official_url}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-md transition-colors"
              >
                <span>Open Official Portal</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            <div className="space-y-4">
              {service.diy_steps.map((step, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-saffron-500/10 border border-saffron-500/30 text-saffron-400 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                    {idx + 1}
                  </div>
                  <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans">{step}</p>
                </div>
              ))}
            </div>

            {/* Warning Box */}
            <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5 text-amber-400" />
              <div>
                <span className="font-bold text-sm block">Important Security & Integrity Warning</span>
                <p className="text-amber-300/80 mt-0.5">
                  Always verify that the website URL ends in <strong className="text-white">.gov.in</strong> or <strong className="text-white">.ap.gov.in</strong> before paying official fees or entering Aadhaar details.
                </p>
              </div>
            </div>

            {/* Start DIY Request Tracking Button */}
            <div className="pt-2 flex justify-end">
              <button
                onClick={() => handleCreateRequest(null)}
                className="px-6 py-3 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-bold text-xs flex items-center gap-2 shadow-lg transition-all"
              >
                <span>Save Checklist & Track My DIY Progress</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* TAB 2: VERIFIED PARTNER MARKETPLACE MATCH */}
        {activeTab === 'assistance' && (
          <div className="space-y-6">
            <div className="bg-sky-950/30 p-6 rounded-3xl border border-sky-500/30 space-y-2">
              <div className="flex items-center gap-2 text-sky-400 font-bold text-sm font-heading">
                <ShieldCheck className="w-5 h-5" />
                <span>Verified Assistance Marketplace (NTR / Vijayawada)</span>
              </div>
              <p className="text-xs text-slate-300">
                Connect with verified MeeSeva operators and digital facilitation centers. All partners are background-verified with transparent pricing.
              </p>
            </div>

            {partners.length === 0 ? (
              <div className="p-8 text-center bg-slate-900 rounded-2xl border border-slate-800 text-xs text-slate-400">
                No verified partners currently active in this district. You can complete this service using the DIY guide!
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {partners.map((partner) => (
                  <PartnerCard key={partner.id} partner={partner} onSelect={() => handleCreateRequest(partner.id)} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { SourceBadge } from '../components/SourceBadge';
import { PhysicalPresenceCard } from '../components/PhysicalPresenceCard';
import { DocumentChecklist } from '../components/DocumentChecklist';
import { EligibilityCard } from '../components/EligibilityCard';
import { FeeBreakdown } from '../components/FeeBreakdown';
import { AssistanceTierSelector } from '../components/AssistanceTierSelector';
import { AIChatDrawer } from '../components/AIChatDrawer';
import { Landmark, ExternalLink, ArrowRight, PhoneCall, CheckCircle2, Bot, Sparkles, AlertCircle, Clock, ShieldCheck, Check } from 'lucide-react';

export const ServiceDetails = () => {
  const { id } = useParams();
  const [subService, setSubService] = useState(null);
  const [selectedTier, setSelectedTier] = useState('LEVEL_B_FORM_HELP');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [showCallbackModal, setShowCallbackModal] = useState(false);
  const [requestSubmitting, setRequestSubmitting] = useState(false);
  const [requestSuccess, setRequestSuccess] = useState(false);
  const [aiDrawerOpen, setAiDrawerOpen] = useState(false);

  const assistanceSectionRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchSubServiceData();
  }, [id]);

  const fetchSubServiceData = async () => {
    try {
      setLoading(true);
      const res = await apiService.getSubServiceById(id || 'sub-birth-father-corr');
      setSubService(res.data);
    } catch (err) {
      console.error('Error loading sub-service:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleScrollToAssistance = () => {
    if (assistanceSectionRef.current) {
      assistanceSectionRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleContinueAction = () => {
    if (selectedTier === 'LEVEL_A_DIY') {
      // DIY Level A: Direct link to official portal
      window.open(subService.official_portal_url, '_blank');
    } else {
      // Level B, C, D: Open Callback Request Modal
      setShowCallbackModal(true);
    }
  };

  const handleCreateAssistanceRequest = async () => {
    try {
      setRequestSubmitting(true);
      await apiService.createRequest(
        subService.id,
        selectedTier,
        'Vijayawada, NTR District (AP)',
        notes || `Assistance request for ${subService.sub_service_name}`,
        true
      );
      setRequestSuccess(true);
      setTimeout(() => {
        setShowCallbackModal(false);
        navigate('/dashboard');
      }, 1500);
    } catch (err) {
      console.error('Error creating assistance request:', err);
      // Fallback navigate to login if unauthenticated
      navigate('/login');
    } finally {
      setRequestSubmitting(false);
    }
  };

  if (loading) {
    return <div className="max-w-5xl mx-auto py-12 animate-pulse h-96 bg-slate-900 rounded-3xl" />;
  }

  if (!subService) {
    return (
      <div className="max-w-md mx-auto py-12 text-center text-slate-400 text-xs">
        Sub-service record not found. Please try searching again.
      </div>
    );
  }

  const parentService = subService.parent_service || {};

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-24">
      {/* 1. SERVICE HEADER */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span className="text-xs font-bold uppercase tracking-wider text-saffron-400 bg-saffron-500/10 px-3 py-1 rounded-full border border-saffron-500/20">
            {subService.action_type}
          </span>
          <SourceBadge
            status={subService.confidence_status}
            lastVerified={subService.last_verified}
            sourceUrl={subService.official_portal_url}
            version={subService.information_version}
          />
        </div>

        <div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">
            {subService.sub_service_name}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Category: <span className="text-slate-200 font-semibold">{parentService.category || 'Government Services'}</span> | Department: <span className="text-slate-200 font-semibold">{parentService.department || 'State Govt'}</span>
          </p>
        </div>

        {/* Action Escape Buttons */}
        <div className="flex flex-wrap items-center gap-3 pt-2">
          <button
            onClick={handleScrollToAssistance}
            className="px-6 py-3 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-bold text-xs flex items-center gap-2 shadow-lg transition-colors"
          >
            <span>View DIY & Assistance Options</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <button
            onClick={() => setAiDrawerOpen(true)}
            className="px-5 py-3 rounded-xl bg-slate-900 border border-slate-800 hover:border-saffron-500/50 text-slate-200 font-bold text-xs flex items-center gap-2 transition-colors"
          >
            <Bot className="w-4 h-4 text-saffron-400" />
            <span>Ask GSP AI Assistant</span>
          </button>
        </div>
      </div>

      {/* 2. WHAT IS THIS SERVICE? */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">What is this service?</h3>
        <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans">
          {subService.description || parentService.description || 'Official statutory government service for citizen documentation and record update.'}
        </p>
      </div>

      {/* 3 & 4. ELIGIBILITY & DOCUMENT CHECKLIST */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <EligibilityCard criteria={subService.eligibility_criteria} />
        <FeeBreakdown officialFee={subService.official_fee} partnerFee={150} showPartner={true} />
      </div>

      <DocumentChecklist documents={subService.required_documents} serviceName={subService.sub_service_name} />

      {/* 5, 6, 7. STATUTORY FEES, PROCESSING TIME, PHYSICAL PRESENCE */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Service Requirements & Presence</h3>
        <PhysicalPresenceCard
          requirement={subService.physical_presence_requirement}
          reason={subService.physical_presence_reason}
        />
      </div>

      {/* 8. OFFICIAL PROCEDURE STEPS */}
      {subService.diy_steps && subService.diy_steps.length > 0 && (
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
            <Landmark className="w-4 h-4 text-emerald-400" />
            <span>Official DIY Procedure Steps</span>
          </h3>
          <div className="space-y-2">
            {subService.diy_steps.map((step, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 flex items-start gap-2">
                <span className="font-bold text-emerald-400 shrink-0">{idx + 1}.</span>
                <span>{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 9. HOW CAN GSP HELP YOU? (GENERIC ASSISTANCE TIER SELECTOR) */}
      <div ref={assistanceSectionRef} className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-6">
        <AssistanceTierSelector
          selectedTier={selectedTier}
          onSelectTier={(t) => setSelectedTier(t)}
          officialFee={subService.official_fee}
          physicalPresence={subService.physical_presence_requirement}
        />

        {/* Continue Action Button */}
        <div className="pt-4 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-slate-400">
            Selected Tier: <strong className="text-saffron-400">{selectedTier}</strong>
          </div>

          <button
            onClick={handleContinueAction}
            className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-gradient-to-r from-saffron-500 to-amber-600 hover:from-saffron-600 hover:to-amber-700 text-white font-bold text-xs shadow-xl transition-all flex items-center justify-center gap-2"
          >
            <span>{selectedTier === 'LEVEL_A_DIY' ? 'Proceed to Official Portal (DIY)' : 'Continue with Selected Assistance'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 10. OFFICIAL GOVERNMENT SOURCE LINK */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        <span className="text-slate-400">Official Government Portal:</span>
        <a
          href={subService.official_portal_url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 text-saffron-400 hover:underline font-semibold"
        >
          <span>{subService.official_portal_url}</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      {/* 11. CONTEXTUAL AI CHAT DRAWER */}
      <AIChatDrawer
        isOpen={aiDrawerOpen}
        onClose={() => setAiDrawerOpen(false)}
        contextSubServiceId={subService.id}
        contextSubServiceName={subService.sub_service_name}
      />

      {/* HUMAN CALLBACK / ASSISTANCE REQUEST MODAL */}
      {showCallbackModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="glass-panel w-full max-w-md p-6 rounded-3xl border border-slate-800 space-y-6 bg-slate-900 shadow-2xl">
            {requestSuccess ? (
              <div className="text-center py-6 space-y-3">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
                  <Check className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-white">Assistance Request Created!</h3>
                <p className="text-xs text-slate-400">Redirecting to your citizen tracking dashboard...</p>
              </div>
            ) : (
              <>
                <div className="border-b border-slate-800 pb-3">
                  <h3 className="text-base font-bold text-white font-heading">Confirm Assistance Request</h3>
                  <p className="text-xs text-slate-400 mt-0.5">Would you like a GSP team member or verified partner to contact you?</p>
                </div>

                <div className="space-y-3 text-xs">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block text-[10px] uppercase font-semibold">Service</span>
                    <span className="text-white font-bold">{subService.sub_service_name}</span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block text-[10px] uppercase font-semibold">Selected Assistance</span>
                    <span className="text-saffron-400 font-bold">{selectedTier}</span>
                  </div>

                  <div>
                    <label className="block text-slate-300 mb-1 font-semibold">Describe Your Exact Situation (Optional)</label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="e.g. Need correction on father's spelling."
                      className="w-full bg-slate-950 text-slate-100 border border-slate-800 rounded-xl p-2.5 text-xs focus:outline-none focus:border-saffron-500 h-20"
                    />
                  </div>
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <button
                    onClick={() => setShowCallbackModal(false)}
                    className="w-1/2 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs"
                  >
                    I'll Do It Myself
                  </button>
                  <button
                    onClick={handleCreateAssistanceRequest}
                    disabled={requestSubmitting}
                    className="w-1/2 py-2.5 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-bold text-xs flex items-center justify-center gap-1.5"
                  >
                    <PhoneCall className="w-3.5 h-3.5" />
                    <span>{requestSubmitting ? 'Submitting...' : 'Yes, Contact Me'}</span>
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

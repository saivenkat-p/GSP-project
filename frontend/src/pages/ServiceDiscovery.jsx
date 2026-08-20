import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import { SourceBadge } from '../components/SourceBadge';
import { DocumentChecklist } from '../components/DocumentChecklist';
import { EligibilityCard } from '../components/EligibilityCard';
import { FeeBreakdown } from '../components/FeeBreakdown';
import { PhysicalPresenceCard } from '../components/PhysicalPresenceCard';
import { Bot, Search, ArrowRight, CheckCircle2, AlertCircle, RefreshCw, Sparkles, PhoneCall, HelpCircle, Compass } from 'lucide-react';

export const ServiceDiscovery = () => {
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  
  const [query, setQuery] = useState(initialQuery);
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);
  const [answers, setAnswers] = useState({});
  const [sessionId] = useState(() => `session-${Math.random().toString(36).substring(7)}`);

  const navigate = useNavigate();

  useEffect(() => {
    if (initialQuery) {
      handleNavSearch(initialQuery, {});
    }
  }, [initialQuery]);

  const handleNavSearch = async (userQuery, currentAnswers) => {
    if (!userQuery.trim()) return;
    try {
      setLoading(true);
      const res = await apiService.chatAI(sessionId, userQuery.trim(), 'AP', 'AP-NTR', 'Vijayawada Urban', currentAnswers);
      setAiResponse(res.data);
    } catch (err) {
      console.error('AI navigation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (field, option) => {
    const updatedAnswers = { ...answers, [field]: option };
    setAnswers(updatedAnswers);
    handleNavSearch(query, updatedAnswers);
  };

  const handleNewQuerySubmit = (e) => {
    e.preventDefault();
    setAnswers({});
    handleNavSearch(query, {});
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-20">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-saffron-500/10 border border-saffron-500/30 text-saffron-400 text-xs font-semibold">
          <Bot className="w-4 h-4" />
          <span>Universal Service Resolution Engine</span>
        </div>
        <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">
          Guided Service Navigator
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
          Searches complete service knowledge base and resolves your exact requirement.
        </p>
      </div>

      {/* Global Query Bar */}
      <form onSubmit={handleNewQuerySubmit} className="glass-panel p-2 rounded-2xl border border-slate-800 flex items-center gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe what you need to get done (e.g. 'pan card', 'father name wrong in birth cert')..."
          className="w-full bg-transparent px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2.5 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-bold text-xs transition-colors shrink-0 flex items-center gap-1.5"
        >
          {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          <span>Universal Search</span>
        </button>
      </form>

      {/* LOADING */}
      {loading && (
        <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center space-y-3">
          <Bot className="w-10 h-10 text-saffron-400 animate-bounce mx-auto" />
          <p className="text-sm font-semibold text-slate-200">Executing Universal Service Resolution Pipeline...</p>
        </div>
      )}

      {/* RESPONSE WORKFLOW */}
      {!loading && aiResponse && (
        <div className="space-y-6">
          {/* Grounded Intent Banner (Renders SourceBadge ONLY if verified service is retrieved) */}
          {aiResponse.confidence_status !== 'NOT_FOUND' && (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <SourceBadge status={aiResponse.confidence_status} lastVerified={aiResponse.source_last_verified} />
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span>Confidence:</span>
                  <span className="font-bold text-emerald-400">{(aiResponse.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>

              <p className="text-sm text-slate-200 leading-relaxed font-sans">{aiResponse.explanation}</p>
            </div>
          )}

          {/* DYNAMIC FOLLOW-UP QUESTION FOR SUB-OPTIONS */}
          {aiResponse.needs_follow_up && aiResponse.questions && aiResponse.questions.length > 0 && (
            <div className="bg-slate-900 p-6 rounded-2xl border border-saffron-500/40 space-y-4 shadow-xl">
              <div className="flex items-center gap-2 text-saffron-400 font-bold text-sm uppercase tracking-wide">
                <Bot className="w-4 h-4" />
                <span>Select Specific Service Option</span>
              </div>

              {aiResponse.questions.map((q, idx) => (
                <div key={idx} className="space-y-3 pt-2">
                  <label className="block text-sm font-bold text-slate-100">{q.question}</label>
                  {q.options && (
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      {q.options.map((opt) => (
                        <button
                          key={opt}
                          onClick={() => handleAnswerSelect(q.field, opt)}
                          className={`p-4 rounded-2xl border text-left text-xs transition-all font-bold flex flex-col justify-between space-y-2 ${
                            answers[q.field] === opt
                              ? 'bg-saffron-500 text-white border-saffron-400 shadow-lg'
                              : 'bg-slate-950 border-slate-800 hover:border-saffron-500/60 text-slate-100 hover:bg-slate-900'
                          }`}
                        >
                          <span className="text-sm">{opt}</span>
                          <span className="text-[10px] opacity-70 block font-normal">Click to select option</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* SECTION 15 HONEST LOW CONFIDENCE STATE */}
          {aiResponse.confidence_status === 'NOT_FOUND' && (
            <div className="p-8 rounded-3xl bg-slate-900 border border-amber-500/30 text-center space-y-6">
              <div className="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-400 flex items-center justify-center mx-auto">
                <HelpCircle className="w-6 h-6" />
              </div>

              <div className="space-y-1">
                <h3 className="text-lg font-bold text-white font-heading">I couldn't identify the exact service yet.</h3>
                <p className="text-xs text-slate-400 max-w-md mx-auto">
                  Try rephrasing your search query, or select from likely services below.
                </p>
              </div>

              {/* Action Escape Buttons */}
              <div className="flex flex-wrap items-center justify-center gap-3 text-xs">
                <button onClick={() => setQuery('')} className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200">
                  Try Another Search
                </button>
                <Link to="/" className="px-4 py-2 rounded-xl bg-saffron-500/10 border border-saffron-500/30 text-saffron-400 font-semibold">
                  Browse Government Services
                </Link>
              </div>

              {/* Did You Mean Candidates */}
              {aiResponse.candidate_suggestions && aiResponse.candidate_suggestions.length > 0 && (
                <div className="pt-4 border-t border-slate-800 text-left space-y-3 max-w-md mx-auto">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Did you mean?</span>
                  <div className="space-y-2">
                    {aiResponse.candidate_suggestions.map((c) => (
                      <Link
                        key={c.id}
                        to={`/services/catalog/${c.id}`}
                        className="p-3 rounded-xl bg-slate-950 border border-slate-800 hover:border-saffron-500/50 flex items-center justify-between text-xs text-slate-200 block"
                      >
                        <span className="font-semibold">{c.name}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-saffron-400" />
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* RESOLVED SUB-SERVICE RECORD */}
          {!aiResponse.needs_follow_up && aiResponse.resolved_sub_service && (
            <div className="space-y-6">
              <div className="bg-slate-900 p-8 rounded-3xl border border-emerald-500/30 space-y-6">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
                  <div>
                    <SourceBadge
                      status={aiResponse.resolved_sub_service.confidence_status}
                      lastVerified={aiResponse.resolved_sub_service.last_verified}
                      version={aiResponse.resolved_sub_service.information_version}
                    />
                    <h2 className="text-2xl font-extrabold text-white mt-2 font-heading">{aiResponse.resolved_sub_service.sub_service_name}</h2>
                    <p className="text-xs text-slate-400 mt-1">Official Channel: {aiResponse.resolved_sub_service.application_method}</p>
                  </div>

                  <button
                    onClick={() => navigate(`/services/${aiResponse.resolved_sub_service.id}`)}
                    className="w-full sm:w-auto px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 shadow-lg transition-all shrink-0"
                  >
                    <span>View DIY & Assistance Options</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>

                <PhysicalPresenceCard
                  requirement={aiResponse.resolved_sub_service.physical_presence_requirement}
                  reason={aiResponse.resolved_sub_service.physical_presence_reason}
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <EligibilityCard criteria={aiResponse.eligibility} />
                  <FeeBreakdown officialFee={aiResponse.official_fee} partnerFee={150} showPartner={true} />
                </div>

                <DocumentChecklist documents={aiResponse.documents} serviceName={aiResponse.resolved_sub_service.sub_service_name} />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

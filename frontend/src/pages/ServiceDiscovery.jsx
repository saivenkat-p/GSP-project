import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { TrustBadge } from '../components/TrustBadge';
import { DocumentChecklist } from '../components/DocumentChecklist';
import { EligibilityCard } from '../components/EligibilityCard';
import { FeeBreakdown } from '../components/FeeBreakdown';
import { Bot, User, ArrowRight, ShieldCheck, Landmark, CheckCircle2, AlertCircle, RefreshCw, Sparkles } from 'lucide-react';

export const ServiceDiscovery = () => {
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  
  const [query, setQuery] = useState(initialQuery);
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);
  const [answers, setAnswers] = useState({});

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
      const res = await apiService.navigateAI(userQuery, 'Andhra Pradesh', null, currentAnswers);
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
          <span>Grounded AI Service Discovery Engine</span>
        </div>
        <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">
          Guided Service Navigator
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
          Our AI matches verified government statutory rules and asks only necessary questions.
        </p>
      </div>

      {/* Query Bar */}
      <form onSubmit={handleNewQuerySubmit} className="glass-panel p-2 rounded-2xl border border-slate-800 flex items-center gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe what you need to get done..."
          className="w-full bg-transparent px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2.5 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-semibold text-xs transition-colors shrink-0 flex items-center gap-1.5"
        >
          {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          <span>Analyze Query</span>
        </button>
      </form>

      {/* CONVERSATIONAL AI WORKFLOW INTERACTION */}
      {loading && (
        <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center space-y-3">
          <Bot className="w-10 h-10 text-saffron-400 animate-bounce mx-auto" />
          <p className="text-sm font-semibold text-slate-200">Matching verified AP state database & government rules...</p>
        </div>
      )}

      {!loading && aiResponse && (
        <div className="space-y-6">
          {/* Grounded AI Intent Header Card */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <TrustBadge type="ai" />
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <span>Confidence score:</span>
                <span className="font-bold text-emerald-400">{(aiResponse.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>

            <p className="text-sm text-slate-200 leading-relaxed font-sans">{aiResponse.explanation}</p>

            {aiResponse.warnings && aiResponse.warnings.length > 0 && (
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 space-y-1">
                <span className="font-semibold block uppercase text-[10px]">Official Notice:</span>
                {aiResponse.warnings.map((w, idx) => (
                  <p key={idx}>• {w}</p>
                ))}
              </div>
            )}
          </div>

          {/* FOLLOW-UP QUESTIONS CARD (If needed) */}
          {aiResponse.needs_follow_up && aiResponse.questions && aiResponse.questions.length > 0 && (
            <div className="bg-slate-900 p-6 rounded-2xl border border-saffron-500/30 space-y-4 shadow-xl">
              <div className="flex items-center gap-2 text-saffron-400 font-bold text-sm uppercase tracking-wide">
                <Bot className="w-4 h-4" />
                <span>Required Clarification Question</span>
              </div>

              {aiResponse.questions.map((q, idx) => (
                <div key={idx} className="space-y-3 pt-2">
                  <label className="block text-sm font-semibold text-slate-100">{q.question}</label>
                  {q.options && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {q.options.map((opt) => (
                        <button
                          key={opt}
                          onClick={() => handleAnswerSelect(q.field, opt)}
                          className={`p-3 rounded-xl border text-left text-xs transition-all font-medium flex items-center justify-between ${
                            answers[q.field] === opt
                              ? 'bg-saffron-500 text-white border-saffron-400 font-bold'
                              : 'bg-slate-950 border-slate-800 hover:border-saffron-500/50 text-slate-200'
                          }`}
                        >
                          <span>{opt}</span>
                          {answers[q.field] === opt && <CheckCircle2 className="w-4 h-4 text-white" />}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* UNKNOWN / NOT FOUND SERVICE CASE (Zero Hallucination Policy) */}
          {aiResponse.source_status === 'not_found' && (
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 text-center space-y-3">
              <AlertCircle className="w-8 h-8 text-amber-400 mx-auto" />
              <h3 className="text-base font-bold text-slate-100">No Verified Government Record Found</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">{aiResponse.explanation}</p>
              <button
                onClick={() => setQuery('Income Certificate')}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-200 text-xs font-semibold hover:bg-slate-700 transition-colors"
              >
                Try 'Income Certificate'
              </button>
            </div>
          )}

          {/* RESOLVED SERVICE CARD & ACTION ENTRY */}
          {!aiResponse.needs_follow_up && aiResponse.service && (
            <div className="space-y-6">
              <div className="bg-slate-900 p-6 rounded-2xl border border-emerald-500/30 space-y-6">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
                  <div>
                    <TrustBadge type="official" lastVerified={aiResponse.service.source_last_verified} isDemo={aiResponse.service.is_demo_data} />
                    <h2 className="text-2xl font-extrabold text-white mt-2 font-heading">{aiResponse.service.official_name}</h2>
                    <p className="text-xs text-slate-400 mt-1">{aiResponse.service.department} • {aiResponse.service.state}</p>
                  </div>

                  <button
                    onClick={() => navigate(`/services/${aiResponse.service.id}`)}
                    className="w-full sm:w-auto px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 shadow-lg transition-all shrink-0"
                  >
                    <span>View Complete DIY & Assistance Options</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <EligibilityCard criteria={aiResponse.eligibility} />
                  <FeeBreakdown officialFee={aiResponse.official_fee} />
                </div>

                <DocumentChecklist documents={aiResponse.documents} serviceName={aiResponse.service.official_name} />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

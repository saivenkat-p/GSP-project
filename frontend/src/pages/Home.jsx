import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { ServiceCard } from '../components/ServiceCard';
import { TrustBadge } from '../components/TrustBadge';
import { Search, Compass, Sparkles, ArrowRight, ShieldCheck, Landmark, CheckCircle2, FileText, Layers } from 'lucide-react';

export const Home = () => {
  const [query, setQuery] = useState('');
  const [services, setServices] = useState([]);
  const [categories, setCategories] = useState(['All']);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    fetchInitialData();
  }, [selectedCategory]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const [srvRes, catRes] = await Promise.all([
        apiService.getServices(selectedCategory, 'Andhra Pradesh'),
        apiService.getCategories(),
      ]);
      setServices(srvRes.data);
      setCategories(catRes.data);
    } catch (err) {
      console.error('Error fetching home data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    navigate(`/discover?q=${encodeURIComponent(query)}`);
  };

  const setExampleQuery = (text) => {
    setQuery(text);
    navigate(`/discover?q=${encodeURIComponent(text)}`);
  };

  return (
    <div className="space-y-16 pb-20">
      {/* HERO SECTION */}
      <section className="relative pt-12 pb-16 overflow-hidden rounded-3xl bg-gradient-to-b from-slate-900 via-slate-950 to-slate-950 border border-slate-800/80 px-6 sm:px-12 text-center">
        {/* Glowing Background Orbs */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-96 bg-saffron-500/10 blur-[120px] rounded-full pointer-events-none" />
        <div className="absolute bottom-0 right-10 w-80 h-80 bg-emerald-500/10 blur-[100px] rounded-full pointer-events-none" />

        <div className="relative max-w-4xl mx-auto space-y-6">
          {/* Top Pill Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-saffron-500/10 border border-saffron-500/30 text-saffron-400 text-xs font-semibold">
            <Sparkles className="w-4 h-4 text-saffron-400 animate-spin" />
            <span>AI-Powered Citizen Guidance & Verification Engine</span>
          </div>

          {/* Core Question Header */}
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight font-heading">
            <span className="block">"I need to get this done.</span>
            <span className="bg-gradient-to-r from-saffron-400 via-amber-300 to-emerald-400 bg-clip-text text-transparent">
              What exactly should I do?"
            </span>
          </h1>

          <p className="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Describe your requirement in plain everyday language. Our AI navigator matches verified government rules, statutory fees, required document checklists, and official portals.
          </p>

          {/* Primary Citizen Interaction Box */}
          <form onSubmit={handleSearchSubmit} className="max-w-2xl mx-auto pt-4">
            <div className="glass-panel p-2 rounded-2xl border border-slate-700 shadow-2xl flex flex-col sm:flex-row items-center gap-2">
              <div className="flex items-center gap-3 px-4 py-2 w-full">
                <Search className="w-5 h-5 text-saffron-400 shrink-0" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g. 'I need an income certificate for college admission in Vijayawada'"
                  className="w-full bg-transparent text-slate-100 placeholder-slate-400 text-sm focus:outline-none"
                />
              </div>
              <button
                type="submit"
                className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-saffron-500 to-amber-600 hover:from-saffron-600 hover:to-amber-700 text-white font-bold text-sm shadow-lg shadow-saffron-500/20 transition-all shrink-0 flex items-center justify-center gap-2"
              >
                <span>Find My Service</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Real Prompt Examples */}
          <div className="pt-2 text-xs text-slate-400 flex flex-wrap items-center justify-center gap-2">
            <span className="font-semibold text-slate-500">Popular queries:</span>
            <button
              onClick={() => setExampleQuery('Income certificate for college admission')}
              className="px-3 py-1 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
            >
              "Income certificate for college"
            </button>
            <button
              onClick={() => setExampleQuery('Encumbrance certificate for property in Vijayawada')}
              className="px-3 py-1 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
            >
              "EC for land purchase"
            </button>
            <button
              onClick={() => setExampleQuery('Driving license renewal Form 1A medical')}
              className="px-3 py-1 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
            >
              "DL renewal Parivahan"
            </button>
            <button
              onClick={() => setExampleQuery('Caste certificate for reservation')}
              className="px-3 py-1 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
            >
              "SC/BC Caste Certificate"
            </button>
          </div>
        </div>
      </section>

      {/* PLATFORM MANDATE & TRUST PRINCIPLES */}
      <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="w-9 h-9 rounded-xl bg-saffron-500/10 text-saffron-400 flex items-center justify-center font-bold">
            1
          </div>
          <h4 className="text-sm font-bold text-slate-200 font-heading">Plain Language Intent</h4>
          <p className="text-xs text-slate-400">Describe your goal without memorizing complex government bureau names.</p>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
            2
          </div>
          <h4 className="text-sm font-bold text-slate-200 font-heading">Verified Source Audit</h4>
          <p className="text-xs text-slate-400">Every service includes last-verified timestamp and official portal URL.</p>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="w-9 h-9 rounded-xl bg-sky-500/10 text-sky-400 flex items-center justify-center font-bold">
            3
          </div>
          <h4 className="text-sm font-bold text-slate-200 font-heading">DIY or Assistance</h4>
          <p className="text-xs text-slate-400">Apply yourself on official portal or get nearby verified partner help.</p>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="w-9 h-9 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center font-bold">
            4
          </div>
          <h4 className="text-sm font-bold text-slate-200 font-heading">Fee Transparency</h4>
          <p className="text-xs text-slate-400">Statutory official fee explicitly separated from partner facilitation fee.</p>
        </div>
      </section>

      {/* VERIFIED SERVICE EXPLORER */}
      <section className="space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-xl font-bold text-white font-heading flex items-center gap-2">
              <Landmark className="w-5 h-5 text-saffron-400" />
              <span>Verified Government Services Catalog</span>
            </h2>
            <p className="text-xs text-slate-400">Andhra Pradesh state & national verified statutory services</p>
          </div>

          {/* Category Filters */}
          <div className="flex flex-wrap items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-lg transition-colors font-medium ${
                  selectedCategory === cat
                    ? 'bg-saffron-500 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-pulse">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-64 bg-slate-900 rounded-2xl border border-slate-800" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {services.map((srv) => (
              <ServiceCard key={srv.id} service={srv} />
            ))}
          </div>
        )}
      </section>

      {/* NON-NEGOTIABLE ARCHITECTURE BANNER */}
      <section className="bg-gradient-to-r from-slate-900 via-slate-950 to-slate-900 rounded-3xl p-8 border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 text-saffron-400 font-bold text-xs uppercase tracking-wider">
          <ShieldCheck className="w-4 h-4" />
          <span>Product Architecture Guarantee</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center text-xs">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="text-slate-500 font-bold block uppercase">Step 1</span>
            <span className="font-bold text-white text-sm">Discovery</span>
            <p className="text-slate-400 text-[11px]">AI intent matching</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="text-slate-500 font-bold block uppercase">Step 2</span>
            <span className="font-bold text-white text-sm">Guidance</span>
            <p className="text-slate-400 text-[11px]">Eligibility & document rules</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="text-slate-500 font-bold block uppercase">Step 3</span>
            <span className="font-bold text-white text-sm">Assistance</span>
            <p className="text-slate-400 text-[11px]">Verified partner support</p>
          </div>
          <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30 space-y-1">
            <span className="text-emerald-400 font-bold block uppercase">Final Step</span>
            <span className="font-bold text-emerald-300 text-sm">Official Authority</span>
            <p className="text-emerald-400/80 text-[11px]">MeeSeva / Tahsildar approval</p>
          </div>
        </div>
      </section>
    </div>
  );
};

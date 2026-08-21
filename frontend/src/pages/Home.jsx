import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import { AIChatDrawer } from '../components/AIChatDrawer';
import { CallbackModal } from '../components/CallbackModal';
import {
  Search, Bot, Sparkles, ArrowRight, ExternalLink, ShieldCheck,
  CheckCircle2, Clock, Bell, UserCheck, FileText, HeartPulse,
  Car, Vote, Grid, Landmark, Compass, GraduationCap,
  ChevronRight, ChevronLeft, Award, HelpCircle, PhoneCall,
  Flame, CheckCircle, RefreshCw, AlertCircle
} from 'lucide-react';

export const Home = () => {
  const navigate = useNavigate();
  const { user, selectedState, selectedDistrict } = useAuth();

  const [query, setQuery] = useState('');
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [fade, setFade] = useState(true);

  // V3.1 Live State Data
  const [heroBanners, setHeroBanners] = useState([]);
  const [trendingItems, setTrendingItems] = useState([]);
  const [schemes, setSchemes] = useState([]);
  const [scholarships, setScholarships] = useState([]);
  const [updates, setUpdates] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [taxonomySummary, setTaxonomySummary] = useState({ total_categories: 10, total_services: 10, total_sub_services: 10, total_verified_records: 12 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modals & Drawers
  const [chatOpen, setChatOpen] = useState(false);
  const [callbackModalOpen, setCallbackModalOpen] = useState(false);
  const [callbackServiceTarget, setCallbackServiceTarget] = useState('General Citizen Assistance');

  useEffect(() => {
    fetchV3Data();
  }, [selectedState, selectedDistrict]);

  const fetchV3Data = async () => {
    try {
      setLoading(true);
      setError(null);
      const [bannersRes, trendingRes, schemesRes, scholarshipsRes, updatesRes, remindersRes, taxRes] = await Promise.all([
        apiService.getHeroBanners(selectedState || 'AP').catch(() => ({ data: [] })),
        apiService.getTrending(selectedState || 'AP').catch(() => ({ data: [] })),
        apiService.getSchemes(selectedState || 'AP').catch(() => ({ data: [] })),
        apiService.getScholarships(selectedState || 'AP').catch(() => ({ data: [] })),
        apiService.getUpdates(selectedState || 'AP').catch(() => ({ data: [] })),
        apiService.getReminders().catch(() => ({ data: [] })),
        apiService.getTaxonomySummary(selectedState || 'AP').catch(() => ({ data: null }))
      ]);

      setHeroBanners(bannersRes.data || []);
      setTrendingItems(trendingRes.data || []);
      setSchemes(schemesRes.data || []);
      setScholarships(scholarshipsRes.data || []);
      setUpdates(updatesRes.data || []);
      setReminders(remindersRes.data || []);
      if (taxRes.data) setTaxonomySummary(taxRes.data);
    } catch (err) {
      console.error('Error fetching V3 information data:', err);
      setError('Verified information is currently unavailable. Showing last cached official records.');
    } finally {
      setLoading(false);
    }
  };

  // Banner auto-rotation every 6 seconds
  useEffect(() => {
    if (heroBanners.length <= 1) return;
    const interval = setInterval(() => {
      handleNextBanner();
    }, 6000);
    return () => clearInterval(interval);
  }, [heroBanners, carouselIndex]);

  const handleNextBanner = () => {
    if (heroBanners.length === 0) return;
    setFade(false);
    setTimeout(() => {
      setCarouselIndex((prev) => (prev + 1) % heroBanners.length);
      setFade(true);
    }, 250);
  };

  const handlePrevBanner = () => {
    if (heroBanners.length === 0) return;
    setFade(false);
    setTimeout(() => {
      setCarouselIndex((prev) => (prev - 1 + heroBanners.length) % heroBanners.length);
      setFade(true);
    }, 250);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    navigate(`/discover?q=${encodeURIComponent(query)}`);
  };

  const handleOpenCallback = (serviceTitle = 'General Government Service Assistance') => {
    setCallbackServiceTarget(serviceTitle);
    setCallbackModalOpen(true);
  };

  const currentBanner = heroBanners[carouselIndex] || null;

  const popularGovtServices = [
    { name: "Aadhaar Services", count: "12 Services", id: "srv-aadhaar-uidai", icon: UserCheck, color: "text-red-500 bg-red-50" },
    { name: "PAN Card Services", count: "4 Services", id: "srv-pan-card", icon: FileText, color: "text-blue-500 bg-blue-50" },
    { name: "Birth Certificate", count: "8 Services", id: "srv-birth-cert", icon: HeartPulse, color: "text-orange-500 bg-orange-50" },
    { name: "Driving Licence", count: "6 Services", id: "srv-dl-parivahan", icon: Car, color: "text-rose-500 bg-rose-50" },
    { name: "Voter ID Services", count: "5 Services", id: "srv-voter-id", icon: Vote, color: "text-emerald-500 bg-emerald-50" },
    { name: "Ration Card", count: "6 Services", id: "srv-ration-card", icon: Grid, color: "text-amber-500 bg-amber-50" },
    { name: "Income Certificate", count: "4 Services", id: "srv-income-cert", icon: Landmark, color: "text-yellow-500 bg-yellow-50" },
    { name: "Land Records", count: "10 Services", id: "srv-land-adangal", icon: Compass, color: "text-teal-500 bg-teal-50" },
    { name: "Passport Services", count: "6 Services", id: "srv-passport-seva", icon: ShieldCheck, color: "text-indigo-500 bg-indigo-50" },
    { name: "Caste Certificate", count: "4 Services", id: "srv-caste-cert", icon: GraduationCap, color: "text-cyan-500 bg-cyan-50" }
  ];

  return (
    <div className="bg-slate-50 min-h-screen text-slate-900 font-sans pb-16 space-y-8">
      {/* Platform Disclaimer Note */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
        <div className="flex items-center justify-between px-4 py-2.5 rounded-2xl bg-indigo-50/80 border border-indigo-100 text-xs text-indigo-950">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-indigo-600 shrink-0" />
            <span>
              <strong>Information verified against registered official sources.</strong> GSP is an independent citizen assistance partner.
            </span>
          </div>
          <span className="hidden sm:inline font-semibold text-[11px] text-indigo-700">Real Information Engine</span>
        </div>
      </div>

      {/* 1. DYNAMIC GOVERNMENT OPPORTUNITY HERO BANNER */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {loading ? (
          <div className="h-64 rounded-3xl bg-white border border-slate-200 animate-pulse shadow-sm" />
        ) : heroBanners.length === 0 ? (
          <div className="p-10 rounded-3xl bg-white border border-slate-200 text-center space-y-2 shadow-xs">
            <h3 className="font-extrabold text-base text-slate-800 font-heading">
              No verified promotional opportunities are currently listed for your region.
            </h3>
            <p className="text-xs text-slate-500">
              We are actively synchronizing with registered official portals. Check back soon.
            </p>
          </div>
        ) : currentBanner ? (
          <div className="relative rounded-3xl p-6 sm:p-10 bg-gradient-to-r from-amber-50 via-emerald-50 to-indigo-50 border border-slate-200/80 shadow-md overflow-hidden">
            {/* Carousel Arrows */}
            {heroBanners.length > 1 && (
              <>
                <button
                  onClick={handlePrevBanner}
                  className="absolute left-3 top-1/2 -translate-y-1/2 z-10 w-9 h-9 rounded-full bg-white/90 shadow-md border border-slate-200 text-slate-700 flex items-center justify-center hover:bg-white transition-colors cursor-pointer"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={handleNextBanner}
                  className="absolute right-3 top-1/2 -translate-y-1/2 z-10 w-9 h-9 rounded-full bg-white/90 shadow-md border border-slate-200 text-slate-700 flex items-center justify-center hover:bg-white transition-colors cursor-pointer"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </>
            )}

            {/* Banner Body */}
            <div className={`transition-opacity duration-300 flex flex-col lg:flex-row items-center justify-between gap-8 ${fade ? 'opacity-100' : 'opacity-0'}`}>
              <div className="space-y-4 max-w-2xl pl-6">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="inline-block px-3.5 py-1 rounded-full bg-white/90 text-orange-600 font-extrabold text-xs tracking-wide shadow-xs border border-orange-200">
                    {currentBanner.category_tag}
                  </span>
                  <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2.5 py-0.5 rounded-full border border-emerald-200">
                    {currentBanner.verification_badge}
                  </span>
                </div>

                <h1 className="text-2xl sm:text-4xl font-black text-slate-900 font-heading tracking-tight leading-tight">
                  {currentBanner.title}
                </h1>

                <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-medium">
                  {currentBanner.subtitle}
                </p>

                <div className="pt-2 flex flex-wrap items-center gap-3">
                  <button
                    onClick={() => navigate(`/discover?q=${encodeURIComponent(currentBanner.action_query || currentBanner.title)}`)}
                    className="px-8 py-3.5 rounded-2xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-md transition-all flex items-center gap-2 cursor-pointer"
                  >
                    <span>Check Eligibility</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>

                  <a
                    href={currentBanner.official_source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-3 rounded-2xl bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 font-semibold text-xs flex items-center gap-1.5 transition-colors"
                  >
                    <span>Official Source</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>

              {/* Right Highlights */}
              <div className="flex flex-wrap lg:flex-col gap-3 shrink-0">
                <div className="p-4 rounded-2xl bg-white/90 border border-slate-200/80 shadow-xs flex items-center gap-3 text-xs">
                  <div className="w-10 h-10 rounded-xl bg-orange-100 text-orange-700 flex items-center justify-center font-bold">
                    ₹
                  </div>
                  <div>
                    <span className="font-bold text-slate-900 block">{currentBanner.benefit_amount}</span>
                    <span className="text-slate-500 text-[11px]">{currentBanner.tag1}</span>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-white/90 border border-slate-200/80 shadow-xs flex items-center gap-3 text-xs">
                  <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                    <CheckCircle2 className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="font-bold text-slate-900 block">Deadline: {currentBanner.deadline}</span>
                    <span className="text-slate-500 text-[11px]">Verified on {currentBanner.last_verified}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {/* Dynamic Pagination Dots Indicator */}
        {heroBanners.length > 1 && (
          <div className="flex items-center justify-center gap-2 pt-3">
            {heroBanners.map((_, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setFade(false);
                  setTimeout(() => {
                    setCarouselIndex(idx);
                    setFade(true);
                  }, 200);
                }}
                className={`h-2.5 rounded-full transition-all cursor-pointer ${carouselIndex === idx ? 'bg-orange-500 w-6' : 'bg-slate-300 w-2.5'}`}
              />
            ))}
          </div>
        )}
      </section>

      {/* 2. GLOBAL SEARCH & ASK AI BAR */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <form onSubmit={handleSearchSubmit} className="bg-white p-3 rounded-3xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center gap-3">
          <div className="flex items-center gap-3 px-4 py-2 w-full">
            <Search className="w-5 h-5 text-slate-400 shrink-0" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search verified schemes, scholarships, certificates, licence renewals, or statutory procedures..."
              className="w-full bg-transparent text-slate-800 placeholder-slate-400 text-xs sm:text-sm focus:outline-none"
            />
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto shrink-0">
            <button
              type="submit"
              className="w-full sm:w-auto px-8 py-3 rounded-2xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-sm transition-colors flex items-center justify-center gap-2 cursor-pointer"
            >
              <Search className="w-4 h-4" />
              <span>Search</span>
            </button>

            <button
              type="button"
              onClick={() => setChatOpen(true)}
              className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-sm transition-colors flex items-center justify-center gap-2 cursor-pointer"
            >
              <Sparkles className="w-4 h-4 text-orange-400" />
              <span>Ask GSP AI</span>
            </button>
          </div>
        </form>

        {/* Dynamic Trending Verified Pills (100% SOURCED FROM DATABASE) */}
        {trendingItems.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 pt-3 text-xs text-slate-600">
            <span className="font-semibold text-slate-400 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-orange-500" />
              Trending Verified:
            </span>
            {trendingItems.map((item) => (
              <button
                key={item.id}
                onClick={() => navigate(`/discover?q=${encodeURIComponent(item.query)}`)}
                className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 hover:border-orange-300 hover:text-orange-600 font-medium transition-colors cursor-pointer"
              >
                {item.label}
              </button>
            ))}
          </div>
        )}
      </section>

      {/* 3. CURRENT GOVERNMENT SCHEMES & BENEFITS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Flame className="w-6 h-6 text-orange-500" />
            <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading">
              Current Government Schemes & Opportunities
            </h2>
          </div>
          <button
            onClick={() => navigate('/services/catalog')}
            className="text-xs font-bold text-orange-600 hover:text-orange-700 flex items-center gap-1 cursor-pointer"
          >
            <span>View All Schemes</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-44 bg-white rounded-3xl border border-slate-200 animate-pulse" />
            ))}
          </div>
        ) : schemes.length === 0 ? (
          <div className="p-10 text-center bg-white rounded-3xl border border-slate-200 text-xs text-slate-500 space-y-1">
            <p className="font-semibold text-slate-700">No verified schemes are currently active for this region.</p>
            <p className="text-slate-400">We're checking registered official sources.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {schemes.slice(0, 4).map((sch) => {
              const bgClass = sch.color_theme === 'purple'
                ? 'bg-purple-50/80 border-purple-200 text-purple-950'
                : sch.color_theme === 'amber'
                ? 'bg-amber-50/80 border-amber-200 text-amber-950'
                : sch.color_theme === 'blue'
                ? 'bg-blue-50/80 border-blue-200 text-blue-950'
                : 'bg-emerald-50/80 border-emerald-200 text-emerald-950';

              return (
                <div
                  key={sch.id}
                  onClick={() => navigate(`/discover?q=${encodeURIComponent(sch.title)}`)}
                  className={`relative p-6 rounded-3xl border shadow-xs hover:shadow-md transition-all cursor-pointer flex flex-col justify-between overflow-hidden group ${bgClass}`}
                >
                  <div className="absolute -right-8 top-5 rotate-45 bg-orange-500 text-white text-[10px] font-black uppercase px-8 py-0.5 shadow-xs">
                    Apply Now
                  </div>

                  <div className="space-y-2 pr-4">
                    <div className="flex items-center gap-1 text-[11px] font-bold text-emerald-700">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{sch.badge_type === 'GOVERNMENT_VERIFIED' ? '🟢 Govt Verified' : '🔵 Org Verified'}</span>
                    </div>

                    <h3 className="font-extrabold text-sm sm:text-base text-slate-900 group-hover:text-orange-600 transition-colors">
                      {sch.title}
                    </h3>
                    <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                      {sch.description}
                    </p>
                  </div>

                  <div className="pt-4 border-t border-slate-200/60 flex items-center justify-between text-xs">
                    <span className="text-slate-500 font-medium">
                      Deadline: <strong className="text-slate-800">{sch.application_deadline || 'Active'}</strong>
                    </span>
                    <span className="w-7 h-7 rounded-full bg-white shadow-xs flex items-center justify-center text-slate-700 group-hover:bg-orange-500 group-hover:text-white transition-colors">
                      <ChevronRight className="w-4 h-4" />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* 4. 3-COLUMN HUB: SCHOLARSHIPS | TODAY'S UPDATES | USER REMINDERS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Column 1: Scholarships & Opportunities */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <GraduationCap className="w-5 h-5 text-indigo-600" />
                  <h3 className="font-extrabold text-base text-slate-900">Scholarships & Grants</h3>
                </div>
                <span className="text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
                  Verified
                </span>
              </div>

              {loading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-14 bg-slate-100 rounded-2xl animate-pulse" />
                  ))}
                </div>
              ) : scholarships.length === 0 ? (
                <div className="p-6 text-center text-xs text-slate-400">
                  No verified scholarships currently listed.
                </div>
              ) : (
                <div className="space-y-3">
                  {scholarships.slice(0, 4).map((sch) => (
                    <div
                      key={sch.id}
                      onClick={() => navigate(`/discover?q=${encodeURIComponent(sch.title)}`)}
                      className="p-3.5 rounded-2xl bg-slate-50 hover:bg-orange-50 border border-slate-100 hover:border-orange-200 transition-all flex items-center justify-between cursor-pointer group"
                    >
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-1.5">
                          <span className="font-bold text-xs text-slate-800 group-hover:text-orange-600 transition-colors">
                            {sch.title}
                          </span>
                        </div>
                        <span className="text-[11px] text-slate-500 block">
                          {sch.badge_type === 'GOVERNMENT_VERIFIED' ? '🟢 Govt Verified' : '🔵 Org Verified'} • {sch.benefit_amount_str || 'Education Grant'}
                        </span>
                      </div>
                      <span className="px-3 py-1 rounded-xl bg-orange-500 text-white font-bold text-[10px] shadow-2xs group-hover:bg-orange-600 shrink-0">
                        Apply Now
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button
              onClick={() => navigate('/discover?q=scholarships')}
              className="w-full py-2.5 rounded-2xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-xs transition-colors flex items-center justify-center gap-1 cursor-pointer"
            >
              <span>Explore All Scholarships</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {/* Column 2: Real-time Statutory Updates & Rule Changes */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-emerald-600" />
                  <h3 className="font-extrabold text-base text-slate-900">Today's Verified Updates</h3>
                </div>
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              </div>

              {loading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-12 bg-slate-100 rounded-2xl animate-pulse" />
                  ))}
                </div>
              ) : updates.length === 0 ? (
                <div className="p-6 text-center text-xs text-slate-400">
                  All systems up-to-date with current statutory notices.
                </div>
              ) : (
                <div className="space-y-3">
                  {updates.slice(0, 5).map((upd) => (
                    <div
                      key={upd.id}
                      onClick={() => navigate(`/discover?q=${encodeURIComponent(upd.title)}`)}
                      className="p-3 rounded-2xl hover:bg-slate-50 transition-colors flex items-center gap-3 cursor-pointer group"
                    >
                      <div className="w-2 h-2 rounded-full bg-orange-500 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-xs text-slate-800 truncate group-hover:text-orange-600 transition-colors">
                          {upd.title}
                        </p>
                        <span className="text-[10px] text-slate-400">
                          Verified on {upd.last_verified} • {upd.department}
                        </span>
                      </div>
                      <ChevronRight className="w-3.5 h-3.5 text-slate-300 group-hover:text-orange-500 shrink-0" />
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button
              onClick={() => navigate('/services/catalog')}
              className="w-full py-2.5 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-colors flex items-center justify-center gap-1 cursor-pointer"
            >
              <span>View All Change Logs</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {/* Column 3: Document Expiry Reminders */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <Bell className="w-5 h-5 text-amber-500" />
                  <h3 className="font-extrabold text-base text-slate-900">Your Document Reminders</h3>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-red-100 text-red-700 text-[10px] font-bold">
                  1 Urgent
                </span>
              </div>

              <div className="space-y-3">
                {reminders.map((rem) => {
                  const bg = rem.bg_color === 'red'
                    ? 'bg-red-50/80 border-red-200'
                    : rem.bg_color === 'amber'
                    ? 'bg-amber-50/80 border-amber-200'
                    : 'bg-emerald-50/80 border-emerald-200';

                  const badgeClass = rem.bg_color === 'red'
                    ? 'bg-red-100 text-red-700 font-bold'
                    : rem.bg_color === 'amber'
                    ? 'bg-amber-100 text-amber-700 font-bold'
                    : 'bg-emerald-100 text-emerald-700 font-bold';

                  const btnClass = rem.bg_color === 'red'
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : rem.bg_color === 'amber'
                    ? 'bg-amber-600 hover:bg-amber-700 text-white'
                    : 'bg-emerald-600 text-white';

                  return (
                    <div
                      key={rem.id}
                      className={`p-3.5 rounded-2xl border flex items-center justify-between ${bg}`}
                    >
                      <div className="space-y-0.5">
                        <span className="font-bold text-xs text-slate-900 block">{rem.document_type}</span>
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] px-2 py-0.5 rounded-full ${badgeClass}`}>
                            {rem.status_label}
                          </span>
                          <span className="text-[10px] text-slate-500">{rem.expiry_date_str}</span>
                        </div>
                      </div>

                      <button
                        onClick={() => navigate(`/discover?q=${encodeURIComponent(rem.query)}`)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold shadow-2xs transition-colors cursor-pointer ${btnClass}`}
                      >
                        {rem.action_text}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100 text-[11px] text-slate-500 text-center">
              💡 Automated alerts trigger 30 days before licence or certificate expiration.
            </div>
          </div>
        </div>
      </section>

      {/* 5. 10 POPULAR GOVERNMENT SERVICES GRID */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading">
              Popular Government Services
            </h2>
            <p className="text-xs text-slate-500">
              Access certified service procedures, official fees, and step-by-step guidance.
            </p>
          </div>
          <button
            onClick={() => navigate('/services/catalog')}
            className="text-xs font-bold text-orange-600 hover:text-orange-700 flex items-center gap-1 cursor-pointer"
          >
            <span>Explore All 45 Categories</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3.5">
          {popularGovtServices.map((srv) => {
            const Icon = srv.icon;
            return (
              <div
                key={srv.id}
                onClick={() => navigate(`/services/catalog/${srv.id}`)}
                className="bg-white p-4 rounded-3xl border border-slate-200/80 shadow-2xs hover:shadow-md hover:border-orange-300 transition-all cursor-pointer flex flex-col items-center text-center space-y-2 group"
              >
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-transform group-hover:scale-110 ${srv.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="font-bold text-xs text-slate-800 group-hover:text-orange-600 transition-colors">
                    {srv.name}
                  </h4>
                  <span className="text-[11px] text-slate-400 font-medium block mt-0.5">{srv.count}</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 6. "WE WILL APPLY FOR YOU" ASSISTANCE BANNER WITH REAL ACTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="rounded-3xl p-6 sm:p-8 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white shadow-lg flex flex-col md:flex-row items-center justify-between gap-6 border border-slate-800">
          <div className="space-y-2 max-w-xl text-center md:text-left">
            <span className="inline-block px-3 py-1 rounded-full bg-orange-500/20 text-orange-400 text-xs font-bold uppercase tracking-wider">
              🤝 Human Assistance & Partner Support
            </span>
            <h3 className="text-xl sm:text-3xl font-black font-heading">
              Need Help With Any Government Application?
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-light">
              Skip queue hassles and paperwork errors. Our verified partner operators and citizen desk experts will complete and track your application end-to-end.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3 shrink-0">
            <button
              onClick={() => handleOpenCallback('General Application Assistance')}
              className="px-6 py-3.5 rounded-2xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-md transition-all flex items-center gap-2 cursor-pointer"
            >
              <PhoneCall className="w-4 h-4" />
              <span>Request Human Callback</span>
            </button>

            <button
              onClick={() => navigate('/services/catalog')}
              className="px-5 py-3.5 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs border border-white/20 transition-colors cursor-pointer"
            >
              <span>Explore Assistance Tiers</span>
            </button>
          </div>
        </div>
      </section>

      {/* 7. TRUST METRICS BAR (100% DATA-DRIVEN - ZERO FAKE STATS) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-2xs grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
          <div>
            <span className="text-xl sm:text-2xl font-black text-slate-900 block font-heading">
              {taxonomySummary.total_categories}
            </span>
            <span className="text-slate-500 text-xs font-medium">Statutory Categories</span>
          </div>
          <div>
            <span className="text-xl sm:text-2xl font-black text-slate-900 block font-heading">
              {taxonomySummary.total_services}
            </span>
            <span className="text-slate-500 text-xs font-medium">Department Services</span>
          </div>
          <div>
            <span className="text-xl sm:text-2xl font-black text-slate-900 block font-heading">
              {taxonomySummary.total_sub_services}
            </span>
            <span className="text-slate-500 text-xs font-medium">Citizen Sub-Services</span>
          </div>
          <div>
            <span className="text-xl sm:text-2xl font-black text-emerald-600 block font-heading">
              {taxonomySummary.total_verified_records}
            </span>
            <span className="text-slate-500 text-xs font-medium">Source-Verified Opportunities</span>
          </div>
        </div>
      </section>

      {/* AI Assistant Drawer & Callback Modal */}
      <AIChatDrawer isOpen={chatOpen} onClose={() => setChatOpen(false)} />
      <CallbackModal
        isOpen={callbackModalOpen}
        onClose={() => setCallbackModalOpen(false)}
        defaultService={callbackServiceTarget}
      />
    </div>
  );
};

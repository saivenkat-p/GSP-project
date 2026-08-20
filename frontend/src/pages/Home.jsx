import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import {
  Search, Sparkles, ArrowRight, ShieldCheck, Landmark, CheckCircle2, Bot, Grid, FileText,
  UserCheck, HeartPulse, GraduationCap, Car, Vote, Wheat, Zap, Building2, HelpCircle,
  Bell, ChevronLeft, ChevronRight, Clock, Award, Users, PhoneCall, Check, ExternalLink, Calendar, RefreshCw, Compass
} from 'lucide-react';

export const Home = () => {
  const [query, setQuery] = useState('');
  const [heroBanners, setHeroBanners] = useState([]);
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [fade, setFade] = useState(true);
  const [loadingBanners, setLoadingBanners] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchBanners();
  }, []);

  useEffect(() => {
    if (heroBanners.length === 0) return;
    const interval = setInterval(() => {
      handleNextBanner();
    }, 6000);
    return () => clearInterval(interval);
  }, [carouselIndex, heroBanners]);

  const fetchBanners = async () => {
    try {
      setLoadingBanners(true);
      const res = await apiService.getHeroBanners();
      setHeroBanners(res.data || []);
    } catch (err) {
      console.error('Error loading dynamic opportunity banners:', err);
    } finally {
      setLoadingBanners(false);
    }
  };

  const handleNextBanner = () => {
    setFade(false);
    setTimeout(() => {
      setCarouselIndex((prev) => (prev + 1) % heroBanners.length);
      setFade(true);
    }, 250);
  };

  const handlePrevBanner = () => {
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

  const currentBanner = heroBanners[carouselIndex] || {
    category_tag: "🏛️ New Government Scheme",
    title: "Dynamic Citizen Opportunity Banner",
    subtitle: "Continuously updated scheme and scholarship information sourced from the verified freshness engine.",
    benefit_amount: "Verified Opportunity",
    tag1: "Data-Driven Engine",
    tag2: "100% Official Sources",
    deadline: "31 Aug 2026",
    verification_badge: "🟢 Government Verified",
    action_query: "government schemes and benefits",
    official_source_url: "https://ap.meeseva.gov.in",
    last_verified: "2026-08-20",
    color_theme: "emerald"
  };

  const currentSchemes = [
    {
      id: 1,
      title: "Student Scholarship 2026",
      desc: "Up to ₹25,000 per year for eligible students. Check your eligibility and apply now.",
      deadline: "30 Sep 2026",
      tag: "Apply Now",
      bgClass: "bg-emerald-50/80 border-emerald-200 text-emerald-950",
      query: "student scholarship"
    },
    {
      id: 2,
      title: "YSR Aarogyasri Health Care",
      desc: "Cashless treatment up to ₹25 Lakhs for eligible families in empanelled hospitals.",
      deadline: "31 Aug 2026",
      tag: "Apply Now",
      bgClass: "bg-purple-50/80 border-purple-200 text-purple-950",
      query: "aarogyasri health card"
    },
    {
      id: 3,
      title: "Housing for All (PMAY)",
      desc: "Get financial assistance for building your dream home under urban & rural housing.",
      deadline: "15 Oct 2026",
      tag: "Apply Now",
      bgClass: "bg-amber-50/80 border-amber-200 text-amber-950",
      query: "housing pmay patta"
    },
    {
      id: 4,
      title: "Annadata Sukhibhava",
      desc: "Financial assistance to farmers. Direct benefit transfer to your bank account.",
      deadline: "31 Aug 2026",
      tag: "Apply Now",
      bgClass: "bg-blue-50/80 border-blue-200 text-blue-950",
      query: "annadata farmer assistance"
    }
  ];

  const scholarshipsList = [
    { name: "LIC Golden Jubilee Scholarship", target: "For Class 10 & 12 Students", badge: "Apply Now", link: "/discover?q=lic+scholarship" },
    { name: "TCS Ignite Scholarship", target: "Engineering Students", badge: "Apply Now", link: "/discover?q=tcs+scholarship" },
    { name: "Reliance Foundation Scholarship", target: "Undergraduate Students", badge: "Apply Now", link: "/discover?q=reliance+scholarship" },
    { name: "Central Sector Scholarship", target: "UG/PG/PhD Students", badge: "Apply Now", link: "/discover?q=central+sector+scholarship" }
  ];

  const todaysUpdates = [
    { title: "New Scheme Launched: AP Yuva Vikasam", time: "2 hours ago" },
    { title: "Birth Certificate procedure updated", time: "4 hours ago" },
    { title: "Driving Licence rule changes effective", time: "6 hours ago" },
    { title: "Scholarship deadline extended", time: "8 hours ago" },
    { title: "New MeeSeva service added", time: "10 hours ago" }
  ];

  const userReminders = [
    {
      type: "Driving Licence",
      status: "Expires in 24 Days",
      date: "Expiry Date: 12 Sep 2026",
      action: "Renew Now",
      bg: "bg-red-50/80 border-red-200",
      badgeClass: "bg-red-100 text-red-700 font-bold",
      btnClass: "bg-red-600 hover:bg-red-700 text-white"
    },
    {
      type: "Aadhaar Update",
      status: "Review Suggested",
      date: "Update your documents",
      action: "Review Now",
      bg: "bg-amber-50/80 border-amber-200",
      badgeClass: "bg-amber-100 text-amber-700 font-bold",
      btnClass: "bg-amber-600 hover:bg-amber-700 text-white"
    },
    {
      type: "PAN Card",
      status: "No Action Required",
      date: "Valid til: 31 Dec 2030",
      action: "✓ Valid",
      bg: "bg-emerald-50/80 border-emerald-200",
      badgeClass: "bg-emerald-100 text-emerald-700 font-bold",
      btnClass: "bg-emerald-600 text-white"
    }
  ];

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
      {/* 1. DYNAMIC GOVERNMENT OPPORTUNITY HERO BANNER (DATA-DRIVEN ROTATION / FADE) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="relative rounded-3xl p-6 sm:p-10 bg-gradient-to-r from-amber-50 via-emerald-50 to-indigo-50 border border-slate-200/80 shadow-md overflow-hidden">
          {/* Carousel Arrows */}
          <button
            onClick={handlePrevBanner}
            className="absolute left-3 top-1/2 -translate-y-1/2 z-10 w-9 h-9 rounded-full bg-white/90 shadow-md border border-slate-200 text-slate-700 flex items-center justify-center hover:bg-white transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <button
            onClick={handleNextBanner}
            className="absolute right-3 top-1/2 -translate-y-1/2 z-10 w-9 h-9 rounded-full bg-white/90 shadow-md border border-slate-200 text-slate-700 flex items-center justify-center hover:bg-white transition-colors"
          >
            <ChevronRight className="w-5 h-5" />
          </button>

          {/* Banner Body with Fade Transition */}
          <div className={`transition-opacity duration-300 flex flex-col lg:flex-row items-center justify-between gap-8 ${fade ? 'opacity-100' : 'opacity-0'}`}>
            {/* Left Content */}
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
                  onClick={() => navigate(`/discover?q=${encodeURIComponent(currentBanner.action_query)}`)}
                  className="px-8 py-3.5 rounded-2xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-md transition-all flex items-center gap-2"
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

            {/* Right Highlights & Verified Metric Cards */}
            <div className="flex flex-wrap lg:flex-col gap-3 shrink-0">
              <div className="p-4 rounded-2xl bg-white/90 border border-slate-200/80 shadow-xs flex items-center gap-3 text-xs">
                <div className="w-10 h-10 rounded-xl bg-orange-100 text-orange-700 flex items-center justify-center font-bold">
                  ₹
                </div>
                <div>
                  <span className="font-bold text-slate-900 block">{currentBanner.benefit_amount}</span>
                  <span className="text-slate-500 text-[11px]">Direct Citizen Benefit</span>
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

        {/* Dynamic Pagination Dots Indicator (● ○ ○ ○ ○) */}
        <div className="flex items-center justify-center gap-2 pt-3">
          {(heroBanners.length > 0 ? heroBanners : [1]).map((_, idx) => (
            <button
              key={idx}
              onClick={() => {
                setFade(false);
                setTimeout(() => {
                  setCarouselIndex(idx);
                  setFade(true);
                }, 200);
              }}
              className={`h-2.5 rounded-full transition-all ${carouselIndex === idx ? 'bg-orange-500 w-6' : 'bg-slate-300 w-2.5'}`}
            />
          ))}
        </div>
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
              placeholder="What service or scheme are you looking for today? Search services, schemes, certificates, scholarships and more..."
              className="w-full bg-transparent text-slate-800 placeholder-slate-400 text-xs sm:text-sm focus:outline-none"
            />
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto shrink-0">
            <button
              type="submit"
              className="w-full sm:w-auto px-8 py-3 rounded-2xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-sm transition-colors flex items-center justify-center gap-2"
            >
              <Search className="w-4 h-4" />
              <span>Search</span>
            </button>

            <button
              type="button"
              onClick={() => navigate('/discover?q=ai+assistant')}
              className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-amber-50 hover:bg-amber-100 border border-amber-200 text-amber-800 font-bold text-xs transition-colors flex items-center justify-center gap-2 shrink-0"
            >
              <Sparkles className="w-4 h-4 text-amber-600" />
              <span>Ask GSP AI</span>
            </button>
          </div>
        </form>
      </section>

      {/* 3. 🔥 CURRENT GOVERNMENT SCHEMES CAROUSEL */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-900 font-heading flex items-center gap-2">
            <span>🔥 Current Government Schemes</span>
          </h2>
          <Link to="/services/catalog" className="text-xs font-bold text-orange-600 hover:underline flex items-center gap-1">
            <span>View All</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {currentSchemes.map((sch) => (
            <div key={sch.id} className={`relative p-5 rounded-3xl border ${sch.bgClass} shadow-xs space-y-4 flex flex-col justify-between overflow-hidden group hover:shadow-md transition-all`}>
              <div className="absolute -right-8 top-4 rotate-45 bg-orange-500 text-white text-[10px] font-extrabold px-8 py-0.5 shadow-xs uppercase tracking-wider">
                {sch.tag}
              </div>

              <div className="space-y-3">
                <div className="w-10 h-10 rounded-2xl bg-white/80 shadow-xs flex items-center justify-center font-bold text-slate-800">
                  <Award className="w-5 h-5 text-orange-500" />
                </div>

                <h3 className="text-base font-bold text-slate-900 font-heading leading-snug">{sch.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed font-sans">{sch.desc}</p>
              </div>

              <div className="pt-3 border-t border-slate-200/60 space-y-3">
                <div className="text-[11px] font-bold text-slate-500">
                  Deadline: <span className="text-slate-900">{sch.deadline}</span>
                </div>

                <button
                  onClick={() => navigate(`/discover?q=${encodeURIComponent(sch.query)}`)}
                  className="w-full py-2.5 rounded-xl bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 font-bold text-xs shadow-xs transition-colors"
                >
                  Check Eligibility
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. 3-COLUMN DASHBOARD GRID */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Column 1: 🎓 Scholarships & Opportunities */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="text-base font-bold text-slate-900 font-heading flex items-center gap-2">
                  <GraduationCap className="w-5 h-5 text-orange-500" />
                  <span>Scholarships & Opportunities</span>
                </h3>
                <Link to="/services/catalog" className="text-xs font-bold text-orange-600 hover:underline">View All</Link>
              </div>

              <div className="space-y-3">
                {scholarshipsList.map((sch, idx) => (
                  <div key={idx} className="p-3 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-between gap-3 text-xs">
                    <div>
                      <h4 className="font-bold text-slate-900">{sch.name}</h4>
                      <p className="text-[11px] text-slate-500">{sch.target}</p>
                    </div>
                    <Link
                      to={sch.link}
                      className="px-3 py-1 rounded-full bg-emerald-100 hover:bg-emerald-200 text-emerald-800 font-bold text-[11px] shrink-0 transition-colors"
                    >
                      {sch.badge}
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Column 2: 📰 Today's Updates */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="text-base font-bold text-slate-900 font-heading flex items-center gap-2">
                  <Bell className="w-5 h-5 text-sky-500" />
                  <span>Today's Updates</span>
                </h3>
                <Link to="/services/catalog" className="text-xs font-bold text-orange-600 hover:underline">View All</Link>
              </div>

              <div className="space-y-3">
                {todaysUpdates.map((upd, idx) => (
                  <div key={idx} className="p-3 rounded-2xl bg-slate-50 border border-slate-100 flex items-start gap-3 text-xs">
                    <div className="w-7 h-7 rounded-xl bg-orange-100 text-orange-600 flex items-center justify-center font-bold shrink-0 mt-0.5">
                      <Bell className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-900 leading-snug">{upd.title}</h4>
                      <span className="text-[10px] text-slate-400 block mt-0.5">{upd.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Column 3: ⏰ Your Reminders */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="text-base font-bold text-slate-900 font-heading flex items-center gap-2">
                  <Clock className="w-5 h-5 text-red-500" />
                  <span>Your Reminders</span>
                </h3>
                <Link to="/dashboard" className="text-xs font-bold text-orange-600 hover:underline">View All</Link>
              </div>

              <div className="space-y-3">
                {userReminders.map((rem, idx) => (
                  <div key={idx} className={`p-4 rounded-2xl border ${rem.bg} space-y-2 text-xs`}>
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{rem.type}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full ${rem.badgeClass}`}>{rem.status}</span>
                    </div>

                    <p className="text-[11px] text-slate-500">{rem.date}</p>

                    <button
                      onClick={() => navigate(`/discover?q=${encodeURIComponent(rem.type)}`)}
                      className={`w-full py-1.5 rounded-xl font-bold text-xs transition-colors ${rem.btnClass}`}
                    >
                      {rem.action}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. POPULAR SERVICES GRID + WE WILL APPLY FOR YOU BANNER */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white p-6 rounded-3xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900 font-heading flex items-center gap-2">
                <Landmark className="w-5 h-5 text-orange-500" />
                <span>Popular Government Services</span>
              </h3>
              <Link to="/services/catalog" className="text-xs font-bold text-orange-600 hover:underline">View All Services</Link>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
              {popularGovtServices.map((srv) => {
                const Icon = srv.icon;
                return (
                  <Link
                    key={srv.id}
                    to={`/services/catalog/${srv.id}`}
                    className="p-4 rounded-2xl bg-slate-50 border border-slate-100 hover:border-orange-300 text-center space-y-2 transition-all hover:bg-orange-50/50 group"
                  >
                    <div className={`w-10 h-10 rounded-2xl mx-auto flex items-center justify-center font-bold ${srv.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>

                    <div>
                      <h4 className="text-xs font-bold text-slate-900 group-hover:text-orange-600 transition-colors font-heading leading-tight">
                        {srv.name}
                      </h4>
                      <span className="text-[10px] text-slate-400 block mt-0.5">{srv.count}</span>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>

          <div className="bg-gradient-to-br from-amber-50 via-orange-50 to-orange-100 p-6 rounded-3xl border border-orange-200 shadow-xs space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-500 text-white font-bold text-xs shadow-xs">
                <span>🤝 We Will Apply For You</span>
              </div>

              <h3 className="text-base font-bold text-slate-900 font-heading leading-snug">Don't know how to apply?</h3>
              <p className="text-xs text-slate-600 leading-relaxed font-sans">
                Our experts will help you with end-to-end application support.
              </p>

              <div className="space-y-2 pt-2 text-xs font-bold text-slate-800">
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Document Preparation</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Form Filling</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Submission Guidance</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Status Tracking</span>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-orange-200/80">
              <button
                onClick={() => navigate('/services/catalog')}
                className="w-full py-3 rounded-2xl bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 text-white font-bold text-xs shadow-sm transition-colors"
              >
                Get Assistance Now
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 6. TRUSTED BY CITIZENS METRICS BAR */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs grid grid-cols-2 sm:grid-cols-5 gap-4 text-center">
          <div className="space-y-1">
            <span className="text-xs text-slate-400 font-bold block uppercase tracking-wider">Trusted Citizens</span>
            <span className="text-xl font-black text-slate-900 font-heading">10L+</span>
            <span className="text-[10px] text-emerald-600 block font-semibold">Happy Citizens</span>
          </div>

          <div className="space-y-1">
            <span className="text-xs text-slate-400 font-bold block uppercase tracking-wider">Categories</span>
            <span className="text-xl font-black text-slate-900 font-heading">45+</span>
            <span className="text-[10px] text-slate-500 block font-semibold">Master Categories</span>
          </div>

          <div className="space-y-1">
            <span className="text-xs text-slate-400 font-bold block uppercase tracking-wider">Services</span>
            <span className="text-xl font-black text-slate-900 font-heading">500+</span>
            <span className="text-[10px] text-slate-500 block font-semibold">Government Services</span>
          </div>

          <div className="space-y-1">
            <span className="text-xs text-slate-400 font-bold block uppercase tracking-wider">Success Rate</span>
            <span className="text-xl font-black text-slate-900 font-heading">98%</span>
            <span className="text-[10px] text-emerald-600 block font-semibold">Success Rate</span>
          </div>

          <div className="space-y-1 col-span-2 sm:col-span-1">
            <span className="text-xs text-slate-400 font-bold block uppercase tracking-wider">Support</span>
            <span className="text-xl font-black text-slate-900 font-heading">24/7</span>
            <span className="text-[10px] text-orange-600 block font-semibold">Support Available</span>
          </div>
        </div>
      </section>
    </div>
  );
};

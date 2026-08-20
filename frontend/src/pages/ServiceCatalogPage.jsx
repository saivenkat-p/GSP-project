import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, Link, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { SourceBadge } from '../components/SourceBadge';
import { Search, Landmark, ArrowRight, ShieldCheck, CheckCircle2, Bot, Filter, Compass, Grid, Sparkles, MapPin, UserCheck, FileText, HeartPulse, GraduationCap, Car, Vote, Wheat, Zap, Building2 } from 'lucide-react';

export const ServiceCatalogPage = () => {
  const { serviceId } = useParams();
  const [searchParams] = useSearchParams();
  const categoryParam = searchParams.get('category') || 'All';

  const [allServices, setAllServices] = useState([]);
  const [singleCatalog, setSingleCatalog] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState(categoryParam);
  const [intentFilter, setIntentFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    if (serviceId) {
      fetchSingleCatalog(serviceId, searchQuery);
    } else {
      fetchAllServices(activeCategory, searchQuery);
    }
  }, [serviceId, activeCategory]);

  const fetchAllServices = async (cat, q) => {
    try {
      setLoading(true);
      const res = await apiService.getServices(cat, 'AP', q);
      setAllServices(res.data);
    } catch (err) {
      console.error('Error loading all services catalog:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSingleCatalog = async (id, q) => {
    try {
      setLoading(true);
      const res = await apiService.getServiceCatalog(id, q);
      setSingleCatalog(res.data);
    } catch (err) {
      console.error('Error loading single catalog:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCatalogSearchSubmit = (e) => {
    e.preventDefault();
    if (serviceId) {
      fetchSingleCatalog(serviceId, searchQuery);
    } else {
      if (searchQuery.trim()) {
        navigate(`/discover?q=${encodeURIComponent(searchQuery)}`);
      } else {
        fetchAllServices(activeCategory, '');
      }
    }
  };

  const masterCategoriesList = [
    'All',
    'Identity & Citizen Documents',
    'Birth & Death Services',
    'Revenue & Certificates',
    'Land & Property',
    'Registration & Stamps',
    'Driving Licence & Transport',
    'Ration Card & Civil Supplies',
    'Welfare Schemes & Social Security',
    'Health Services',
    'Education',
    'Voter Services',
    'Passport & Consular',
    'Agriculture',
    'Municipal Services',
    'Electricity & Water'
  ];

  const intentFilterButtons = [
    { label: 'ALL', value: 'ALL' },
    { label: 'Address Change / Transfer', value: 'address' },
    { label: 'Name Correction', value: 'correction' },
    { label: 'Duplicate / Lost Card', value: 'duplicate' },
    { label: 'New Application', value: 'new' },
    { label: 'Download / Search', value: 'download' }
  ];

  // LEVEL 2 / LEVEL 3: SINGLE PARENT SERVICE VIEW (e.g. Birth Certificate or Aadhaar)
  if (serviceId && singleCatalog) {
    const subServicesToDisplay = singleCatalog.sub_services?.filter((sub) => {
      if (intentFilter === 'ALL') return true;
      return (
        sub.action_type.toLowerCase().includes(intentFilter.toLowerCase()) ||
        sub.sub_service_name.toLowerCase().includes(intentFilter.toLowerCase()) ||
        anyMatchesAlias(sub.aliases, intentFilter)
      );
    }) || [];

    return (
      <div className="max-w-5xl mx-auto space-y-8 pb-20">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-xs text-slate-400 font-medium">
          <Link to="/services/catalog" className="hover:text-saffron-400">All Services</Link>
          <span>/</span>
          <span className="text-slate-200">{singleCatalog.category}</span>
          <span>/</span>
          <span className="text-saffron-400 font-semibold">{singleCatalog.official_name}</span>
        </div>

        {/* Parent Service Header */}
        <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs font-bold uppercase tracking-wider text-saffron-400 bg-saffron-500/10 px-3 py-1 rounded-full border border-saffron-500/20">
              {singleCatalog.category}
            </span>
            <SourceBadge status="VERIFIED" lastVerified="2026-08-20" />
          </div>

          <div>
            <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">{singleCatalog.official_name}</h1>
            <p className="text-xs sm:text-sm text-slate-300 mt-1">{singleCatalog.department}</p>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed font-sans">{singleCatalog.description}</p>
        </div>

        {/* Mode A — IN-CATEGORY SEARCH BAR */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-800 space-y-4">
          <form onSubmit={handleCatalogSearchSubmit} className="flex items-center gap-2">
            <div className="flex items-center gap-3 px-4 py-2.5 bg-slate-950 rounded-xl border border-slate-800 w-full text-xs">
              <Search className="w-4 h-4 text-saffron-400 shrink-0" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  fetchSingleCatalog(serviceId, e.target.value);
                }}
                placeholder={`Search within ${singleCatalog.official_name} (e.g. 'father', 'mother', 'child', 'address')...`}
                className="w-full bg-transparent text-slate-100 placeholder-slate-500 focus:outline-none"
              />
            </div>
            <button type="submit" className="px-6 py-2.5 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-bold text-xs shrink-0">
              Search Service
            </button>
          </form>
        </div>

        {/* Available Sub-Services Grid */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
            Available Options ({subServicesToDisplay.length})
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {subServicesToDisplay.map((sub) => (
              <div key={sub.id} className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      {sub.action_type}
                    </span>
                    <span className="text-[11px] font-bold text-saffron-400">Govt Fee: ₹{sub.official_fee}</span>
                  </div>
                  <h4 className="text-base font-bold text-white font-heading">{sub.sub_service_name}</h4>
                  <p className="text-xs text-slate-400">Processing Time: {sub.processing_time} • Method: {sub.application_method}</p>
                </div>

                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                  <span className="text-[11px] text-amber-400 font-medium">
                    Physical Presence: {sub.physical_presence_requirement}
                  </span>
                  <Link
                    to={`/services/${sub.id}`}
                    className="px-4 py-2 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-bold text-xs flex items-center gap-1 transition-colors"
                  >
                    <span>View Options</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // LEVEL 1: ALL SERVICES & MASTER CATEGORIES CATALOGUE OVERVIEW
  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-24">
      {/* Header Banner */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-4 text-center sm:text-left">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-saffron-500/10 border border-saffron-500/30 text-saffron-400 text-xs font-semibold mx-auto sm:mx-0">
            <Grid className="w-4 h-4" />
            <span>Master 45-Category Service Catalogue</span>
          </div>
          <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1 mx-auto sm:mx-0">
            <MapPin className="w-3.5 h-3.5" />
            <span>Services available for your location + National services</span>
          </span>
        </div>

        <div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">Government Services Catalogue</h1>
          <p className="text-xs sm:text-sm text-slate-300 mt-1">
            Browse services by statutory category or search by your intention.
          </p>
        </div>

        {/* Global Catalog Search Box */}
        <form onSubmit={handleCatalogSearchSubmit} className="pt-2">
          <div className="glass-panel p-2 rounded-2xl border border-slate-700 shadow-xl flex items-center gap-2 max-w-2xl">
            <Search className="w-5 h-5 text-saffron-400 ml-3 shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search all services (e.g. 'aadhaar', 'voter card', 'birth certificate')..."
              className="w-full bg-transparent text-slate-100 placeholder-slate-400 text-sm focus:outline-none py-2"
            />
            <button type="submit" className="px-6 py-2.5 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-bold text-xs shrink-0">
              Search Catalogue
            </button>
          </div>
        </form>

        {/* Intent Quick Filters */}
        <div className="pt-2 flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-400 font-bold uppercase text-[10px]">What are you trying to do?</span>
          {intentFilterButtons.map((btn) => (
            <button
              key={btn.value}
              onClick={() => setIntentFilter(btn.value)}
              className={`px-3 py-1 rounded-full text-[11px] font-semibold transition-colors ${
                intentFilter === btn.value
                  ? 'bg-saffron-500 text-white shadow'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {btn.label}
            </button>
          ))}
        </div>
      </div>

      {/* Categories Filter Bar */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 text-xs no-scrollbar">
        {masterCategoriesList.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-4 py-2 rounded-xl whitespace-nowrap font-bold transition-all shrink-0 ${
              activeCategory === cat
                ? 'bg-saffron-500 text-white shadow-lg'
                : 'bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Services Grid (Level 2) */}
      <div className="space-y-6">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
          Services in {activeCategory} ({allServices.length})
        </h3>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-pulse">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-56 bg-slate-900 rounded-3xl border border-slate-800" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {allServices.map((srv) => (
              <div key={srv.id} className="glass-card p-6 rounded-3xl border border-slate-800 space-y-4 flex flex-col justify-between">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase text-saffron-400 bg-saffron-500/10 px-2.5 py-0.5 rounded border border-saffron-500/20">
                      {srv.category}
                    </span>
                    <SourceBadge status={srv.verification_status} lastVerified={srv.last_verified} />
                  </div>
                  <h3 className="text-xl font-bold text-white font-heading">{srv.official_name}</h3>
                  <p className="text-xs text-slate-400">{srv.department}</p>
                </div>

                <div className="pt-3 border-t border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold text-slate-300 uppercase">Available Sub-Options ({srv.sub_services?.length || 0}):</span>
                    <Link
                      to={`/services/catalog/${srv.id}`}
                      className="text-xs font-bold text-saffron-400 hover:underline flex items-center gap-1"
                    >
                      <span>Open Catalogue</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>

                  <div className="space-y-1.5">
                    {srv.sub_services?.slice(0, 3).map((sub) => (
                      <Link
                        key={sub.id}
                        to={`/services/${sub.id}`}
                        className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 flex items-center justify-between text-xs text-slate-200 block transition-colors"
                      >
                        <span className="font-semibold">{sub.sub_service_name}</span>
                        <ArrowRight className="w-3 h-3 text-saffron-400" />
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

function anyMatchesAlias(aliases, term) {
  if (!aliases) return false;
  return aliases.some((a) => a.toLowerCase().includes(term.toLowerCase()));
}

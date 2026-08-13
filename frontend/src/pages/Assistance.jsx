import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { PartnerCard } from '../components/PartnerCard';
import { ShieldCheck, MapPin, Filter, Search } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export const Assistance = () => {
  const { selectedDistrict } = useAuth();
  const [partners, setPartners] = useState([]);
  const [services, setServices] = useState([]);
  const [selectedService, setSelectedService] = useState('All');
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    fetchMarketplaceData();
  }, [selectedDistrict, selectedService]);

  const fetchMarketplaceData = async () => {
    try {
      setLoading(true);
      const srvId = selectedService === 'All' ? null : selectedService;
      const [prtRes, srvRes] = await Promise.all([
        apiService.getPartners(selectedDistrict, srvId),
        apiService.getServices('All', 'Andhra Pradesh'),
      ]);
      setPartners(prtRes.data);
      setServices(srvRes.data);
    } catch (err) {
      console.error('Error fetching partner marketplace:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePartnerRequest = async (partner) => {
    try {
      const defaultSrv = partner.supported_service_ids[0] || 'ap-income-certificate';
      await apiService.createRequest(defaultSrv, partner.id, `Assistance requested from center ${partner.business_name}`);
      navigate('/dashboard');
    } catch (err) {
      console.error('Request creation error:', err);
      navigate('/login');
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20">
      {/* Header */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
          <ShieldCheck className="w-4 h-4" />
          <span>Verified Citizen Assistance Marketplace</span>
        </div>

        <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">
          Nearby Verified Service Centers
        </h1>
        <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
          Authorized MeeSeva centers, CSC Kendra operators, and verified digital facilitators. Vetted for security, credentials, transparent pricing, and quality service.
        </p>

        {/* Filter bar */}
        <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-800">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <MapPin className="w-4 h-4 text-saffron-400" />
            <span>Active District: <strong className="text-white">{selectedDistrict}</strong></span>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-500" />
            <select
              value={selectedService}
              onChange={(e) => setSelectedService(e.target.value)}
              className="bg-slate-900 text-xs text-slate-200 border border-slate-800 rounded-xl px-3 py-2 focus:outline-none w-full sm:w-auto"
            >
              <option value="All">Filter by Service: All</option>
              {services.map((s) => (
                <option key={s.id} value={s.id}>{s.official_name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Grid of Verified Partners */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[1, 2].map((i) => (
            <div key={i} className="h-64 bg-slate-900 rounded-2xl border border-slate-800" />
          ))}
        </div>
      ) : partners.length === 0 ? (
        <div className="p-12 text-center bg-slate-900 rounded-3xl border border-slate-800 text-slate-400 text-xs space-y-2">
          <p className="text-slate-300 font-semibold">No verified partners found matching this filter.</p>
          <p>You can complete any service directly using our step-by-step DIY guide!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {partners.map((p) => (
            <PartnerCard key={p.id} partner={p} onSelect={() => handlePartnerRequest(p)} />
          ))}
        </div>
      )}
    </div>
  );
};

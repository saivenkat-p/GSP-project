import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { UserCheck, ShieldCheck, Landmark, FileText, CheckCircle2, XCircle, RefreshCw } from 'lucide-react';

export const AdminDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [partners, setPartners] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      const [metRes, prtRes] = await Promise.all([
        apiService.getAdminMetrics(),
        apiService.getAdminPartners(),
      ]);
      setMetrics(metRes.data);
      setPartners(prtRes.data);
    } catch (err) {
      console.error('Error fetching admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyToggle = async (partnerId, currentStatus) => {
    const nextStatus = currentStatus === 'verified' ? 'rejected' : 'verified';
    try {
      await apiService.verifyPartner(partnerId, nextStatus);
      fetchAdminData();
    } catch (err) {
      console.error('Error verifying partner:', err);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20">
      {/* Header */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold">
          <UserCheck className="w-4 h-4" />
          <span>System Administration & Audit Operations</span>
        </div>

        <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">
          Platform Governance Dashboard
        </h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Monitor verified government service catalog, partner verification queue, and official source audit timestamps.
        </p>

        {/* Metrics Overview */}
        {metrics && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-800 text-xs">
            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block uppercase font-semibold text-[10px]">Verified Services</span>
              <span className="text-emerald-400 font-bold text-xl">{metrics.verified_services} Services</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block uppercase font-semibold text-[10px]">Total Users</span>
              <span className="text-saffron-400 font-bold text-xl">{metrics.total_users} Users</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block uppercase font-semibold text-[10px]">Partner Centers</span>
              <span className="text-sky-400 font-bold text-xl">{metrics.total_partners} Centers</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block uppercase font-semibold text-[10px]">Last Official Audit</span>
              <span className="text-slate-200 font-mono font-bold text-xs">{metrics.last_source_audit}</span>
            </div>
          </div>
        )}
      </div>

      {/* Partner Verification Queue */}
      <div className="space-y-6">
        <h2 className="text-xl font-bold text-white font-heading flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-indigo-400" />
          <span>Partner Center Verification & Compliance Queue</span>
        </h2>

        {loading ? (
          <div className="h-48 bg-slate-900 rounded-3xl animate-pulse border border-slate-800" />
        ) : (
          <div className="space-y-3">
            {partners.map((partner) => (
              <div key={partner.id} className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-white">{partner.business_name}</span>
                    <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${partner.verification_status === 'verified' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                      {partner.verification_status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{partner.center_type} • {partner.address}</p>
                </div>

                <button
                  onClick={() => handleVerifyToggle(partner.id, partner.verification_status)}
                  className={`px-4 py-2 rounded-xl font-bold text-xs transition-colors flex items-center gap-1.5 ${partner.verification_status === 'verified' ? 'bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-emerald-500 hover:bg-emerald-600 text-slate-950'}`}
                >
                  {partner.verification_status === 'verified' ? (
                    <>
                      <XCircle className="w-4 h-4" />
                      <span>Revoke Verification</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Approve Verification</span>
                    </>
                  )}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

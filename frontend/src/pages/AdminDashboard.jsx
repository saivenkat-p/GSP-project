import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { UserCheck, ShieldCheck, Landmark, Clock, AlertTriangle, CheckCircle2, XCircle, RefreshCw } from 'lucide-react';

export const AdminDashboard = () => {
  const [healthMetrics, setHealthMetrics] = useState(null);
  const [changeQueue, setChangeQueue] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      const [metRes, queueRes] = await Promise.all([
        apiService.getFreshnessMetrics(),
        apiService.getFreshnessQueue(),
      ]);
      setHealthMetrics(metRes.data);
      setChangeQueue(queueRes.data);
    } catch (err) {
      console.error('Error fetching admin health data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveChange = async (changeId) => {
    try {
      await apiService.approveSourceChange(changeId);
      fetchAdminData();
    } catch (err) {
      console.error('Error approving source version update:', err);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20">
      {/* Header */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold">
          <UserCheck className="w-4 h-4" />
          <span>GSP Information Intelligence & Health Governance</span>
        </div>

        <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">
          Government Information Health Dashboard
        </h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Monitor source freshness, verify detected government rule changes, and approve version snapshots before they become active.
        </p>

        {/* 🟢 🟡 🔴 Information Health Metrics Grid */}
        {healthMetrics && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-800 text-xs">
            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30">
              <span className="text-emerald-400 font-bold block uppercase text-[10px]">🟢 Verified Records</span>
              <span className="text-emerald-300 font-bold text-2xl mt-1 block">{healthMetrics.verified_count} / {healthMetrics.total_services}</span>
            </div>

            <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30">
              <span className="text-amber-400 font-bold block uppercase text-[10px]">🟡 Verification Pending</span>
              <span className="text-amber-300 font-bold text-2xl mt-1 block">{healthMetrics.pending_count}</span>
            </div>

            <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30">
              <span className="text-red-400 font-bold block uppercase text-[10px]">🔴 Outdated Records</span>
              <span className="text-red-300 font-bold text-2xl mt-1 block">{healthMetrics.outdated_count}</span>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block uppercase font-semibold text-[10px]">Last Source Audit</span>
              <span className="text-slate-200 font-mono font-bold text-xs mt-1 block">{healthMetrics.last_source_audit}</span>
            </div>
          </div>
        )}
      </div>

      {/* Source Change Detection Review Queue */}
      <div className="space-y-6">
        <h2 className="text-xl font-bold text-white font-heading flex items-center gap-2">
          <Clock className="w-5 h-5 text-amber-400" />
          <span>Detected Source Change Verification Queue</span>
        </h2>

        {loading ? (
          <div className="h-48 bg-slate-900 rounded-3xl animate-pulse border border-slate-800" />
        ) : changeQueue.length === 0 ? (
          <div className="p-12 text-center bg-slate-900 rounded-3xl border border-slate-800 text-slate-400 text-xs">
            No pending source updates requiring approval right now. All active records are 🟢 VERIFIED.
          </div>
        ) : (
          <div className="space-y-4">
            {changeQueue.map((item) => (
              <div key={item.id} className="glass-panel p-6 rounded-2xl border border-amber-500/30 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-amber-400 uppercase tracking-wide">
                    Change Item #{item.id} • Sub-Service: {item.sub_service_id}
                  </span>
                  <a href={item.source_url} target="_blank" rel="noreferrer" className="text-xs text-saffron-400 hover:underline">
                    View Source URL
                  </a>
                </div>

                <p className="text-xs text-slate-200 font-medium">{item.detected_change_summary}</p>

                <div className="flex justify-end gap-2 pt-2 text-xs">
                  <button
                    onClick={() => handleApproveChange(item.id)}
                    className="px-4 py-2 rounded-xl bg-emerald-500 text-slate-950 font-bold hover:bg-emerald-600 flex items-center gap-1.5"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Approve Update & Increment Version</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

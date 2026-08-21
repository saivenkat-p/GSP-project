import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  UserCheck, ShieldCheck, Landmark, Clock, AlertTriangle,
  CheckCircle2, XCircle, RefreshCw, Layers, Database, ExternalLink
} from 'lucide-react';

export const AdminDashboard = () => {
  const [healthMetrics, setHealthMetrics] = useState(null);
  const [changeQueue, setChangeQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);

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
      setChangeQueue(queueRes.data || []);
    } catch (err) {
      console.error('Error fetching admin health data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveChange = async (changeId) => {
    try {
      setActionLoading(changeId);
      await apiService.approveSourceChange(changeId, 'Verified against official state/central government gazette');
      await fetchAdminData();
    } catch (err) {
      console.error('Error approving source version update:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleRejectChange = async (changeId) => {
    try {
      setActionLoading(changeId);
      await apiService.rejectSourceChange(changeId, 'Rejected: Could not verify against official portal gazette');
      await fetchAdminData();
    } catch (err) {
      console.error('Error rejecting source change:', err);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20 px-4 sm:px-6">
      {/* Header */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold">
          <ShieldCheck className="w-4 h-4 text-indigo-600" />
          <span>GSP V3 Information Health & Trust Governance</span>
        </div>

        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-heading">
          Government Information Health Dashboard
        </h1>
        <p className="text-xs sm:text-sm text-slate-600">
          Continuous monitoring across registered Tier 1–4 sources, automated change detection diffs, version history snapshots, and admin verification governance.
        </p>

        {/* Health Metrics Grid */}
        {healthMetrics && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-100 text-xs">
            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200">
              <span className="text-emerald-700 font-bold block uppercase text-[10px]">🟢 Verified Records</span>
              <span className="text-emerald-900 font-bold text-2xl mt-1 block">
                {(healthMetrics.information_records?.verified || 0) + (healthMetrics.services?.verified || 0)} / {(healthMetrics.information_records?.total || 0) + (healthMetrics.services?.total || 0)}
              </span>
              <span className="text-[11px] text-emerald-600 mt-1 block">
                {healthMetrics.information_records?.verified || 0} Schemes • {healthMetrics.services?.verified || 0} Services
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200">
              <span className="text-amber-700 font-bold block uppercase text-[10px]">🟡 Verification Pending</span>
              <span className="text-amber-900 font-bold text-2xl mt-1 block">
                {(healthMetrics.information_records?.pending || 0) + (healthMetrics.services?.pending || 0)}
              </span>
              <span className="text-[11px] text-amber-600 mt-1 block">Requires manual audit</span>
            </div>

            <div className="p-4 rounded-2xl bg-red-50 border border-red-200">
              <span className="text-red-700 font-bold block uppercase text-[10px]">🔴 Outdated Records</span>
              <span className="text-red-900 font-bold text-2xl mt-1 block">
                {(healthMetrics.information_records?.outdated || 0) + (healthMetrics.services?.outdated || 0)}
              </span>
              <span className="text-[11px] text-red-600 mt-1 block">Freshness policy expired</span>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block uppercase font-semibold text-[10px]">Sources Monitored</span>
              <span className="text-slate-900 font-mono font-bold text-xl mt-1 block">
                {healthMetrics.sources?.total || 0} Sources
              </span>
              <span className="text-[10px] text-slate-500 mt-1 block">
                Audit: {healthMetrics.last_source_audit}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Source Change Detection Review Queue */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-900 font-heading flex items-center gap-2">
            <Clock className="w-5 h-5 text-orange-500" />
            <span>Detected Source Change Verification Queue</span>
          </h2>
          <button
            onClick={fetchAdminData}
            className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-700 text-xs font-semibold flex items-center gap-1 hover:bg-slate-50"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>

        {loading ? (
          <div className="h-48 bg-white rounded-3xl animate-pulse border border-slate-200" />
        ) : changeQueue.length === 0 ? (
          <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 text-slate-500 text-xs space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto" />
            <p className="font-semibold text-slate-800">All registered information is 🟢 VERIFIED and in sync with official sources.</p>
            <p className="text-slate-400">New changes detected by scheduled crawlers will appear here for admin review.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {changeQueue.map((item) => (
              <div key={item.id} className="bg-white p-6 rounded-3xl border border-amber-300 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <span className="text-xs font-bold text-amber-700 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-200">
                    Change #{item.id} • {item.information_record_id || item.sub_service_id}
                  </span>
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-orange-600 hover:underline flex items-center gap-1"
                  >
                    <span>View Official Source</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>

                <p className="text-xs text-slate-800 font-medium">{item.detected_change_summary}</p>

                {/* Diff Viewer */}
                {item.diff_data && Object.keys(item.diff_data).length > 0 && (
                  <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200 text-[11px] font-mono space-y-1">
                    <span className="font-bold text-slate-700 block uppercase text-[10px]">Field-level Diffs:</span>
                    {Object.entries(item.diff_data).map(([k, v]) => (
                      <div key={k} className="text-slate-600">
                        <span className="text-indigo-600 font-bold">{k}: </span>
                        <span className="text-red-500 line-through">"{JSON.stringify(v?.old)}"</span>
                        <span> ➔ </span>
                        <span className="text-emerald-600 font-bold">"{JSON.stringify(v?.new)}"</span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="flex justify-end gap-2 pt-2 text-xs">
                  <button
                    onClick={() => handleRejectChange(item.id)}
                    disabled={actionLoading === item.id}
                    className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold flex items-center gap-1.5 cursor-pointer"
                  >
                    <XCircle className="w-4 h-4 text-red-500" />
                    <span>Reject</span>
                  </button>

                  <button
                    onClick={() => handleApproveChange(item.id)}
                    disabled={actionLoading === item.id}
                    className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold flex items-center gap-1.5 shadow-xs cursor-pointer"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{actionLoading === item.id ? 'Approving...' : 'Approve & Increment Version'}</span>
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

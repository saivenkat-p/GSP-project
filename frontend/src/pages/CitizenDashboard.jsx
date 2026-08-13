import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { StatusTimeline } from '../components/StatusTimeline';
import { LayoutDashboard, FileText, AlertTriangle, CheckCircle2, Clock, ArrowRight, ShieldCheck, Landmark } from 'lucide-react';

export const CitizenDashboard = () => {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const res = await apiService.getUserRequests();
      setRequests(res.data);
    } catch (err) {
      console.error('Error fetching user requests:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20">
      {/* Header */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
            <LayoutDashboard className="w-4 h-4" />
            <span>Citizen Service Portal</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-white mt-2 font-heading">
            Welcome back, {user?.name || 'Citizen'}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Track active service checklists, application status timelines, and rejection diagnostics
          </p>
        </div>

        <Link
          to="/discover"
          className="px-5 py-2.5 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-bold text-xs flex items-center gap-2 shadow-lg transition-colors shrink-0"
        >
          <span>Start New Service Request</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Main Content */}
      {loading ? (
        <div className="h-64 bg-slate-900 rounded-3xl animate-pulse border border-slate-800" />
      ) : requests.length === 0 ? (
        <div className="p-12 text-center bg-slate-900 rounded-3xl border border-slate-800 text-slate-400 space-y-4">
          <FileText className="w-12 h-12 text-slate-600 mx-auto" />
          <div>
            <h3 className="text-base font-bold text-slate-200">No Active Service Applications</h3>
            <p className="text-xs text-slate-400 mt-1">Search our AI Navigator to find and save your first government service checklist.</p>
          </div>
          <Link
            to="/discover"
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-bold text-xs transition-colors"
          >
            <span>Explore Services</span>
          </Link>
        </div>
      ) : (
        <div className="space-y-8">
          <h2 className="text-xl font-bold text-white font-heading flex items-center gap-2">
            <Clock className="w-5 h-5 text-saffron-400" />
            <span>My Active Service Applications & Status Timelines</span>
          </h2>

          {requests.map((req) => {
            const isRejected = req.status === 'rejected';
            return (
              <div key={req.id} className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-6">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-saffron-400 bg-saffron-500/10 px-2.5 py-0.5 rounded border border-saffron-500/20">
                        {req.service?.category || 'Revenue'}
                      </span>
                      {req.partner && (
                        <span className="text-xs font-semibold text-sky-400 bg-sky-500/10 px-2.5 py-0.5 rounded border border-sky-500/20">
                          Partner: {req.partner.business_name}
                        </span>
                      )}
                    </div>
                    <h3 className="text-xl font-bold text-white mt-2 font-heading">
                      {req.service?.official_name || 'Government Service Request'}
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Created on: {new Date(req.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })} • District: {req.citizen_district}
                    </p>
                  </div>

                  {/* Rejection Alert Action */}
                  {isRejected ? (
                    <Link
                      to={`/rejection-help/${req.id}`}
                      className="px-4 py-2.5 rounded-xl bg-red-500 hover:bg-red-600 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-red-500/20 transition-colors animate-pulse"
                    >
                      <AlertTriangle className="w-4 h-4" />
                      <span>View Rejection Diagnostic & Remedy</span>
                    </Link>
                  ) : (
                    <Link
                      to={`/tracking/${req.id}`}
                      className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 font-semibold text-xs transition-colors flex items-center gap-1.5"
                    >
                      <span>Full Timeline View</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  )}
                </div>

                {/* Status Timeline */}
                <StatusTimeline currentStatus={req.status} officialAppNo={req.official_application_no} notes={req.status_notes} />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

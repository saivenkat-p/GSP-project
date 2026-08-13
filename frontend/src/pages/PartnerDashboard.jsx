import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Clock, CheckCircle2, AlertOctagon, Edit, Save, RefreshCw } from 'lucide-react';

export const PartnerDashboard = () => {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  // Status update state for selected request
  const [updatingId, setUpdatingId] = useState(null);
  const [newStatus, setNewStatus] = useState('');
  const [statusNotes, setStatusNotes] = useState('');
  const [appNo, setAppNo] = useState('');

  useEffect(() => {
    fetchPartnerRequests();
  }, []);

  const fetchPartnerRequests = async () => {
    try {
      setLoading(true);
      const res = await apiService.getUserRequests();
      setRequests(res.data);
    } catch (err) {
      console.error('Error fetching partner requests:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatusSubmit = async (reqId) => {
    try {
      await apiService.updateRequestStatus(reqId, newStatus, statusNotes, appNo);
      setUpdatingId(null);
      fetchPartnerRequests();
    } catch (err) {
      console.error('Status update error:', err);
    }
  };

  const startEdit = (req) => {
    setUpdatingId(req.id);
    setNewStatus(req.status);
    setStatusNotes(req.status_notes || '');
    setAppNo(req.official_application_no || '');
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20">
      {/* Header */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
          <ShieldCheck className="w-4 h-4" />
          <span>Verified Partner Operations Portal</span>
        </div>

        <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">
          {user?.name || 'Partner Center Operations'}
        </h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Manage incoming citizen assistance requests, update official portal submission numbers, and process document verifications.
        </p>

        {/* Metrics Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-800 text-xs">
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span className="text-slate-500 block uppercase font-semibold text-[10px]">Total Cases</span>
            <span className="text-white font-bold text-lg">{requests.length}</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span className="text-slate-500 block uppercase font-semibold text-[10px]">In Progress</span>
            <span className="text-amber-400 font-bold text-lg">
              {requests.filter((r) => r.status !== 'certificate_generated' && r.status !== 'rejected').length}
            </span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span className="text-slate-500 block uppercase font-semibold text-[10px]">Completed</span>
            <span className="text-emerald-400 font-bold text-lg">
              {requests.filter((r) => r.status === 'certificate_generated').length}
            </span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span className="text-slate-500 block uppercase font-semibold text-[10px]">Assistance Rating</span>
            <span className="text-saffron-400 font-bold text-lg">4.9 ⭐</span>
          </div>
        </div>
      </div>

      {/* Incoming Assistance Cases */}
      <div className="space-y-6">
        <h2 className="text-xl font-bold text-white font-heading flex items-center gap-2">
          <Clock className="w-5 h-5 text-sky-400" />
          <span>Active Citizen Assistance Requests Queue</span>
        </h2>

        {loading ? (
          <div className="h-64 bg-slate-900 rounded-3xl animate-pulse border border-slate-800" />
        ) : requests.length === 0 ? (
          <div className="p-12 text-center bg-slate-900 rounded-3xl border border-slate-800 text-slate-400 text-xs">
            No incoming assistance requests in queue right now.
          </div>
        ) : (
          <div className="space-y-4">
            {requests.map((req) => (
              <div key={req.id} className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold uppercase text-saffron-400 bg-saffron-500/10 px-2 py-0.5 rounded border border-saffron-500/20">
                        Case #{req.id}
                      </span>
                      <span className="text-xs font-semibold text-slate-300">
                        Citizen: {req.citizen?.name || 'Citizen User'}
                      </span>
                    </div>
                    <h3 className="text-lg font-bold text-white mt-1 font-heading">
                      {req.service?.official_name || 'Government Service'}
                    </h3>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-semibold px-3 py-1 rounded bg-slate-950 text-emerald-400 border border-slate-800">
                      Status: {req.status}
                    </span>
                    <button
                      onClick={() => startEdit(req)}
                      className="px-3 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 font-semibold text-xs border border-sky-500/30 flex items-center gap-1 transition-colors"
                    >
                      <Edit className="w-3.5 h-3.5" />
                      <span>Update Status</span>
                    </button>
                  </div>
                </div>

                {/* Edit Form Drawer */}
                {updatingId === req.id && (
                  <div className="p-4 rounded-xl bg-slate-950 border border-sky-500/30 space-y-4">
                    <h4 className="text-xs font-bold text-sky-400 uppercase tracking-wider">Update Application Status Timeline</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                      <div>
                        <label className="block text-slate-400 mb-1 font-medium">Timeline Step</label>
                        <select
                          value={newStatus}
                          onChange={(e) => setNewStatus(e.target.value)}
                          className="w-full bg-slate-900 text-slate-200 border border-slate-800 rounded-lg p-2 focus:outline-none"
                        >
                          <option value="requirement_identified">1. Requirement Identified</option>
                          <option value="documents_prepared">2. Documents Prepared</option>
                          <option value="submitted_to_official_portal">3. Submitted to Official Portal</option>
                          <option value="government_verification">4. Government Verification</option>
                          <option value="certificate_generated">5. Certificate Generated (Completed)</option>
                          <option value="rejected">Rejected by Authority</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-slate-400 mb-1 font-medium">Official Portal Application No.</label>
                        <input
                          type="text"
                          value={appNo}
                          onChange={(e) => setAppNo(e.target.value)}
                          placeholder="e.g. IC012026887799"
                          className="w-full bg-slate-900 text-slate-200 border border-slate-800 rounded-lg p-2 focus:outline-none"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-slate-400 text-xs mb-1 font-medium">Operator Status Notes</label>
                      <textarea
                        value={statusNotes}
                        onChange={(e) => setStatusNotes(e.target.value)}
                        placeholder="Add updates for citizen..."
                        className="w-full bg-slate-900 text-slate-200 border border-slate-800 rounded-lg p-2 text-xs focus:outline-none h-16"
                      />
                    </div>

                    <div className="flex justify-end gap-2 text-xs">
                      <button
                        onClick={() => setUpdatingId(null)}
                        className="px-3 py-1.5 rounded-lg bg-slate-900 text-slate-400 hover:text-white"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleUpdateStatusSubmit(req.id)}
                        className="px-4 py-1.5 rounded-lg bg-sky-500 text-white font-bold flex items-center gap-1 hover:bg-sky-600"
                      >
                        <Save className="w-3.5 h-3.5" />
                        <span>Save Status Update</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { PhoneCall, UserCheck, ShieldCheck, Clock, CheckCircle2, AlertCircle, Edit, Plus, FileText } from 'lucide-react';

export const StaffDashboard = () => {
  const { user } = useAuth();
  const [leads, setLeads] = useState([]);
  const [partners, setPartners] = useState([]);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  // Edit drawer state
  const [activeLead, setActiveLead] = useState(null);
  const [selectedStatus, setSelectedStatus] = useState('NEW');
  const [selectedPartner, setSelectedPartner] = useState('');
  const [newNote, setNewNote] = useState('');
  const [appNo, setAppNo] = useState('');

  useEffect(() => {
    fetchLeadsAndPartners();
  }, [statusFilter]);

  const fetchLeadsAndPartners = async () => {
    try {
      setLoading(true);
      const [leadRes, prtRes] = await Promise.all([
        apiService.getStaffLeads(statusFilter),
        apiService.getPartners('AP-NTR'),
      ]);
      setLeads(leadRes.data);
      setPartners(prtRes.data);
    } catch (err) {
      console.error('Error fetching staff leads:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateLead = async () => {
    if (!activeLead) return;
    try {
      const pId = selectedPartner ? parseInt(selectedPartner) : null;
      await apiService.updateLeadStatus(activeLead.id, selectedStatus, newNote, appNo, pId);
      if (newNote.trim()) {
        await apiService.addLeadNote(activeLead.id, newNote);
      }
      setActiveLead(null);
      setNewNote('');
      fetchLeadsAndPartners();
    } catch (err) {
      console.error('Error updating lead status:', err);
    }
  };

  const openLeadModal = (lead) => {
    setActiveLead(lead);
    setSelectedStatus(lead.status);
    setSelectedPartner(lead.partner_id || '');
    setAppNo(lead.official_application_no || '');
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20">
      {/* Header */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
          <PhoneCall className="w-4 h-4" />
          <span>GSP Staff Lead Operations Desk</span>
        </div>

        <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">
          Citizen Callback & Lead Management
        </h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Core business workflow: Contact citizens, record exact assistance requirements, assign service-certified partners, and update lead statuses across the 14-step timeline.
        </p>

        {/* Lead Status Filter Pills */}
        <div className="pt-2 flex flex-wrap items-center gap-1.5 text-xs">
          <span className="text-slate-500 font-bold uppercase text-[10px]">Filter Status:</span>
          {['ALL', 'NEW', 'CONTACT_PENDING', 'CONTACTED', 'REQUIREMENT_IDENTIFIED', 'ASSISTANCE_SELECTED', 'PARTNER_ASSIGNED', 'IN_PROGRESS', 'COMPLETED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-2.5 py-1 rounded-lg transition-colors font-medium ${
                statusFilter === st ? 'bg-emerald-500 text-slate-950 font-bold' : 'bg-slate-900 border border-slate-800 text-slate-400'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Leads Queue */}
      {loading ? (
        <div className="h-64 bg-slate-900 rounded-3xl animate-pulse border border-slate-800" />
      ) : leads.length === 0 ? (
        <div className="p-12 text-center bg-slate-900 rounded-3xl border border-slate-800 text-slate-400 text-xs">
          No leads matching status filter '{statusFilter}'.
        </div>
      ) : (
        <div className="space-y-4">
          {leads.map((lead) => (
            <div key={lead.id} className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase text-saffron-400 bg-saffron-500/10 px-2 py-0.5 rounded border border-saffron-500/20">
                      Lead #{lead.id}
                    </span>
                    <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      Tier: {lead.assistance_tier}
                    </span>
                    {lead.callback_requested && (
                      <span className="text-xs font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                        📞 Callback Requested
                      </span>
                    )}
                  </div>
                  <h3 className="text-lg font-bold text-white mt-1 font-heading">
                    {lead.sub_service?.sub_service_name || 'Government Sub-Service Request'}
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Location: {lead.citizen_location_str} • Scheduled: {lead.scheduled_callback_time || 'Immediate'}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold px-3 py-1 rounded bg-slate-950 text-saffron-400 border border-slate-800">
                    Status: {lead.status}
                  </span>
                  <button
                    onClick={() => openLeadModal(lead)}
                    className="px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 font-semibold text-xs border border-emerald-500/30 flex items-center gap-1 transition-colors"
                  >
                    <Edit className="w-3.5 h-3.5" />
                    <span>Manage Lead</span>
                  </button>
                </div>
              </div>

              {lead.notes && (
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300">
                  <strong className="text-slate-500 block text-[10px] uppercase">Notes:</strong>
                  {lead.notes}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* MANAGE LEAD MODAL */}
      {activeLead && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="glass-panel w-full max-w-lg p-6 rounded-3xl border border-slate-800 space-y-4 bg-slate-900 shadow-2xl">
            <h3 className="text-base font-bold text-white font-heading">Manage Service Lead #{activeLead.id}</h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-semibold">14 Lead Statuses Workflow</label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="w-full bg-slate-950 text-slate-100 border border-slate-800 rounded-xl p-2.5 focus:outline-none"
                >
                  <option value="NEW">1. NEW</option>
                  <option value="CONTACT_PENDING">2. CONTACT PENDING</option>
                  <option value="CONTACTED">3. CONTACTED</option>
                  <option value="REQUIREMENT_IDENTIFIED">4. REQUIREMENT IDENTIFIED</option>
                  <option value="ASSISTANCE_SELECTED">5. ASSISTANCE SELECTED</option>
                  <option value="PARTNER_ASSIGNED">6. PARTNER ASSIGNED</option>
                  <option value="DOCUMENTS_PENDING">7. DOCUMENTS PENDING</option>
                  <option value="IN_PROGRESS">8. IN PROGRESS</option>
                  <option value="WAITING_FOR_CITIZEN">9. WAITING FOR CITIZEN</option>
                  <option value="WAITING_FOR_GOVERNMENT">10. WAITING FOR GOVERNMENT</option>
                  <option value="COMPLETED">11. COMPLETED</option>
                  <option value="CANCELLED">12. CANCELLED</option>
                  <option value="REJECTED">13. REJECTED</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-semibold">Assign Service-Certified Partner</label>
                <select
                  value={selectedPartner}
                  onChange={(e) => setSelectedPartner(e.target.value)}
                  className="w-full bg-slate-950 text-slate-100 border border-slate-800 rounded-xl p-2.5 focus:outline-none"
                >
                  <option value="">Unassigned (Staff Handling)</option>
                  {partners.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.business_name} (⭐ {p.rating})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-semibold">Official Application Number</label>
                <input
                  type="text"
                  value={appNo}
                  onChange={(e) => setAppNo(e.target.value)}
                  placeholder="e.g. IC0120268877"
                  className="w-full bg-slate-950 text-slate-100 border border-slate-800 rounded-xl p-2.5 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-semibold">Call Log / Staff Note</label>
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Record citizen requirement details from phone call..."
                  className="w-full bg-slate-950 text-slate-100 border border-slate-800 rounded-xl p-2.5 h-20 focus:outline-none"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 text-xs pt-2">
              <button onClick={() => setActiveLead(null)} className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300">
                Cancel
              </button>
              <button onClick={handleUpdateLead} className="px-5 py-2 rounded-xl bg-emerald-500 text-slate-950 font-bold hover:bg-emerald-600">
                Save & Update Lead
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

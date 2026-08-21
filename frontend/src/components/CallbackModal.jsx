import React, { useState } from 'react';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { PhoneCall, CheckCircle2, X, Clock, MapPin, Sparkles, ShieldCheck } from 'lucide-react';

export const CallbackModal = ({ isOpen, onClose, defaultService = 'General Government Service Assistance' }) => {
  const { user, selectedState, selectedDistrict } = useAuth();
  
  const [name, setName] = useState(user?.name || '');
  const [phone, setPhone] = useState(user?.phone || '');
  const [serviceNeeded, setServiceNeeded] = useState(defaultService);
  const [preferredTime, setPreferredTime] = useState('Within 15 Minutes');
  const [notes, setNotes] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [successResult, setSuccessResult] = useState(null);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Please provide your name.');
      return;
    }
    if (!phone || phone.length < 10) {
      setError('Please enter a valid 10-digit phone number.');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const res = await apiService.requestCallback({
        citizen_name: name,
        phone: phone,
        service_needed: serviceNeeded,
        preferred_time: preferredTime,
        location_str: `${selectedDistrict || 'NTR'}, ${selectedState || 'AP'}`,
        requirement_notes: notes
      });

      setSuccessResult(res.data);
    } catch (err) {
      console.error('Callback request failed:', err);
      setError('Failed to schedule callback. Please try again or call our toll-free desk.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSuccessResult(null);
    setError('');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-md w-full overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="p-6 bg-gradient-to-r from-orange-500 to-amber-600 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-2xl bg-white/20 flex items-center justify-center">
              <PhoneCall className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-extrabold text-base font-heading">Request Citizen Assistance</h3>
              <p className="text-xs text-orange-100 font-medium">Connect with a certified GSP specialist</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors cursor-pointer"
          >
            <X className="w-4 h-4 text-white" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {successResult ? (
            <div className="text-center py-4 space-y-3">
              <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h4 className="font-black text-lg text-slate-900 font-heading">Callback Scheduled!</h4>
              <p className="text-xs text-slate-600 leading-relaxed font-medium">
                {successResult.message}
              </p>
              <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200 text-xs text-slate-700 font-mono">
                Request Lead ID: <strong>#{successResult.request_id}</strong>
              </div>
              <button
                onClick={handleClose}
                className="w-full py-3 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-md transition-colors cursor-pointer"
              >
                Done
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-3.5">
              {error && (
                <div className="p-2.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-600 font-medium text-center">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Your Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Sai Kumar"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-800 focus:outline-none focus:border-orange-500 font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Contact Mobile Number</label>
                <div className="relative">
                  <span className="absolute left-3 top-2 text-xs font-bold text-slate-400">+91</span>
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    maxLength={10}
                    placeholder="98765 43210"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-11 pr-3.5 py-2 text-xs text-slate-800 focus:outline-none focus:border-orange-500 font-medium"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Service / Scheme Requirement</label>
                <input
                  type="text"
                  value={serviceNeeded}
                  onChange={(e) => setServiceNeeded(e.target.value)}
                  placeholder="e.g. Driving Licence Renewal or Rythu Bharosa"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-800 focus:outline-none focus:border-orange-500 font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Preferred Callback Time</label>
                <select
                  value={preferredTime}
                  onChange={(e) => setPreferredTime(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-orange-500 font-medium"
                >
                  <option value="Within 15 Minutes">⚡ Immediately (Within 15 Mins)</option>
                  <option value="Today Afternoon (1 PM - 4 PM)">Today Afternoon (1 PM - 4 PM)</option>
                  <option value="Today Evening (5 PM - 8 PM)">Today Evening (5 PM - 8 PM)</option>
                  <option value="Tomorrow Morning (9 AM - 12 PM)">Tomorrow Morning (9 AM - 12 PM)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Specific Questions or Notes (Optional)</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={2}
                  placeholder="Briefly describe what assistance you need..."
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-orange-500 font-medium resize-none"
                />
              </div>

              <div className="p-2.5 rounded-xl bg-indigo-50/80 border border-indigo-100 flex items-center gap-2 text-[11px] text-indigo-900">
                <ShieldCheck className="w-4 h-4 text-indigo-600 shrink-0" />
                <span>Zero charge for consultation. Official statutory fees are always separated.</span>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-md transition-colors flex items-center justify-center gap-2 cursor-pointer"
              >
                <PhoneCall className="w-4 h-4" />
                <span>{loading ? 'Scheduling...' : 'Request Assistance Specialist Call'}</span>
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

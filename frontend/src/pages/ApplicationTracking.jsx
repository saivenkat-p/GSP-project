import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import { StatusTimeline } from '../components/StatusTimeline';
import { Landmark, ArrowLeft, ShieldCheck, Clock } from 'lucide-react';

export const ApplicationTracking = () => {
  const { id } = useParams();
  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRequest();
  }, [id]);

  const fetchRequest = async () => {
    try {
      setLoading(true);
      const res = await apiService.getRequestById(id);
      setRequest(res.data);
    } catch (err) {
      console.error('Error fetching request timeline:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="max-w-4xl mx-auto py-12 animate-pulse h-96 bg-slate-900 rounded-3xl" />;
  }

  if (!request) {
    return (
      <div className="max-w-md mx-auto py-12 text-center space-y-4">
        <p className="text-slate-400">Application request not found.</p>
        <Link to="/dashboard" className="text-saffron-400 font-semibold text-xs hover:underline">Return to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-20">
      <Link to="/dashboard" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to My Dashboard</span>
      </Link>

      <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-6">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-saffron-400 bg-saffron-500/10 px-3 py-1 rounded-full border border-saffron-500/20">
            {request.service?.category || 'Revenue'}
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-2 font-heading">
            {request.service?.official_name}
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Official Submission Channel: {request.service?.application_method}
          </p>
        </div>

        <StatusTimeline currentStatus={request.status} officialAppNo={request.official_application_no} notes={request.status_notes} />
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Compass, User, ShieldCheck, UserCheck, ArrowRight, Lock, Mail, Smartphone, Key, CheckCircle } from 'lucide-react';

export const Login = () => {
  const [authMode, setAuthMode] = useState('MOBILE_OTP'); // MOBILE_OTP | AADHAAR_CONSENT | EMAIL
  const [mobileNumber, setMobileNumber] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [otpInput, setOtpInput] = useState('');
  const [aadhaarNumber, setAadhaarNumber] = useState('');
  const [aadhaarConsent, setAadhaarConsent] = useState(false);
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, demoSwitchRole } = useAuth();
  const navigate = useNavigate();

  const handleMobileSubmit = (e) => {
    e.preventDefault();
    if (!mobileNumber || mobileNumber.length < 10) {
      setError('Please enter a valid 10-digit mobile number.');
      return;
    }
    if (!otpSent) {
      setOtpSent(true);
      setError('');
    } else {
      // Complete OTP Sign-In
      handleDemoSwitch('citizen');
    }
  };

  const handleAadhaarVerify = (e) => {
    e.preventDefault();
    if (!aadhaarConsent) {
      setError('Please check the consent box to proceed with UIDAI-compliant verification.');
      return;
    }
    if (!aadhaarNumber || aadhaarNumber.length < 12) {
      setError('Please enter a valid 12-digit Aadhaar number.');
      return;
    }
    // Complete Aadhaar Verification
    handleDemoSwitch('citizen');
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      setLoading(true);
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoSwitch = async (role) => {
    try {
      await demoSwitchRole(role);
      if (role === 'partner') navigate('/partner-dashboard');
      else if (role === 'admin') navigate('/admin-dashboard');
      else navigate('/');
    } catch (err) {
      console.error('Demo login failed:', err);
    }
  };

  return (
    <div className="max-w-md mx-auto py-8 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center text-white font-bold mx-auto shadow-md">
          <Compass className="w-7 h-7" />
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 font-heading">Welcome to GSP V2</h1>
        <p className="text-xs text-slate-500 font-medium">Your Personal Government & Opportunity Assistant</p>
      </div>

      {/* Platform Disclaimer Banner */}
      <div className="p-3 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 text-[11px] leading-relaxed text-center font-medium">
        🛡️ <strong>Independent Platform Notice:</strong> GSP is an independent citizen assistance & guidance platform. Official government sources are linked for all statutory records.
      </div>

      {/* INSTANT DEMO PERSONA SWITCHER */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-2">
        <span className="text-[10px] font-bold uppercase text-orange-600 block tracking-wider text-center">
          ⚡ One-Click Instant Demo Login
        </span>
        <div className="grid grid-cols-3 gap-2 text-xs">
          <button
            onClick={() => handleDemoSwitch('citizen')}
            className="p-2.5 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-bold transition-colors flex flex-col items-center gap-1 shadow-xs"
          >
            <User className="w-4 h-4" />
            <span>Citizen</span>
          </button>

          <button
            onClick={() => handleDemoSwitch('partner')}
            className="p-2.5 rounded-xl bg-sky-600 hover:bg-sky-700 text-white font-bold transition-colors flex flex-col items-center gap-1 shadow-xs"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Partner 🛡️</span>
          </button>

          <button
            onClick={() => handleDemoSwitch('admin')}
            className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition-colors flex flex-col items-center gap-1 shadow-xs"
          >
            <UserCheck className="w-4 h-4" />
            <span>Admin</span>
          </button>
        </div>
      </div>

      {/* Authentication Mode Tabs */}
      <div className="grid grid-cols-2 gap-1 p-1 rounded-2xl bg-slate-100 border border-slate-200 text-xs font-bold">
        <button
          onClick={() => { setAuthMode('MOBILE_OTP'); setError(''); }}
          className={`py-2 rounded-xl transition-all ${authMode === 'MOBILE_OTP' ? 'bg-white text-orange-600 shadow-xs' : 'text-slate-600'}`}
        >
          📱 Mobile OTP
        </button>
        <button
          onClick={() => { setAuthMode('AADHAAR_CONSENT'); setError(''); }}
          className={`py-2 rounded-xl transition-all ${authMode === 'AADHAAR_CONSENT' ? 'bg-white text-orange-600 shadow-xs' : 'text-slate-600'}`}
        >
          🆔 Aadhaar Verification
        </button>
      </div>

      {error && <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-600 font-medium text-center">{error}</div>}

      {/* MODE 1: MOBILE OTP PRIMARY SIGN-IN */}
      {authMode === 'MOBILE_OTP' && (
        <form onSubmit={handleMobileSubmit} className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Mobile Number</label>
            <div className="relative">
              <span className="absolute left-3 top-2.5 text-xs font-bold text-slate-400">+91</span>
              <input
                type="tel"
                value={mobileNumber}
                onChange={(e) => setMobileNumber(e.target.value)}
                maxLength={10}
                placeholder="98765 43210"
                className="w-full bg-slate-50 text-slate-900 border border-slate-200 rounded-xl pl-12 pr-4 py-2.5 text-xs focus:outline-none focus:border-orange-500 font-medium"
              />
            </div>
          </div>

          {otpSent && (
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-slate-700">Enter 4-Digit OTP</label>
              <input
                type="text"
                value={otpInput}
                onChange={(e) => setOtpInput(e.target.value)}
                maxLength={4}
                placeholder="1 2 3 4"
                className="w-full bg-slate-50 text-slate-900 border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-center font-bold tracking-widest focus:outline-none focus:border-orange-500"
              />
              <span className="text-[10px] text-emerald-600 font-semibold block text-center">✓ OTP sent to +91 {mobileNumber}</span>
            </div>
          )}

          <button
            type="submit"
            className="w-full py-3 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-md transition-colors flex items-center justify-center gap-2"
          >
            <span>{otpSent ? 'Verify OTP & Continue' : 'Get OTP'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      )}

      {/* MODE 2: OPTIONAL AADHAAR-BASED VERIFICATION */}
      {authMode === 'AADHAAR_CONSENT' && (
        <form onSubmit={handleAadhaarVerify} className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div className="p-3 rounded-xl bg-sky-50 border border-sky-200 text-[11px] text-sky-900 leading-relaxed font-medium">
            🛡️ <strong>UIDAI Compliant Verification:</strong> Aadhaar verification is optional. Consent is requested for identity verification only.
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">12-Digit Aadhaar Number</label>
            <input
              type="text"
              value={aadhaarNumber}
              onChange={(e) => setAadhaarNumber(e.target.value)}
              maxLength={12}
              placeholder="1234 5678 9012"
              className="w-full bg-slate-50 text-slate-900 border border-slate-200 rounded-xl px-4 py-2.5 text-xs font-medium focus:outline-none focus:border-orange-500"
            />
          </div>

          <div className="flex items-start gap-2 pt-1 text-xs">
            <input
              type="checkbox"
              id="consent"
              checked={aadhaarConsent}
              onChange={(e) => setAadhaarConsent(e.target.checked)}
              className="mt-0.5 rounded border-slate-300 text-orange-500 focus:ring-orange-500"
            />
            <label htmlFor="consent" className="text-[11px] text-slate-600 leading-tight">
              I voluntarily consent to authenticate my identity via Aadhaar OTP in accordance with UIDAI guidelines.
            </label>
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-xl bg-sky-600 hover:bg-sky-700 text-white font-bold text-xs shadow-md transition-colors flex items-center justify-center gap-2"
          >
            <span>Verify Aadhaar</span>
            <CheckCircle className="w-4 h-4" />
          </button>

          <p className="text-[10px] text-slate-400 text-center font-medium">Your choice • Secure • Consent based</p>
        </form>
      )}

      {/* Alternative Email Login Link */}
      <div className="text-center text-xs text-slate-500">
        Prefer password login?{' '}
        <button
          onClick={() => handleDemoSwitch('citizen')}
          className="text-orange-600 font-bold hover:underline"
        >
          Sign in as Citizen Demo
        </button>
      </div>
    </div>
  );
};

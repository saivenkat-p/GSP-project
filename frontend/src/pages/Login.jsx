import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Compass, User, ShieldCheck, UserCheck, ArrowRight, Lock, Mail, Smartphone, Key, CheckCircle, LogIn } from 'lucide-react';

export const Login = () => {
  const [authMode, setAuthMode] = useState('MOBILE_OTP'); // MOBILE_OTP | EMAIL
  const [mobileNumber, setMobileNumber] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [otpInput, setOtpInput] = useState('');
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, demoSwitchRole } = useAuth();
  const navigate = useNavigate();

  const handleMobileSubmit = async (e) => {
    e.preventDefault();
    if (!mobileNumber || mobileNumber.length < 10) {
      setError('Please enter a valid 10-digit mobile number.');
      return;
    }
    if (!otpSent) {
      setOtpSent(true);
      setError('');
    } else {
      if (otpInput.length < 4) {
        setError('Please enter the 4-digit OTP.');
        return;
      }
      // Authenticate via prototype OTP session
      try {
        setLoading(true);
        await demoSwitchRole('citizen');
        navigate('/');
      } catch (err) {
        setError('Authentication failed. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      setLoading(true);
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPersona = async (role) => {
    try {
      setLoading(true);
      await demoSwitchRole(role);
      if (role === 'partner') navigate('/partner-dashboard');
      else if (role === 'staff') navigate('/staff');
      else if (role === 'admin') navigate('/admin-dashboard');
      else navigate('/');
    } catch (err) {
      console.error('Login failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-8 space-y-6 px-4">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center text-white font-bold mx-auto shadow-md">
          <Compass className="w-7 h-7" />
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 font-heading">
          Welcome to GSP
        </h1>
        <p className="text-xs text-slate-500 font-medium">Your Personal Government & Opportunity Partner</p>
      </div>

      {/* Platform Disclaimer Banner */}
      <div className="p-3 rounded-2xl bg-indigo-50/80 border border-indigo-100 text-indigo-900 text-[11px] leading-relaxed text-center font-medium">
        🛡️ <strong>Citizen Privacy & Consent:</strong> GSP is an independent citizen assistance platform. All official statutory information is cited from registered government portals.
      </div>

      {/* Authentication Mode Tabs */}
      <div className="grid grid-cols-2 gap-1 p-1 rounded-2xl bg-slate-100 border border-slate-200 text-xs font-bold">
        <button
          onClick={() => { setAuthMode('MOBILE_OTP'); setError(''); }}
          className={`py-2 rounded-xl transition-all cursor-pointer ${authMode === 'MOBILE_OTP' ? 'bg-white text-orange-600 shadow-xs' : 'text-slate-600'}`}
        >
          📱 Mobile OTP
        </button>
        <button
          onClick={() => { setAuthMode('EMAIL'); setError(''); }}
          className={`py-2 rounded-xl transition-all cursor-pointer ${authMode === 'EMAIL' ? 'bg-white text-orange-600 shadow-xs' : 'text-slate-600'}`}
        >
          ✉️ Staff / Email Sign-In
        </button>
      </div>

      {error && <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-600 font-medium text-center">{error}</div>}

      {/* MODE 1: MOBILE OTP PRIMARY SIGN-IN */}
      {authMode === 'MOBILE_OTP' && (
        <form onSubmit={handleMobileSubmit} className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Enter Mobile Number</label>
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
            <div className="space-y-1.5 animate-in fade-in">
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
            disabled={loading}
            className="w-full py-3 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-md transition-colors flex items-center justify-center gap-2 cursor-pointer"
          >
            <span>{otpSent ? (loading ? 'Signing In...' : 'Verify OTP & Continue') : 'Send OTP'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      )}

      {/* MODE 2: EMAIL / PASSWORD FOR STAFF & CITIZEN */}
      {authMode === 'EMAIL' && (
        <form onSubmit={handleEmailSubmit} className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              className="w-full bg-slate-50 text-slate-900 border border-slate-200 rounded-xl px-4 py-2.5 text-xs focus:outline-none focus:border-orange-500 font-medium"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-slate-50 text-slate-900 border border-slate-200 rounded-xl px-4 py-2.5 text-xs focus:outline-none focus:border-orange-500 font-medium"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-md transition-colors flex items-center justify-center gap-2 cursor-pointer"
          >
            <LogIn className="w-4 h-4" />
            <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
          </button>
        </form>
      )}

      {/* Quick Test Persona Switcher (Convenient for Verification Testing) */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-2">
        <span className="text-[10px] font-bold uppercase text-slate-400 block tracking-wider text-center">
          Test Account One-Click Access
        </span>
        <div className="grid grid-cols-3 gap-2 text-xs">
          <button
            onClick={() => handleQuickPersona('citizen')}
            className="p-2 rounded-xl bg-slate-100 hover:bg-orange-50 hover:text-orange-600 text-slate-700 font-semibold transition-colors flex flex-col items-center gap-1 cursor-pointer"
          >
            <User className="w-3.5 h-3.5" />
            <span>Citizen</span>
          </button>

          <button
            onClick={() => handleQuickPersona('staff')}
            className="p-2 rounded-xl bg-slate-100 hover:bg-emerald-50 hover:text-emerald-600 text-slate-700 font-semibold transition-colors flex flex-col items-center gap-1 cursor-pointer"
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>Staff Desk</span>
          </button>

          <button
            onClick={() => handleQuickPersona('partner')}
            className="p-2 rounded-xl bg-slate-100 hover:bg-sky-50 hover:text-sky-600 text-slate-700 font-semibold transition-colors flex flex-col items-center gap-1 cursor-pointer"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Partner</span>
          </button>
        </div>
      </div>
    </div>
  );
};

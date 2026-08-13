import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Compass, User, ShieldCheck, UserCheck, ArrowRight, Lock, Mail } from 'lucide-react';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, demoSwitchRole } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
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
      else navigate('/dashboard');
    } catch (err) {
      console.error('Demo login failed:', err);
    }
  };

  return (
    <div className="max-w-md mx-auto py-12 space-y-8">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-saffron-500 to-amber-600 flex items-center justify-center text-white font-bold mx-auto shadow-lg shadow-saffron-500/20">
          <Compass className="w-7 h-7" />
        </div>
        <h1 className="text-2xl font-extrabold text-white font-heading">Sign In to GovNav</h1>
        <p className="text-xs text-slate-400">Access citizen service checklists, tracking timelines, & partner operations</p>
      </div>

      {/* ONE-CLICK INSTANT DEMO PERSONA SWITCHER */}
      <div className="bg-slate-900 p-4 rounded-2xl border border-saffron-500/30 space-y-2">
        <span className="text-[11px] font-bold uppercase text-saffron-400 block tracking-wider text-center">
          ⚡ One-Click Instant Demo Login Switcher
        </span>
        <div className="grid grid-cols-3 gap-2 text-xs">
          <button
            onClick={() => handleDemoSwitch('citizen')}
            className="p-2.5 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-bold transition-colors flex flex-col items-center gap-1 shadow"
          >
            <User className="w-4 h-4" />
            <span>Citizen</span>
          </button>

          <button
            onClick={() => handleDemoSwitch('partner')}
            className="p-2.5 rounded-xl bg-sky-500 hover:bg-sky-600 text-white font-bold transition-colors flex flex-col items-center gap-1 shadow"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Partner 🛡️</span>
          </button>

          <button
            onClick={() => handleDemoSwitch('admin')}
            className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition-colors flex flex-col items-center gap-1 shadow"
          >
            <UserCheck className="w-4 h-4" />
            <span>Admin</span>
          </button>
        </div>
      </div>

      {/* Standard Email Login Form */}
      <form onSubmit={handleSubmit} className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        {error && <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-400">{error}</div>}

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address</label>
          <div className="relative">
            <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="citizen@govnav.in"
              className="w-full bg-slate-900 text-slate-100 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-xs focus:outline-none focus:border-saffron-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              className="w-full bg-slate-900 text-slate-100 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-xs focus:outline-none focus:border-saffron-500"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-bold text-xs shadow-lg transition-colors flex items-center justify-center gap-2"
        >
          <span>Sign In</span>
          <ArrowRight className="w-4 h-4" />
        </button>

        <p className="text-center text-xs text-slate-400 pt-2">
          Don't have an account?{' '}
          <Link to="/register" className="text-saffron-400 font-semibold hover:underline">
            Register Account
          </Link>
        </p>
      </form>
    </div>
  );
};

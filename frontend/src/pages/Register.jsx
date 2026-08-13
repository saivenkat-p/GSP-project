import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Compass, User, ArrowRight, Lock, Mail, Phone, MapPin } from 'lucide-react';

export const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('citizen'); // 'citizen' | 'partner'
  const [phone, setPhone] = useState('');
  const [district, setDistrict] = useState('NTR / Vijayawada');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      setLoading(true);
      await register({ name, email, password, role, phone, district, state: 'Andhra Pradesh' });
      if (role === 'partner') navigate('/partner-dashboard');
      else navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-12 space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-extrabold text-white font-heading">Register New Account</h1>
        <p className="text-xs text-slate-400">Join Government Services Navigator as Citizen or Verified Partner</p>
      </div>

      <form onSubmit={handleSubmit} className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        {error && <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-400">{error}</div>}

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Account Role</label>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => setRole('citizen')}
              className={`p-2.5 rounded-xl font-bold border transition-colors ${role === 'citizen' ? 'bg-saffron-500 text-white border-saffron-400' : 'bg-slate-900 border-slate-800 text-slate-400'}`}
            >
              Citizen User
            </button>
            <button
              type="button"
              onClick={() => setRole('partner')}
              className={`p-2.5 rounded-xl font-bold border transition-colors ${role === 'partner' ? 'bg-sky-500 text-white border-sky-400' : 'bg-slate-900 border-slate-800 text-slate-400'}`}
            >
              Partner Center 🛡️
            </button>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Full Name / Center Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="Sai Kumar Varma"
            className="w-full bg-slate-900 text-slate-100 border border-slate-800 rounded-xl px-4 py-2.5 text-xs focus:outline-none focus:border-saffron-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="name@example.com"
            className="w-full bg-slate-900 text-slate-100 border border-slate-800 rounded-xl px-4 py-2.5 text-xs focus:outline-none focus:border-saffron-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Mobile Number</label>
          <input
            type="text"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+91 98765 43210"
            className="w-full bg-slate-900 text-slate-100 border border-slate-800 rounded-xl px-4 py-2.5 text-xs focus:outline-none focus:border-saffron-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">District (Andhra Pradesh)</label>
          <select
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
            className="w-full bg-slate-900 text-slate-100 border border-slate-800 rounded-xl px-4 py-2.5 text-xs focus:outline-none focus:border-saffron-500"
          >
            <option value="NTR / Vijayawada">NTR / Vijayawada</option>
            <option value="Visakhapatnam">Visakhapatnam</option>
            <option value="Guntur">Guntur</option>
            <option value="Tirupati">Tirupati</option>
            <option value="Anantapur">Anantapur</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="••••••••"
            className="w-full bg-slate-900 text-slate-100 border border-slate-800 rounded-xl px-4 py-2.5 text-xs focus:outline-none focus:border-saffron-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white font-bold text-xs shadow-lg transition-colors flex items-center justify-center gap-2"
        >
          <span>Register Account</span>
          <ArrowRight className="w-4 h-4" />
        </button>

        <p className="text-center text-xs text-slate-400 pt-2">
          Already have an account?{' '}
          <Link to="/login" className="text-saffron-400 font-semibold hover:underline">
            Sign In
          </Link>
        </p>
      </form>
    </div>
  );
};

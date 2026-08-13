import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Compass, MapPin, User, ShieldCheck, UserCheck, LogOut, Compass as CompassIcon, Search, LayoutDashboard, FileText, CheckCircle2 } from 'lucide-react';

export const Navbar = () => {
  const { user, logout, demoSwitchRole, selectedState, setSelectedState, selectedDistrict, setSelectedDistrict } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800 bg-slate-950/90 backdrop-blur-md">
      {/* Top National / State Banner */}
      <div className="bg-gradient-to-r from-saffron-600 via-amber-600 to-emerald-600 px-4 py-1 text-center text-xs font-semibold text-white tracking-wide flex items-center justify-between">
        <div className="flex items-center gap-2 mx-auto">
          <span>🇮🇳 GOVERNMENT SERVICES NAVIGATOR</span>
          <span className="hidden md:inline text-amber-200">•</span>
          <span className="hidden md:inline font-normal">Intelligent Discovery & Guidance Layer (Official Portals Authority)</span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-saffron-500 to-amber-600 flex items-center justify-center text-white font-bold shadow-lg shadow-saffron-500/20 group-hover:scale-105 transition-transform">
              <Compass className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <span className="text-lg font-extrabold text-white tracking-tight flex items-center gap-1.5 font-heading">
                GovNav <span className="text-saffron-500 text-xs px-2 py-0.5 rounded-full bg-saffron-500/10 border border-saffron-500/20">AP State</span>
              </span>
              <p className="text-[11px] text-slate-400 -mt-1 font-sans">Official Service Guidance Navigator</p>
            </div>
          </Link>

          {/* District & Location Filter */}
          <div className="hidden lg:flex items-center gap-2 bg-slate-900/90 px-3 py-1.5 rounded-full border border-slate-800 text-xs text-slate-300">
            <MapPin className="w-3.5 h-3.5 text-saffron-400" />
            <span className="text-slate-400">State & District:</span>
            <select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              className="bg-transparent font-medium text-amber-400 focus:outline-none cursor-pointer"
            >
              <option value="NTR / Vijayawada" className="bg-slate-900 text-white">NTR / Vijayawada (AP)</option>
              <option value="Visakhapatnam" className="bg-slate-900 text-white">Visakhapatnam (AP)</option>
              <option value="Guntur" className="bg-slate-900 text-white">Guntur (AP)</option>
              <option value="Tirupati" className="bg-slate-900 text-white">Tirupati (AP)</option>
              <option value="Anantapur" className="bg-slate-900 text-white">Anantapur (AP)</option>
            </select>
          </div>

          {/* Main Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 text-sm font-medium">
            <Link
              to="/discover"
              className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-1.5 ${
                isActive('/discover') ? 'bg-saffron-500/10 text-saffron-400 font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-900'
              }`}
            >
              <Search className="w-4 h-4 text-saffron-400" />
              <span>AI Service Navigator</span>
            </Link>

            <Link
              to="/assistance"
              className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-1.5 ${
                isActive('/assistance') ? 'bg-saffron-500/10 text-saffron-400 font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-900'
              }`}
            >
              <ShieldCheck className="w-4 h-4 text-sky-400" />
              <span>Verified Assistance</span>
            </Link>

            {user?.role === 'citizen' && (
              <Link
                to="/dashboard"
                className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-1.5 ${
                  isActive('/dashboard') ? 'bg-saffron-500/10 text-saffron-400 font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-900'
                }`}
              >
                <LayoutDashboard className="w-4 h-4 text-emerald-400" />
                <span>My Dashboard</span>
              </Link>
            )}

            {user?.role === 'partner' && (
              <Link
                to="/partner-dashboard"
                className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-1.5 ${
                  isActive('/partner-dashboard') ? 'bg-saffron-500/10 text-saffron-400 font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-900'
                }`}
              >
                <ShieldCheck className="w-4 h-4 text-amber-400" />
                <span>Partner Dashboard</span>
              </Link>
            )}

            {user?.role === 'admin' && (
              <Link
                to="/admin-dashboard"
                className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-1.5 ${
                  isActive('/admin-dashboard') ? 'bg-saffron-500/10 text-saffron-400 font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-900'
                }`}
              >
                <UserCheck className="w-4 h-4 text-indigo-400" />
                <span>Admin Dashboard</span>
              </Link>
            )}
          </nav>

          {/* User Auth & Instant Demo Switcher */}
          <div className="flex items-center gap-2">
            {/* Quick Demo Switcher Buttons */}
            <div className="hidden sm:flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs">
              <span className="text-[10px] text-slate-500 font-bold px-1.5 uppercase">Switch Role:</span>
              <button
                onClick={() => demoSwitchRole('citizen')}
                className={`px-2 py-1 rounded text-xs transition-colors ${
                  user?.role === 'citizen' ? 'bg-saffron-500 text-white font-semibold' : 'text-slate-400 hover:text-white'
                }`}
              >
                Citizen
              </button>
              <button
                onClick={() => demoSwitchRole('partner')}
                className={`px-2 py-1 rounded text-xs transition-colors ${
                  user?.role === 'partner' ? 'bg-sky-500 text-white font-semibold' : 'text-slate-400 hover:text-white'
                }`}
              >
                Partner 🛡️
              </button>
              <button
                onClick={() => demoSwitchRole('admin')}
                className={`px-2 py-1 rounded text-xs transition-colors ${
                  user?.role === 'admin' ? 'bg-indigo-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
                }`}
              >
                Admin
              </button>
            </div>

            {user ? (
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-slate-200 hidden md:inline px-2 py-1 rounded bg-slate-900 border border-slate-800">
                  {user.name.split(' ')[0]} ({user.role})
                </span>
                <button
                  onClick={logout}
                  className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-900 transition-colors"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="px-4 py-2 rounded-lg bg-saffron-500 hover:bg-saffron-600 text-white font-medium text-xs shadow-md transition-colors"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

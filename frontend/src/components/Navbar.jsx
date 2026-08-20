import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LocationBar } from './LocationBar';
import { AIChatDrawer } from './AIChatDrawer';
import { Compass, Search, ShieldCheck, PhoneCall, UserCheck, LayoutDashboard, Bot, LogOut, Grid, Bell, User, Sparkles } from 'lucide-react';

export const Navbar = () => {
  const { user, logout, demoSwitchRole } = useAuth();
  const location = useLocation();
  const [chatOpen, setChatOpen] = useState(false);

  const isActive = (path) => location.pathname === path;

  return (
    <>
      <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 gap-4">
            {/* Brand Logo */}
            <Link to="/" className="flex items-center gap-2.5 shrink-0">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center text-white font-bold shadow-sm">
                <Compass className="w-5 h-5" />
              </div>
              <div>
                <span className="text-lg font-black text-slate-900 tracking-tight flex items-center gap-1.5 font-heading">
                  GSP <span className="text-orange-600 text-xs px-2 py-0.5 rounded-full bg-orange-50 font-bold border border-orange-200">V2</span>
                </span>
                <p className="text-[10px] text-slate-500 font-medium -mt-1 font-sans">Your Government Service Partner</p>
              </div>
            </Link>

            {/* Location Selector */}
            <LocationBar />

            {/* Navigation Items (Exact Mockup Items) */}
            <nav className="hidden md:flex items-center gap-2 text-xs font-semibold">
              <Link
                to="/"
                className={`px-3.5 py-2 rounded-xl transition-all flex items-center gap-1.5 ${
                  isActive('/') ? 'bg-orange-50 text-orange-600 font-bold border border-orange-200' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <span>Home</span>
              </Link>

              <Link
                to="/services/catalog"
                className={`px-3.5 py-2 rounded-xl transition-all flex items-center gap-1.5 ${
                  isActive('/services/catalog') ? 'bg-orange-50 text-orange-600 font-bold border border-orange-200' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <Grid className="w-4 h-4 text-slate-500" />
                <span>All Services</span>
              </Link>

              <button
                onClick={() => setChatOpen(true)}
                className="px-3.5 py-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-all flex items-center gap-1.5"
              >
                <Bot className="w-4 h-4 text-orange-500" />
                <span>AI Assistant</span>
              </button>

              <Link
                to="/dashboard"
                className={`px-3.5 py-2 rounded-xl transition-all flex items-center gap-1.5 ${
                  isActive('/dashboard') ? 'bg-orange-50 text-orange-600 font-bold border border-orange-200' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <span>My Requests</span>
              </Link>

              <Link
                to="/services/catalog"
                className={`px-3.5 py-2 rounded-xl transition-all flex items-center gap-1.5 ${
                  isActive('/updates') ? 'bg-orange-50 text-orange-600 font-bold border border-orange-200' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <span>Updates</span>
              </Link>
            </nav>

            {/* Notification Bell & Profile Avatar */}
            <div className="flex items-center gap-3">
              {/* Bell Icon with Red Badge */}
              <button className="relative p-2 text-slate-600 hover:bg-slate-100 rounded-full transition-colors">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white rounded-full text-[10px] font-extrabold flex items-center justify-center">
                  3
                </span>
              </button>

              {/* Profile Avatar Card */}
              <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
                <div className="w-8 h-8 rounded-full bg-slate-200 overflow-hidden shrink-0 border border-slate-300">
                  <img
                    src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"
                    alt="Sai Kumar Profile"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="hidden sm:block text-left text-xs">
                  <span className="font-bold text-slate-900 block leading-tight">Sai Kumar</span>
                  <span className="text-[10px] text-slate-500 block">Citizen</span>
                </div>
              </div>

              {/* Role Switcher */}
              <div className="hidden lg:flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-[11px]">
                <button
                  onClick={() => demoSwitchRole('CITIZEN')}
                  className={`px-2 py-0.5 rounded-lg text-[10px] ${user?.role === 'CITIZEN' ? 'bg-orange-500 text-white font-bold' : 'text-slate-600'}`}
                >
                  Citizen
                </button>
                <button
                  onClick={() => demoSwitchRole('STAFF')}
                  className={`px-2 py-0.5 rounded-lg text-[10px] ${user?.role === 'STAFF' ? 'bg-emerald-600 text-white font-bold' : 'text-slate-600'}`}
                >
                  Staff 📞
                </button>
                <button
                  onClick={() => demoSwitchRole('PARTNER')}
                  className={`px-2 py-0.5 rounded-lg text-[10px] ${user?.role === 'PARTNER' ? 'bg-sky-600 text-white font-bold' : 'text-slate-600'}`}
                >
                  Partner 🛡️
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Grounded AI Chat Drawer */}
      <AIChatDrawer isOpen={chatOpen} onClose={() => setChatOpen(false)} />
    </>
  );
};

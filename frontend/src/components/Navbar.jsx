import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LocationBar } from './LocationBar';
import { AIChatDrawer } from './AIChatDrawer';
import {
  Compass, Search, ShieldCheck, PhoneCall, UserCheck,
  LayoutDashboard, Bot, LogOut, Grid, Bell, User, Sparkles,
  ChevronDown, FileText, Settings, Bookmark, CheckCircle2,
  LogIn, UserPlus
} from 'lucide-react';

export const Navbar = () => {
  const { user, logout, demoSwitchRole } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const [chatOpen, setChatOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  
  const dropdownRef = useRef(null);

  const isActive = (path) => location.pathname === path;

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setProfileDropdownOpen(false);
        setNotificationsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSignOut = () => {
    logout();
    setProfileDropdownOpen(false);
    navigate('/login');
  };

  const handleRoleNav = (targetRole, path) => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (user.role === targetRole || user.role === 'ADMIN') {
      navigate(path);
    } else {
      // If switching persona in prototype mode
      demoSwitchRole(targetRole.toLowerCase()).then(() => navigate(path));
    }
  };

  return (
    <>
      <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 gap-4">
            {/* Brand Logo (No fake V2 badge) */}
            <Link to="/" className="flex items-center gap-2.5 shrink-0">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center text-white font-bold shadow-sm">
                <Compass className="w-5 h-5" />
              </div>
              <div>
                <span className="text-lg font-black text-slate-900 tracking-tight font-heading">
                  GSP
                </span>
                <p className="text-[10px] text-slate-500 font-medium -mt-1 font-sans">
                  Your Government Service Partner
                </p>
              </div>
            </Link>

            {/* Dynamic Location Selector */}
            <LocationBar />

            {/* Navigation Items */}
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
                className="px-3.5 py-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-all flex items-center gap-1.5 cursor-pointer"
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

            {/* Right Controls: Notifications & Auth/Profile */}
            <div className="flex items-center gap-3" ref={dropdownRef}>
              {/* Notification Bell */}
              <div className="relative">
                <button
                  onClick={() => setNotificationsOpen(!notificationsOpen)}
                  className="relative p-2 text-slate-600 hover:bg-slate-100 rounded-full transition-colors cursor-pointer"
                >
                  <Bell className="w-5 h-5" />
                  <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white rounded-full text-[10px] font-extrabold flex items-center justify-center">
                    2
                  </span>
                </button>

                {/* Notifications Drawer */}
                {notificationsOpen && (
                  <div className="absolute right-0 mt-2 w-72 bg-white rounded-2xl border border-slate-200 shadow-xl p-4 space-y-3 z-50 text-xs animate-in fade-in zoom-in-95">
                    <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                      <span className="font-extrabold text-slate-900">Notifications</span>
                      <span className="text-[10px] text-orange-600 font-bold">2 New</span>
                    </div>
                    <div className="space-y-2">
                      <div className="p-2.5 rounded-xl bg-orange-50 border border-orange-100 space-y-1">
                        <span className="font-bold text-slate-800 block text-[11px]">DL Expiry Alert</span>
                        <p className="text-[10px] text-slate-600">Driving licence expires in 24 days. Contactless renewal available.</p>
                      </div>
                      <div className="p-2.5 rounded-xl bg-indigo-50 border border-indigo-100 space-y-1">
                        <span className="font-bold text-slate-800 block text-[11px]">Birth Certificate Rule Updated</span>
                        <p className="text-[10px] text-slate-600">VRO affidavit process expedited to 5 working days.</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Dynamic Authenticated Profile vs Logged Out State */}
              {user ? (
                <div className="relative">
                  <button
                    onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                    className="flex items-center gap-2 p-1.5 rounded-2xl hover:bg-slate-100 transition-colors border border-transparent hover:border-slate-200 cursor-pointer"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-400 to-amber-500 text-white flex items-center justify-center font-bold text-xs uppercase shadow-xs">
                      {user.name ? user.name[0] : 'U'}
                    </div>
                    <div className="hidden sm:block text-left text-xs">
                      <span className="font-bold text-slate-900 block leading-tight truncate max-w-[100px]">
                        {user.name || 'Citizen'}
                      </span>
                      <span className="text-[10px] text-slate-500 block capitalize">
                        {user.role ? user.role.toLowerCase() : 'Citizen'}
                      </span>
                    </div>
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                  </button>

                  {/* Profile Dropdown Menu */}
                  {profileDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl border border-slate-200 shadow-xl p-2 space-y-1 z-50 text-xs animate-in fade-in zoom-in-95">
                      <div className="p-3 border-b border-slate-100 space-y-0.5">
                        <p className="font-extrabold text-slate-900">{user.name}</p>
                        <p className="text-[10px] text-slate-500 truncate">{user.email || user.phone || 'Citizen Account'}</p>
                      </div>

                      <Link
                        to="/dashboard"
                        onClick={() => setProfileDropdownOpen(false)}
                        className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-700 hover:bg-orange-50 hover:text-orange-600 transition-colors"
                      >
                        <LayoutDashboard className="w-4 h-4 text-slate-400" />
                        <span>My Dashboard & Requests</span>
                      </Link>

                      <Link
                        to="/services/catalog"
                        onClick={() => setProfileDropdownOpen(false)}
                        className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-700 hover:bg-orange-50 hover:text-orange-600 transition-colors"
                      >
                        <Bookmark className="w-4 h-4 text-slate-400" />
                        <span>Saved Services & Schemes</span>
                      </Link>

                      {/* Staff & Admin Links if Authorized */}
                      {(user.role === 'STAFF' || user.role === 'ADMIN') && (
                        <Link
                          to="/staff"
                          onClick={() => setProfileDropdownOpen(false)}
                          className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-emerald-700 bg-emerald-50 hover:bg-emerald-100 font-bold transition-colors"
                        >
                          <UserCheck className="w-4 h-4 text-emerald-600" />
                          <span>Staff Operations Desk</span>
                        </Link>
                      )}

                      {user.role === 'ADMIN' && (
                        <Link
                          to="/admin-dashboard"
                          onClick={() => setProfileDropdownOpen(false)}
                          className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-indigo-700 bg-indigo-50 hover:bg-indigo-100 font-bold transition-colors"
                        >
                          <ShieldCheck className="w-4 h-4 text-indigo-600" />
                          <span>Trust Governance Desk</span>
                        </Link>
                      )}

                      <div className="border-t border-slate-100 my-1" />

                      <button
                        onClick={handleSignOut}
                        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-red-600 hover:bg-red-50 transition-colors font-semibold cursor-pointer"
                      >
                        <LogOut className="w-4 h-4 text-red-500" />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Link
                    to="/login"
                    className="px-4 py-2 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-xs transition-colors flex items-center gap-1.5"
                  >
                    <LogIn className="w-3.5 h-3.5" />
                    <span>Sign In</span>
                  </Link>
                </div>
              )}

              {/* Role Quick Switcher for Staff / Partner Desk Access */}
              <div className="hidden lg:flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-[11px]">
                <button
                  onClick={() => handleRoleNav('CITIZEN', '/')}
                  className={`px-2 py-0.5 rounded-lg text-[10px] cursor-pointer ${user?.role === 'CITIZEN' ? 'bg-orange-500 text-white font-bold' : 'text-slate-600 hover:text-slate-900'}`}
                >
                  Citizen
                </button>
                <button
                  onClick={() => handleRoleNav('STAFF', '/staff')}
                  className={`px-2 py-0.5 rounded-lg text-[10px] cursor-pointer ${user?.role === 'STAFF' ? 'bg-emerald-600 text-white font-bold' : 'text-slate-600 hover:text-slate-900'}`}
                >
                  Staff 📞
                </button>
                <button
                  onClick={() => handleRoleNav('PARTNER', '/partner-dashboard')}
                  className={`px-2 py-0.5 rounded-lg text-[10px] cursor-pointer ${user?.role === 'PARTNER' ? 'bg-sky-600 text-white font-bold' : 'text-slate-600 hover:text-slate-900'}`}
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

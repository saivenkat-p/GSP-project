import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, PhoneCall, MessageSquare, Facebook, Twitter, Youtube, Instagram } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-white border-t border-slate-200 text-slate-700 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
          {/* Logo & Tagline */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-orange-500 text-white flex items-center justify-center font-bold shadow-xs">
                <Compass className="w-5 h-5" />
              </div>
              <span className="text-xl font-black text-slate-900 font-heading">GSP</span>
            </div>

            <p className="text-xs text-slate-500 leading-relaxed max-w-sm font-sans">
              Your trusted partner for government services. Verified information, end-to-end assistance.
            </p>

            <div className="space-y-1">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Follow Us</span>
              <div className="flex items-center gap-2">
                <button className="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-blue-600 flex items-center justify-center transition-colors">
                  <Facebook className="w-3.5 h-3.5" />
                </button>
                <button className="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-sky-500 flex items-center justify-center transition-colors">
                  <Twitter className="w-3.5 h-3.5" />
                </button>
                <button className="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-red-600 flex items-center justify-center transition-colors">
                  <Youtube className="w-3.5 h-3.5" />
                </button>
                <button className="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-pink-600 flex items-center justify-center transition-colors">
                  <Instagram className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-3">
            <h4 className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">Quick Links</h4>
            <ul className="space-y-2 text-slate-600 font-medium">
              <li><Link to="/about" className="hover:text-orange-600">About GSP</Link></li>
              <li><Link to="/how-it-works" className="hover:text-orange-600">How It Works</Link></li>
              <li><Link to="/services/catalog" className="hover:text-orange-600">Service Categories</Link></li>
              <li><Link to="/assistance" className="hover:text-orange-600">Help & Support</Link></li>
              <li><Link to="/contact" className="hover:text-orange-600">Contact Us</Link></li>
            </ul>
          </div>

          {/* For Citizens */}
          <div className="space-y-3">
            <h4 className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">For Citizens</h4>
            <ul className="space-y-2 text-slate-600 font-medium">
              <li><Link to="/services/catalog" className="hover:text-orange-600">All Services</Link></li>
              <li><Link to="/dashboard" className="hover:text-orange-600">Track Request</Link></li>
              <li><Link to="/eligibility" className="hover:text-orange-600">Check Eligibility</Link></li>
              <li><Link to="/documents" className="hover:text-orange-600">Document Guide</Link></li>
              <li><Link to="/payments" className="hover:text-orange-600">Feed & Payments</Link></li>
            </ul>
          </div>

          {/* Need Help Column */}
          <div className="space-y-3">
            <h4 className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">Resources & Help</h4>
            <ul className="space-y-2 text-slate-600 font-medium pb-2">
              <li><Link to="/schemes" className="hover:text-orange-600">Schemes & Benefits</Link></li>
              <li><Link to="/scholarships" className="hover:text-orange-600">Scholarships</Link></li>
            </ul>

            <div className="p-3 rounded-2xl bg-orange-50 border border-orange-100 space-y-2">
              <span className="text-[11px] font-bold text-orange-800 flex items-center gap-1">
                <PhoneCall className="w-3.5 h-3.5 text-orange-600" />
                <span>Need Help?</span>
              </span>
              <p className="text-[11px] text-slate-600">Our support team is here to help you</p>
              <div className="font-extrabold text-slate-900 text-sm">1800-123-4567</div>
              <span className="text-[10px] text-slate-500 block">Toll Free • 24/7 Available</span>
            </div>
          </div>
        </div>

        <div className="pt-8 mt-8 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-500 font-medium">
          <div>© 2026 GSP - Government Services Platform. All rights reserved.</div>
          <div className="flex items-center gap-4">
            <Link to="/privacy" className="hover:underline">Privacy Policy</Link>
            <span>|</span>
            <Link to="/terms" className="hover:underline">Terms of Service</Link>
            <span>|</span>
            <Link to="/disclosure" className="hover:underline">Disclosure</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

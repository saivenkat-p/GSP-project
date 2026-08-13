import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';

// Pages
import { Home } from './pages/Home';
import { ServiceDiscovery } from './pages/ServiceDiscovery';
import { ServiceDetails } from './pages/ServiceDetails';
import { Assistance } from './pages/Assistance';
import { CitizenDashboard } from './pages/CitizenDashboard';
import { PartnerDashboard } from './pages/PartnerDashboard';
import { AdminDashboard } from './pages/AdminDashboard';
import { ApplicationTracking } from './pages/ApplicationTracking';
import { RejectionAssistance } from './pages/RejectionAssistance';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

export function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col justify-between bg-slate-950 text-slate-100 selection:bg-saffron-500 selection:text-white">
          <div>
            <Navbar />
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/discover" element={<ServiceDiscovery />} />
                <Route path="/services/:id" element={<ServiceDetails />} />
                <Route path="/assistance" element={<Assistance />} />
                <Route path="/dashboard" element={<CitizenDashboard />} />
                <Route path="/partner-dashboard" element={<PartnerDashboard />} />
                <Route path="/admin-dashboard" element={<AdminDashboard />} />
                <Route path="/tracking/:id" element={<ApplicationTracking />} />
                <Route path="/rejection-help/:id" element={<RejectionAssistance />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
              </Routes>
            </main>
          </div>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

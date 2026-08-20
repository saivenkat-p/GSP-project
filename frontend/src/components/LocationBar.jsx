import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import { MapPin, Navigation, ChevronDown, Check, X } from 'lucide-react';

export const LocationBar = () => {
  const { selectedState = 'AP', setSelectedState, selectedDistrict = 'AP-NTR', setSelectedDistrict } = useAuth();
  
  const [tree, setTree] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [activeMandal, setActiveMandal] = useState('Vijayawada Urban');
  const [gpsLoading, setGpsLoading] = useState(false);
  const [gpsMessage, setGpsMessage] = useState('');

  useEffect(() => {
    fetchTree();
  }, []);

  const fetchTree = async () => {
    try {
      const res = await apiService.getLocationTree();
      const treeData = res.data || [];
      setTree(treeData);
      
      if (treeData.length > 0) {
        const firstState = treeData[0];
        if (!selectedState || selectedState === 'Andhra Pradesh') setSelectedState(firstState.id);
        if (firstState.districts && firstState.districts.length > 0) {
          const firstDist = firstState.districts[0];
          if (!selectedDistrict || selectedDistrict === 'NTR / Vijayawada') setSelectedDistrict(firstDist.id);
          if (firstDist.mandals && firstDist.mandals.length > 0) {
            setActiveMandal(firstDist.mandals[0].name);
          }
        }
      }
    } catch (err) {
      console.error('Error fetching dynamic location tree:', err);
    }
  };

  const handleUseGPS = () => {
    setGpsLoading(true);
    setGpsMessage('');
    if (!navigator.geolocation) {
      setGpsMessage('Geolocation is not supported by your browser. Please select manually.');
      setGpsLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGpsLoading(false);
        if (tree.length > 0 && tree[0].districts && tree[0].districts.length > 0) {
          const dist = tree[0].districts[0];
          setSelectedDistrict(dist.id);
          if (dist.mandals && dist.mandals.length > 0) {
            setActiveMandal(dist.mandals[0].name);
          }
        }
        setGpsMessage('📍 Location detected automatically via GPS');
      },
      (err) => {
        setGpsLoading(false);
        setGpsMessage('GPS permission denied. Please select your location manually below.');
      }
    );
  };

  // Safe Fallback Derivation
  const currentStateObj = (tree || []).find((s) => s.id === selectedState || s.name === selectedState) || tree[0] || { id: 'AP', name: 'Andhra Pradesh', districts: [] };
  const availableDistricts = currentStateObj?.districts || [];

  const currentDistrictObj = (availableDistricts || []).find((d) => d.id === selectedDistrict || d.name === selectedDistrict) || availableDistricts[0] || { id: 'AP-NTR', name: 'Vijayawada Urban, Andhra Pradesh', mandals: [] };
  const availableMandals = currentDistrictObj?.mandals || [];

  return (
    <>
      <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200 text-xs text-slate-700 font-medium">
        <MapPin className="w-4 h-4 text-orange-500 shrink-0" />
        <div className="flex items-center gap-1 cursor-pointer" onClick={() => setShowModal(true)}>
          <span className="font-bold text-slate-900 hover:underline">
            {currentDistrictObj?.name || 'Vijayawada Urban, Andhra Pradesh'} {activeMandal ? `(${activeMandal})` : ''}
          </span>
          <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
        </div>
      </div>

      {/* DYNAMIC LOCATION SELECTION MODAL */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
          <div className="bg-white w-full max-w-lg p-6 rounded-3xl border border-slate-200 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <MapPin className="w-5 h-5 text-orange-500" />
                <h3 className="text-base font-bold text-slate-900 font-heading">Location Hierarchy Selector</h3>
              </div>
              <button onClick={() => setShowModal(false)} className="p-1 rounded-lg hover:bg-slate-100 text-slate-400">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* GPS Auto-Detect Button */}
            <div className="p-4 rounded-2xl bg-orange-50 border border-orange-200 space-y-2">
              <button
                onClick={handleUseGPS}
                disabled={gpsLoading}
                className="w-full py-2.5 px-4 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs flex items-center justify-center gap-2 transition-colors shadow-xs"
              >
                <Navigation className={`w-4 h-4 ${gpsLoading ? 'animate-spin' : ''}`} />
                <span>{gpsLoading ? 'Detecting GPS Coordinates...' : 'Use My Current Location (GPS)'}</span>
              </button>
              {gpsMessage && <p className="text-[11px] text-orange-800 text-center font-medium">{gpsMessage}</p>}
            </div>

            <div className="relative text-center text-xs text-slate-400 font-semibold uppercase tracking-wider">
              <span>— OR Select Manually —</span>
            </div>

            {/* Dynamic Hierarchy Selectors */}
            <div className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-600 mb-1 font-semibold">1. State</label>
                <select
                  value={selectedState}
                  onChange={(e) => {
                    const stId = e.target.value;
                    setSelectedState(stId);
                    const stObj = (tree || []).find((s) => s.id === stId);
                    if (stObj && stObj.districts && stObj.districts.length > 0) {
                      setSelectedDistrict(stObj.districts[0].id);
                      if (stObj.districts[0].mandals && stObj.districts[0].mandals.length > 0) {
                        setActiveMandal(stObj.districts[0].mandals[0].name);
                      }
                    }
                  }}
                  className="w-full bg-slate-50 text-slate-900 border border-slate-200 rounded-xl p-2.5 font-medium focus:outline-none focus:border-orange-500"
                >
                  {(tree || []).map((st) => (
                    <option key={st.id} value={st.id}>
                      {st.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-600 mb-1 font-semibold">2. District</label>
                <select
                  value={selectedDistrict}
                  onChange={(e) => {
                    const distId = e.target.value;
                    setSelectedDistrict(distId);
                    const distObj = (availableDistricts || []).find((d) => d.id === distId);
                    if (distObj && distObj.mandals && distObj.mandals.length > 0) {
                      setActiveMandal(distObj.mandals[0].name);
                    }
                  }}
                  className="w-full bg-slate-50 text-slate-900 border border-slate-200 rounded-xl p-2.5 font-medium focus:outline-none focus:border-orange-500"
                >
                  {(availableDistricts || []).map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-600 mb-1 font-semibold">3. Mandal / Municipality</label>
                <select
                  value={activeMandal}
                  onChange={(e) => setActiveMandal(e.target.value)}
                  className="w-full bg-slate-50 text-slate-900 border border-slate-200 rounded-xl p-2.5 font-medium focus:outline-none focus:border-orange-500"
                >
                  {(availableMandals || []).map((m) => (
                    <option key={m.id} value={m.name}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setShowModal(false)}
                className="px-6 py-2.5 rounded-xl bg-emerald-600 text-white font-bold text-xs flex items-center gap-1 hover:bg-emerald-700 shadow-xs"
              >
                <Check className="w-4 h-4" />
                <span>Apply Location Filter</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedState, setSelectedState] = useState('AP');
  const [selectedDistrict, setSelectedDistrict] = useState('AP-NTR');

  useEffect(() => {
    checkLoggedInUser();
  }, []);

  const checkLoggedInUser = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const res = await apiService.getMe();
      setUser(res.data);
      if (res.data.district_id) setSelectedDistrict(res.data.district_id);
      if (res.data.state_id) setSelectedState(res.data.state_id);
    } catch (err) {
      console.error('Session validation error:', err);
      localStorage.removeItem('token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const res = await apiService.login({ email, password });
    localStorage.setItem('token', res.data.access_token);
    setUser(res.data.user);
    return res.data;
  };

  const register = async (userData) => {
    const res = await apiService.register(userData);
    localStorage.setItem('token', res.data.access_token);
    setUser(res.data.user);
    return res.data;
  };

  const demoSwitchRole = async (role) => {
    try {
      setLoading(true);
      const res = await apiService.demoSwitch(role);
      localStorage.setItem('token', res.data.access_token);
      setUser(res.data.user);
      return res.data;
    } catch (err) {
      console.error('Demo role switch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        demoSwitchRole,
        selectedState,
        setSelectedState,
        selectedDistrict,
        setSelectedDistrict,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

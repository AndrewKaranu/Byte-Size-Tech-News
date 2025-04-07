import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import AdminLogin from './AdminLogin';
import Dashboard from './Dashboard';
import ArticleManagement from './ArticleManagement';
import NewsletterPreview from './NewsletterPreview';
import Settings from './Settings';
import './Styles/AdminStyles.css';   

const AdminPanel = () => {
  const [adminKey, setAdminKey] = useState(sessionStorage.getItem('adminKey'));
  const navigate = useNavigate();

  useEffect(() => {
    const storedKey = sessionStorage.getItem('adminKey');
    if (storedKey) {
      setAdminKey(storedKey);
    } else {
      // Redirect to login if no admin key exists
      navigate('/admin/login');
    }
  }, [navigate]);

  const handleLogin = (key) => {
    sessionStorage.setItem('adminKey', key);
    setAdminKey(key);
    navigate('/admin/dashboard');
  };

  const handleLogout = () => {
    sessionStorage.removeItem('adminKey');
    setAdminKey(null);
    navigate('/admin/login');
  };

  const returnToDesktop = () => {
    window.location.href = '/';
  };

  return (
    <div className="admin-panel">
      <Routes>
        <Route path="/login" element={<AdminLogin onLogin={handleLogin} onBack={returnToDesktop} />} />
        
        <Route
          path="/dashboard"
          element={
            adminKey ? (
              <Dashboard adminKey={adminKey} onLogout={handleLogout} />
            ) : (
              <Navigate to="/admin/login" replace />
            )
          }
        />
        
        <Route
          path="/articles"
          element={
            adminKey ? (
              <ArticleManagement adminKey={adminKey} onLogout={handleLogout} />
            ) : (
              <Navigate to="/admin/login" replace />
            )
          }
        />
        
        <Route
          path="/articles/:batchId"
          element={
            adminKey ? (
              <ArticleManagement adminKey={adminKey} onLogout={handleLogout} />
            ) : (
              <Navigate to="/admin/login" replace />
            )
          }
        />
        
        <Route
          path="/preview/:batchId"
          element={
            adminKey ? (
              <NewsletterPreview adminKey={adminKey} />
            ) : (
              <Navigate to="/admin/login" replace />
            )
          }
        />
        
        <Route
          path="/settings"
          element={
            adminKey ? (
              <Settings adminKey={adminKey} onLogout={handleLogout} />
            ) : (
              <Navigate to="/admin/login" replace />
            )
          }
        />
        
        <Route
          path="/"
          element={<Navigate to={adminKey ? "/admin/dashboard" : "/admin/login"} replace />}
        />
      </Routes>
    </div>
  );
};

export default AdminPanel;
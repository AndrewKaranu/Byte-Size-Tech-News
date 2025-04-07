import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import AdminLogin from './AdminLogin';
import AdminLayout from './AdminLayout';
import Dashboard from './Dashboard';
import ArticleManagement from './ArticleManagement';
import NewsletterPreview from './NewsletterPreview';
import Settings from './Settings';

const AdminMain = () => {
  const [adminKey, setAdminKey] = useState(sessionStorage.getItem('adminKey'));
  const navigate = useNavigate();

  useEffect(() => {
    // Check if admin key is in session storage
    const storedKey = sessionStorage.getItem('adminKey');
    if (storedKey) {
      setAdminKey(storedKey);
    }
  }, []);

  const handleLogin = (key) => {
    setAdminKey(key);
    navigate('/admin/dashboard');
  };

  const handleLogout = () => {
    sessionStorage.removeItem('adminKey');
    setAdminKey(null);
    navigate('/admin');
  };

  if (!adminKey) {
    return <AdminLogin onLogin={handleLogin} />;
  }

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/admin/dashboard" replace />} />
      
      <Route
        path="/dashboard"
        element={
          <AdminLayout onLogout={handleLogout}>
            <Dashboard />
          </AdminLayout>
        }
      />
      
      <Route
        path="/articles"
        element={
          <AdminLayout onLogout={handleLogout}>
            <ArticleManagement />
          </AdminLayout>
        }
      />
      
      <Route
        path="/articles/:batchId"
        element={
          <AdminLayout onLogout={handleLogout}>
            <ArticleManagement />
          </AdminLayout>
        }
      />
      
      <Route
        path="/preview/:batchId"
        element={<NewsletterPreview />}
      />
      
      <Route
        path="/settings"
        element={
          <AdminLayout onLogout={handleLogout}>
            <Settings />
          </AdminLayout>
        }
      />
      
      <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
    </Routes>
  );
};

export default AdminMain;
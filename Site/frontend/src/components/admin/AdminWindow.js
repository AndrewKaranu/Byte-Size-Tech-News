import React, { useState } from 'react';
import './Styles/AdminStyles.css';   

import AdminLogin from './admin/AdminLogin';
import Dashboard from './admin/Dashboard';
import ArticleManagement from './admin/ArticleManagement';
import Settings from './admin/Settings';

const Admin = ({ onClose }) => {
  const [adminKey, setAdminKey] = useState(sessionStorage.getItem('adminKey'));
  const [currentView, setCurrentView] = useState('dashboard');
  const [activeBatchId, setActiveBatchId] = useState(null);

  const handleLogin = (key) => {
    sessionStorage.setItem('adminKey', key);
    setAdminKey(key);
  };

  const handleLogout = () => {
    sessionStorage.removeItem('adminKey');
    setAdminKey(null);
  };

  const navigateToView = (view, batchId = null) => {
    setCurrentView(view);
    if (batchId) {
      setActiveBatchId(batchId);
    }
  };

  return (
    <div className="window admin-window">
      <div className="window-title-bar">
        <div className="window-title">Admin Panel</div>
        <div className="window-controls">
          <button className="window-control close" onClick={onClose}>X</button>
        </div>
      </div>
      <div className="window-content">
        {!adminKey ? (
          <AdminLogin onLogin={handleLogin} />
        ) : (
          <div className="admin-container">
            <div className="admin-sidebar">
              <div className="admin-logo">
                <h2>Byte Sized Tech News</h2>
                <p>Admin Panel</p>
              </div>
              
              <nav className="admin-nav">
                <ul>
                  <li className={currentView === 'dashboard' ? 'active' : ''}>
                    <a href="#" onClick={() => navigateToView('dashboard')}>Dashboard</a>
                  </li>
                  <li className={currentView === 'articles' ? 'active' : ''}>
                    <a href="#" onClick={() => navigateToView('articles')}>Article Management</a>
                  </li>
                  <li className={currentView === 'settings' ? 'active' : ''}>
                    <a href="#" onClick={() => navigateToView('settings')}>Settings</a>
                  </li>
                </ul>
              </nav>
              
              <div className="admin-sidebar-footer">
                <button className="admin-button secondary" onClick={handleLogout}>
                  Logout
                </button>
              </div>
            </div>
            
            <div className="admin-content">
              <div className="admin-content-inner">
                {currentView === 'dashboard' && (
                  <Dashboard 
                    navigateToArticles={(batchId) => navigateToView('articles', batchId)} 
                  />
                )}
                
                {currentView === 'articles' && (
                  <ArticleManagement 
                    initialBatchId={activeBatchId}
                    navigateToDashboard={() => navigateToView('dashboard')}
                  />
                )}
                
                {currentView === 'settings' && (
                  <Settings />
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin;
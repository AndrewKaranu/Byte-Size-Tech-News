import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Styles/AdminStyles.css';   


const AdminLayout = ({ children, onLogout }) => {
  const location = useLocation();
  
  return (
    <div className="admin-container">
      <div className="admin-sidebar">
        <div className="admin-logo">
          <h2>Byte Sized Tech News</h2>
          <p>Admin Panel</p>
        </div>
        
        <nav className="admin-nav">
          <ul>
            <li className={location.pathname === '/admin/dashboard' ? 'active' : ''}>
              <Link to="/admin/dashboard">Dashboard</Link>
            </li>
            <li className={location.pathname === '/admin/articles' ? 'active' : ''}>
              <Link to="/admin/articles">Article Management</Link>
            </li>
            <li className={location.pathname === '/admin/users' ? 'active' : ''}>
              <Link to="/admin/users">Users</Link>
            </li>
            <li className={location.pathname === '/admin/settings' ? 'active' : ''}>
              <Link to="/admin/settings">Settings</Link>
            </li>
          </ul>
        </nav>
        
        <div className="admin-sidebar-footer">
          <button className="admin-button secondary" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>
      
      <div className="admin-content">
        {/* Top page navigation and logout for all admin pages */}
        <div className="admin-top-nav" style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div className="admin-page-nav">
            <Link to="/admin/dashboard" className={location.pathname.startsWith('/admin/dashboard') ? 'active' : ''} style={{ marginRight: '15px' }}>
              Dashboard
            </Link>
            <Link to="/admin/articles" className={location.pathname.startsWith('/admin/articles') ? 'active' : ''} style={{ marginRight: '15px' }}>
              Articles
            </Link>
            <Link to="/admin/users" className={location.pathname.startsWith('/admin/users') ? 'active' : ''} style={{ marginRight: '15px' }}>
              Users
            </Link>
            <Link to="/admin/settings" className={location.pathname.startsWith('/admin/settings') ? 'active' : ''}>
              Settings
            </Link>
          </div>
          <button className="admin-button secondary" onClick={onLogout}>
            Logout
          </button>
        </div>
        <div className="admin-content-inner">
          {children}
        </div>
      </div>
    </div>
  );
};

export default AdminLayout;
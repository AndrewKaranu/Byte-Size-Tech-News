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
        <div className="admin-content-inner">
          {children}
        </div>
      </div>
    </div>
  );
};

export default AdminLayout;
import React, { useState } from 'react';
import './Styles/AdminStyles.css';

const AdminLogin = ({ onLogin }) => {
  const [adminKey, setAdminKey] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!adminKey) {
      setError('Please enter your admin key');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // Validate admin key by making a simple authenticated request
      const response = await fetch('http://localhost:5000/admin/verify', {
        method: 'GET',
        headers: {
          'Admin-Key': adminKey,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      console.log("Response status:", response.status);
      console.log("Entered admin key:", adminKey);
      console.log("Expected key:", "admin-dev-key-2025");
      console.log("Keys match:", adminKey === "admin-dev-key-2025");
      
      if (response.ok) {
        sessionStorage.setItem('adminKey', adminKey);
        onLogin(adminKey);
      } else {
        const errorData = await response.text();
        console.error("Server response:", errorData);
        setError('Invalid admin key');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-login-container">
      <div className="admin-login-card">
        <h1>Byte Sized Tech News</h1>
        <h2>Admin Access</h2>
        
        {error && <div className="admin-error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="adminKey">Admin Key</label>
            <input 
              type="password"
              id="adminKey"
              value={adminKey}
              onChange={(e) => setAdminKey(e.target.value)}
              placeholder="Enter your admin key"
            />
          </div>
          
          <button 
            type="submit" 
            className="admin-button primary" 
            disabled={loading}
          >
            {loading ? 'Verifying...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AdminLogin;
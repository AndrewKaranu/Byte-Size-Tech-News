import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Styles/AdminStyles.css';   


const Settings = () => {
  const navigate = useNavigate();
  const [settings, setSettings] = useState({
    collection_time: '05:00',
    admin_review_time: '14:00',
    send_time: '16:00',
    admin_email: '',
    auto_approve: false
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const adminKey = sessionStorage.getItem('adminKey');
    if (!adminKey) {
      navigate('/admin');
      return;
    }

    const fetchSettings = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:5000/admin/settings', {
          headers: { 'Admin-Key': adminKey }
        });
        
        setSettings(response.data);
      } catch (error) {
        console.error('Error fetching settings:', error);
        setError('Failed to load settings');
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, [navigate]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const adminKey = sessionStorage.getItem('adminKey');
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      await axios.post('http://localhost:5000/admin/settings', settings, {
        headers: { 'Admin-Key': adminKey }
      });
      
      setSuccess('Settings updated successfully');
    } catch (error) {
      console.error('Error updating settings:', error);
      setError('Failed to update settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <p>Loading settings...</p>
      </div>
    );
  }

  return (
    <div className="admin-settings">
      <div className="admin-header">
        <h1>Newsletter Settings</h1>
      </div>
      
      {error && <div className="admin-error-message">{error}</div>}
      {success && <div className="admin-success-message">{success}</div>}
      
      <div className="admin-card">
        <form onSubmit={handleSubmit}>
          <div className="admin-form-group">
            <label htmlFor="collection_time">Article Collection Time</label>
            <input
              type="time"
              id="collection_time"
              name="collection_time"
              value={settings.collection_time}
              onChange={handleChange}
              required
            />
            <p className="admin-field-help">
              Time of day when articles are automatically collected.
            </p>
          </div>
          
          <div className="admin-form-group">
            <label htmlFor="admin_review_time">Admin Review Deadline</label>
            <input
              type="time"
              id="admin_review_time"
              name="admin_review_time"
              value={settings.admin_review_time}
              onChange={handleChange}
              required
            />
            <p className="admin-field-help">
              Time of day when a reminder is sent if no article selection has been made.
            </p>
          </div>
          
          <div className="admin-form-group">
            <label htmlFor="send_time">Newsletter Send Time</label>
            <input
              type="time"
              id="send_time"
              name="send_time"
              value={settings.send_time}
              onChange={handleChange}
              required
            />
            <p className="admin-field-help">
              Time of day when newsletters are automatically sent out.
            </p>
          </div>
          
          <div className="admin-form-group">
            <label htmlFor="admin_email">Admin Email</label>
            <input
              type="email"
              id="admin_email"
              name="admin_email"
              value={settings.admin_email}
              onChange={handleChange}
              required
              placeholder="admin@example.com"
            />
            <p className="admin-field-help">
              Email address for admin notifications and previews.
            </p>
          </div>
          
          <div className="admin-form-group checkbox">
            <input
              type="checkbox"
              id="auto_approve"
              name="auto_approve"
              checked={settings.auto_approve}
              onChange={handleChange}
            />
            <label htmlFor="auto_approve">Auto-approve newsletters</label>
            <p className="admin-field-help">
              When enabled, newsletters will be automatically approved and sent at the specified send time.
            </p>
          </div>
          
          <div className="admin-form-actions">
            <button 
              type="submit" 
              className="admin-button primary" 
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Settings;
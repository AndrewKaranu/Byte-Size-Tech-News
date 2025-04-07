import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Styles/AdminStyles.css';   


const Dashboard = () => {
  const [latestBatch, setLatestBatch] = useState(null);
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const adminKey = sessionStorage.getItem('adminKey');
    if (!adminKey) {
      navigate('/admin');
      return;
    }

    // Update the fetchDashboardData function:
// Update the fetchDashboardData function:
const fetchDashboardData = async () => {
  try {
    setLoading(true);

    // Fetch latest batch - REMOVE Content-Type header for GET request
    const batchesResponse = await axios.get('http://localhost:5000/admin/batches', {
        headers: {
            'Admin-Key': adminKey,
            'Accept': 'application/json'
        }
    });

    if (batchesResponse.data.batches && batchesResponse.data.batches.length > 0) {
      setLatestBatch(batchesResponse.data.batches[0]);
    }

    // Fetch settings - REMOVE Content-Type header for GET request
    const settingsResponse = await axios.get('http://localhost:5000/admin/settings', {
      headers: {
        'Admin-Key': adminKey,
        'Accept': 'application/json'
      }
    });

    setSettings(settingsResponse.data);

  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    setError('Failed to load dashboard data');
  } finally {
    setLoading(false);
  }
};

    fetchDashboardData();
  }, [navigate]);

  const collectNewArticles = async () => {
    const adminKey = sessionStorage.getItem('adminKey');
    try {
      setLoading(true);
      const response = await axios.post('http://localhost:5000/admin/collect-articles', {}, {
        headers: { 'Admin-Key': adminKey }
      });
      
      alert('Articles collected successfully!');
      window.location.reload(); // Refresh to see the new batch
    } catch (error) {
      console.error('Error collecting articles:', error);
      setError('Failed to collect articles');
    } finally {
      setLoading(false);
    }
  };

  // Update your createDummyBatch function:

  const createDummyBatch = async () => {
    const adminKey = sessionStorage.getItem('adminKey');
try {
    setLoading(true);
    const response = await fetch('http://localhost:5000/admin/test/create-dummy-batch', {
    method: 'POST',
    headers: {
        'Admin-Key': adminKey,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
    });

  if (response.ok) {
    const data = await response.json();
    alert(`Dummy batch created successfully! Batch ID: ${data.batch_id}`);
    window.location.reload();
  } else {
    const errorText = await response.text();
    console.error('Error response:', errorText);
    setError('Failed to create dummy batch');
  }
} catch (error) {
  console.error('Error creating dummy batch:', error);
  setError('Failed to create dummy batch');
} finally {
  setLoading(false);
}
};

  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return 'N/A';
    const date = new Date(dateTimeStr);
    return date.toLocaleString();
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>Newsletter Dashboard</h1>
        <button className="admin-button primary" onClick={collectNewArticles}>
          Collect New Articles
        </button>
        <button 
            className="admin-button secondary" 
            onClick={createDummyBatch}
            style={{ marginLeft: '10px' }}
          >
            Create Dummy Batch
          </button>
      </div>
      
      {error && <div className="admin-error-message">{error}</div>}
      
      <div className="admin-dashboard-grid">
        <div className="admin-card">
          <h2>Latest Newsletter Batch</h2>
          {latestBatch ? (
            <div>
              <p><strong>Batch ID:</strong> {latestBatch.id}</p>
              <p><strong>Created:</strong> {formatDateTime(latestBatch.date_created)}</p>
              <p><strong>Status:</strong> {latestBatch.is_finalized ? 'Finalized' : 'Draft'}</p>
              <p><strong>Approved:</strong> {latestBatch.admin_approved ? 'Yes' : 'No'}</p>
              <p><strong>Sent:</strong> {latestBatch.is_sent ? 'Yes' : 'No'}</p>
              
              <div className="admin-card-actions">
                <button 
                  className="admin-button secondary"
                  onClick={() => navigate(`/admin/articles/${latestBatch.id}`)}
                >
                  Manage Articles
                </button>
              </div>
            </div>
          ) : (
            <p>No newsletter batches found.</p>
          )}
        </div>
        
        <div className="admin-card">
          <h2>Newsletter Schedule</h2>
          {settings ? (
            <div>
              <p><strong>Article Collection:</strong> {settings.collection_time}</p>
              <p><strong>Admin Review Deadline:</strong> {settings.admin_review_time}</p>
              <p><strong>Newsletter Dispatch:</strong> {settings.send_time}</p>
              <p><strong>Admin Email:</strong> {settings.admin_email || 'Not set'}</p>
              <p><strong>Auto-approve:</strong> {settings.auto_approve ? 'Enabled' : 'Disabled'}</p>
              
              <div className="admin-card-actions">
                <button 
                  className="admin-button secondary"
                  onClick={() => navigate('/admin/settings')}
                >
                  Update Settings
                </button>
              </div>
            </div>
          ) : (
            <p>No settings found.</p>
          )}
        </div>
      </div>
      
      <div className="admin-card">
        <h2>Recent Batches</h2>
        <button 
          className="admin-button secondary"
          onClick={() => navigate('/admin/articles')}
        >
          View All Batches
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
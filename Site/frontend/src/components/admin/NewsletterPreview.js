import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './Styles/AdminStyles.css';   


const NewsletterPreview = () => {
  const { batchId } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [preview, setPreview] = useState('');

  useEffect(() => {
    const adminKey = sessionStorage.getItem('adminKey');
    if (!adminKey || !batchId) {
      setError('Invalid access');
      setLoading(false);
      return;
    }

    const fetchPreview = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`http://localhost:5000/admin/preview/${batchId}`, {
          headers: { 'Admin-Key': adminKey }
        });
        
        setPreview(response.data.email_content);
      } catch (error) {
        console.error('Error fetching preview:', error);
        setError('Failed to load newsletter preview');
      } finally {
        setLoading(false);
      }
    };

    fetchPreview();
  }, [batchId]);

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <p>Loading preview...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-error-container">
        <h2>Error</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="admin-preview-container">
      <div className="admin-preview-header">
        <h1>Newsletter Preview</h1>
        <button onClick={() => window.print()} className="admin-button secondary">
          Print Preview
        </button>
      </div>
      
      <div className="admin-preview-content">
        <div dangerouslySetInnerHTML={{ __html: preview }} />
      </div>
    </div>
  );
};

export default NewsletterPreview;
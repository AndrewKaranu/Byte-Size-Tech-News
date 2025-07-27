import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Styles/AdminStyles.css';

const Users = ({ adminKey, onLogout }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingUserId, setEditingUserId] = useState(null);
  const [editData, setEditData] = useState({});
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const key = sessionStorage.getItem('adminKey');
    if (!key) {
      navigate('/admin');
      return;
    }
    fetchUsers();
  }, [navigate]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/admin/users', {
        headers: { 'Admin-Key': sessionStorage.getItem('adminKey') }
      });
      setUsers(response.data.users);
    } catch (err) {
      console.error('Error fetching users:', err);
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleEditClick = (user) => {
    setEditingUserId(user.id);
    setEditData({ email: user.email, language: user.language, is_admin: user.is_admin });
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setEditData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSaveClick = async (id) => {
    setLoading(true);
    try {
      await axios.put(
        `http://localhost:5000/admin/users/${id}`,
        editData,
        { headers: { 'Admin-Key': sessionStorage.getItem('adminKey') } }
      );
      setEditingUserId(null);
      fetchUsers();
    } catch (err) {
      console.error('Error updating user:', err);
      setError('Failed to update user');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelClick = () => {
    setEditingUserId(null);
    setError('');
  };

  return (
    <div className="admin-users">
      <div className="admin-header">
        <h1>Manage Users</h1>
      </div>
      {error && <div className="admin-error-message">{error}</div>}
      {loading ? (
        <div className="admin-loading">
          <div className="spinner"></div>
          <p>Loading users...</p>
        </div>
      ) : (
        <table className="admin-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ borderBottom: '1px solid #ddd', padding: '8px' }}>ID</th>
              <th style={{ borderBottom: '1px solid #ddd', padding: '8px' }}>Email</th>
              <th style={{ borderBottom: '1px solid #ddd', padding: '8px' }}>Language</th>
              <th style={{ borderBottom: '1px solid #ddd', padding: '8px' }}>Admin</th>
              <th style={{ borderBottom: '1px solid #ddd', padding: '8px' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td style={{ borderBottom: '1px solid #eee', padding: '8px' }}>{user.id}</td>
                <td style={{ borderBottom: '1px solid #eee', padding: '8px' }}>
                  {editingUserId === user.id ? (
                    <input
                      type="email"
                      name="email"
                      value={editData.email}
                      onChange={handleChange}
                    />
                  ) : (
                    user.email
                  )}
                </td>
                <td style={{ borderBottom: '1px solid #eee', padding: '8px' }}>
                  {editingUserId === user.id ? (
                    <input
                      type="text"
                      name="language"
                      value={editData.language}
                      onChange={handleChange}
                    />
                  ) : (
                    user.language
                  )}
                </td>
                <td style={{ borderBottom: '1px solid #eee', padding: '8px', textAlign: 'center' }}>
                  {editingUserId === user.id ? (
                    <input
                      type="checkbox"
                      name="is_admin"
                      checked={editData.is_admin}
                      onChange={handleChange}
                    />
                  ) : (
                    user.is_admin ? 'Yes' : 'No'
                  )}
                </td>
                <td style={{ borderBottom: '1px solid #eee', padding: '8px' }}>
                  {editingUserId === user.id ? (
                    <>
                      <button
                        className="admin-button primary small"
                        onClick={() => handleSaveClick(user.id)}
                      >
                        Save
                      </button>
                      <button
                        className="admin-button secondary small"
                        style={{ marginLeft: '8px' }}
                        onClick={handleCancelClick}
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button
                      className="admin-button secondary small"
                      onClick={() => handleEditClick(user)}
                    >
                      Edit
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Users;

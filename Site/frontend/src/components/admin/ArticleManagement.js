import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Styles/AdminStyles.css';

const ArticleManagement = () => {
  const { batchId } = useParams();
  const navigate = useNavigate();

  const [batches, setBatches] = useState([]);
  const [currentBatch, setCurrentBatch] = useState(null);
  const [articles, setArticles] = useState(null);
  const [selectedArticles, setSelectedArticles] = useState({}); // State to hold selected articles
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1); // Pagination state
  const articlesPerPage = 10; // Articles per page
  const [expandedTopics, setExpandedTopics] = useState({}); // Track expanded/collapsed state for topics

  // For custom article
  const [showCustomForm, setShowCustomForm] = useState(false);
  const [customArticle, setCustomArticle] = useState({
    title: '',
    link: '',
    summary: '',
    topic: ''
  });

  useEffect(() => {
    const adminKey = sessionStorage.getItem('adminKey');
    if (!adminKey) {
      navigate('/admin');
      return;
    }

    const fetchBatches = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:5000/admin/batches', {
          headers: { 'Admin-Key': adminKey }
        });
        setBatches(response.data.batches);

        // If a batchId is provided, fetch that batch's articles
        if (batchId) {
          const selectedBatch = response.data.batches.find(b => b.id === parseInt(batchId));
          setCurrentBatch(selectedBatch);
          await fetchArticles(batchId);
        }
      } catch (error) {
        console.error('Error fetching batches:', error);
        setError('Failed to load batches');
      } finally {
        setLoading(false);
      }
    };

    fetchBatches();
  }, [batchId, navigate]);

  useEffect(() => {
    // Add warning button style
    const style = document.createElement('style');
    style.innerHTML = `
      .admin-button.warning {
        background-color: #e74c3c;
        color: white;
      }
      .admin-button.warning:hover {
        background-color: #c0392b;
      }
      .admin-button.warning:disabled {
        background-color: #f6b9b3;
      }
    `;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, []);

  const fetchArticles = async (id) => {
    const adminKey = sessionStorage.getItem('adminKey');
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:5000/admin/articles/${id}`, {
        headers: { 'Admin-Key': adminKey }
      });
      setArticles(response.data);

      // Fetch selected articles and update state
      const selected = await fetchSelectedArticles(id);
      setSelectedArticles(selected);

    } catch (error) {
      console.error('Error fetching articles:', error);
      setError('Failed to load articles');
    } finally {
      setLoading(false);
    }
  };

  const fetchSelectedArticles = async (batchId) => {
    const adminKey = sessionStorage.getItem('adminKey');
    try {
      const response = await axios.get(`http://localhost:5000/admin/selected-articles/${batchId}`, {
        headers: { 'Admin-Key': adminKey }
      });
      return response.data.selected_articles;
    } catch (error) {
      console.error('Error fetching selected articles:', error);
      setError('Failed to load selected articles');
      return {};
    }
  };

  const handleBatchSelect = (batch) => {
    setCurrentBatch(batch);
    navigate(`/admin/articles/${batch.id}`);
  };

  const handleAutoSelect = async () => {
    if (!currentBatch) return;

    const adminKey = sessionStorage.getItem('adminKey');
    try {
      setLoading(true);
      const response = await axios.post(
        `http://localhost:5000/admin/auto-select/${currentBatch.id}`,
        {},
        { headers: { 'Admin-Key': adminKey } }
      );
      alert('Articles auto-selected successfully');
      await fetchArticles(currentBatch.id);
    } catch (error) {
      console.error('Error auto-selecting articles:', error);
      setError('Failed to auto-select articles');
    } finally {
      setLoading(false);
    }
  };

  const handleArticleSelect = async (article, topic) => {
    if (!currentBatch) return;
  
    const adminKey = sessionStorage.getItem('adminKey');
    const selectedTopic = topic || 'General';
  
    try {
      setLoading(true);
      const response = await axios.post(
        `http://localhost:5000/admin/select-article/${currentBatch.id}`,
        {
          article_id: article.id, // Ensure the unique ID is sent
          topic: selectedTopic
        },
        { headers: { 'Admin-Key': adminKey } }
      );
  
      // Optimistically update the selectedArticles state
      setSelectedArticles(prevSelected => {
        const isSelected = prevSelected[selectedTopic]?.some(a => a.id === article.id);
  
        if (isSelected) {
          // Deselect the article
          const updatedArticles = prevSelected[selectedTopic].filter(a => a.id !== article.id);
          if (updatedArticles.length === 0) {
            const { [selectedTopic]: removedTopic, ...rest } = prevSelected;
            return rest;
          } else {
            return { ...prevSelected, [selectedTopic]: updatedArticles };
          }
        } else {
          // Select the article
          return {
            ...prevSelected,
            [selectedTopic]: [...(prevSelected[selectedTopic] || []), article]
          };
        }
      });
  
      // Optionally, refresh articles to ensure data consistency
      await fetchArticles(currentBatch.id);
    } catch (error) {
      console.error('Error selecting article:', error);
      setError('Failed to select article');
      // Revert optimistic update on error
      await fetchArticles(currentBatch.id);
    } finally {
      setLoading(false);
    }
  };

  const handleCustomArticleChange = (e) => {
    const { name, value } = e.target;
    setCustomArticle(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddCustomArticle = async (e) => {
    e.preventDefault();
    if (!currentBatch) return;

    const adminKey = sessionStorage.getItem('adminKey');
    try {
      setLoading(true);
      await axios.post(
        `http://localhost:5000/admin/add-custom-article/${currentBatch.id}`,
        customArticle,
        { headers: { 'Admin-Key': adminKey } }
      );

      alert('Custom article added successfully');
      setShowCustomForm(false);
      setCustomArticle({ title: '', link: '', summary: '', topic: '' });
      await fetchArticles(currentBatch.id);
    } catch (error) {
      console.error('Error adding custom article:', error);
      setError('Failed to add custom article');
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = async () => {
    if (!currentBatch) return;

    window.open(`/admin/preview/${currentBatch.id}`, '_blank');
  };

  const handleSendPreview = async () => {
    if (!currentBatch) return;

    const adminKey = sessionStorage.getItem('adminKey');
    const adminEmail = prompt('Enter your email address to receive the preview:');

    if (!adminEmail) return;

    try {
      setLoading(true);
      await axios.post(
        `http://localhost:5000/admin/send-preview/${currentBatch.id}`,
        { admin_email: adminEmail },
        { headers: { 'Admin-Key': adminKey } }
      );

      alert('Preview sent successfully to ' + adminEmail);
    } catch (error) {
      console.error('Error sending preview:', error);
      setError('Failed to send preview');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!currentBatch) return;

    const adminKey = sessionStorage.getItem('adminKey');
    try {
      setLoading(true);
      await axios.post(
        `http://localhost:5000/admin/approve/${currentBatch.id}`,
        {},
        { headers: { 'Admin-Key': adminKey } }
      );

      alert('Newsletter approved successfully');
      navigate('/admin/dashboard');
    } catch (error) {
      console.error('Error approving newsletter:', error);
      setError('Failed to approve newsletter');
    } finally {
      setLoading(false);
    }
  };

  const handleSendNewsletter = async () => {
    if (!currentBatch) return;

    if (!window.confirm('Are you sure you want to send this newsletter to all subscribers?')) {
      return;
    }

    const adminKey = sessionStorage.getItem('adminKey');
    try {
      setLoading(true);
      const response = await axios.post(
        `http://localhost:5000/admin/send-newsletter/${currentBatch.id}`,
        {},
        { headers: { 'Admin-Key': adminKey } }
      );

      alert(`Newsletter sent successfully! ${response.data.stats.sent} emails sent.`);
      navigate('/admin/dashboard');
    } catch (error) {
      console.error('Error sending newsletter:', error);
      setError('Failed to send newsletter');
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return 'N/A';
    const date = new Date(dateTimeStr);
    return date.toLocaleString();
  };

  const isArticleSelected = (article, topic) => {
    const selectedTopic = topic || 'General';
    return selectedArticles &&
      selectedArticles[selectedTopic] &&
      selectedArticles[selectedTopic].some(selected => selected.id === article.id);
  };

  const toggleTopic = (topic) => {
    setExpandedTopics(prev => ({
      ...prev,
      [topic]: !prev[topic]
    }));
  };

  // Function to sort articles: Selected articles first
  const sortArticles = (articles, topic) => {
    return [...articles].sort((a, b) => {
      const aSelected = isArticleSelected(a, topic);
      const bSelected = isArticleSelected(b, topic);
      if (aSelected && !bSelected) return -1;
      if (!aSelected && bSelected) return 1;
      return 0;
    });
  };

  // Pagination function
  const paginateArticles = (articles) => {
    const startIndex = (currentPage - 1) * articlesPerPage;
    const endIndex = startIndex + articlesPerPage;
    return articles.slice(startIndex, endIndex);
  };

  // Change page
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  const handleResetSelection = async () => {
    if (!currentBatch) return;

    if (!window.confirm('Are you sure you want to reset all selected articles? This cannot be undone.')) {
      return;
    }

    const adminKey = sessionStorage.getItem('adminKey');
    try {
      setLoading(true);
      await axios.post(
        `http://localhost:5000/admin/reset-selection/${currentBatch.id}`,
        {},
        { headers: { 'Admin-Key': adminKey } }
      );

      setSelectedArticles({});
      alert('Article selection has been reset');
      await fetchArticles(currentBatch.id);
    } catch (error) {
      console.error('Error resetting article selection:', error);
      setError('Failed to reset article selection');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !currentBatch && !articles) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="admin-article-management">
      <div className="admin-header">
        <h1>Article Management</h1>
      </div>

      {error && <div className="admin-error-message">{error}</div>}

      <div className="admin-tabs">
        <div className="admin-batches-list">
          <h2>Newsletter Batches</h2>
          <div className="admin-batches">
            {batches.map(batch => (
              <div
                key={batch.id}
                className={`admin-batch-item ${currentBatch && batch.id === currentBatch.id ? 'active' : ''}`}
                onClick={() => handleBatchSelect(batch)}
              >
                <h3>Batch #{batch.id}</h3>
                <p>Created: {formatDateTime(batch.date_created)}</p>
                <p>
                  Status: {batch.is_finalized ? 'Finalized' : 'Draft'},
                  {batch.is_sent ? ' Sent' : ' Not Sent'}
                </p>
              </div>
            ))}

            {batches.length === 0 && (
              <p>No batches available. Collect articles to create a new batch.</p>
            )}
          </div>
        </div>

        <div className="admin-article-content">
          {currentBatch ? (
            <>
              <div className="admin-article-header">
                <h2>Batch #{currentBatch.id} - {formatDateTime(currentBatch.date_created)}</h2>
                <div className="admin-article-actions">
                  <button
                    className="admin-button secondary"
                    onClick={handleAutoSelect}
                  >
                    Auto-Select Articles
                  </button>

                  <button
                    className="admin-button secondary"
                    onClick={() => setShowCustomForm(!showCustomForm)}
                  >
                    {showCustomForm ? 'Cancel Custom' : 'Add Custom Article'}
                  </button>

                  <button
                    className="admin-button secondary"
                    onClick={handlePreview}
                  >
                    Preview Newsletter
                  </button>

                  <button
                    className="admin-button secondary"
                    onClick={handleSendPreview}
                  >
                    Send Preview
                  </button>

                  <button
                    className="admin-button secondary warning"
                    onClick={handleResetSelection}
                    disabled={!currentBatch || Object.keys(selectedArticles).length === 0}
                  >
                    Reset Selection
                  </button>
                </div>
              </div>

              {showCustomForm && (
                <div className="admin-custom-article-form">
                  <h3>Add Custom Article</h3>
                  <form onSubmit={handleAddCustomArticle}>
                    <div className="form-group">
                      <label htmlFor="title">Title</label>
                      <input
                        id="title"
                        name="title"
                        value={customArticle.title}
                        onChange={handleCustomArticleChange}
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="link">Link</label>
                      <input
                        id="link"
                        name="link"
                        value={customArticle.link}
                        onChange={handleCustomArticleChange}
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="summary">Summary</label>
                      <textarea
                        id="summary"
                        name="summary"
                        value={customArticle.summary}
                        onChange={handleCustomArticleChange}
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="topic">Topic</label>
                      <input
                        id="topic"
                        name="topic"
                        value={customArticle.topic}
                        onChange={handleCustomArticleChange}
                        required
                        placeholder="e.g., AI, Cybersecurity, Web Development"
                      />
                    </div>

                    <button type="submit" className="admin-button primary">
                      Add Article
                    </button>
                  </form>
                </div>
              )}

              {articles ? (
                <div className="admin-articles-container">
                  <h3>Specific Topic Articles</h3>
                  {Object.entries(articles.specific_articles || {}).map(([topic, topicArticles]) => {
                    const sortedArticles = sortArticles(topicArticles, topic);
                    const paginatedArticles = paginateArticles(sortedArticles);

                    return (
                      <div key={topic} className="admin-topic-section">
                        <h4 onClick={() => toggleTopic(topic)} style={{ cursor: 'pointer' }}>
                          {topic} ({topicArticles.length})
                          {expandedTopics[topic] ? ' [-]' : ' [+]'}
                        </h4>
                        {expandedTopics[topic] && (
                          <div className="admin-articles-grid">
                            {paginatedArticles.map(article => (
                              <div
                                key={article.id}
                                className={`admin-article-card ${isArticleSelected(article, topic) ? 'selected' : ''}`}
                              >
                                <h5>{article.title}</h5>
                                <p><small>Source: {article.source}</small></p>
                                <p className="admin-article-summary">{article.summary}</p>
                                <div className="admin-article-card-footer">
                                  <a href={article.link} target="_blank" rel="noopener noreferrer">
                                    Read More
                                  </a>
                                  <button
                                    className="admin-button small"
                                    onClick={() => handleArticleSelect(article, topic)}
                                  >
                                    {isArticleSelected(article, topic) ? 'Deselect' : 'Select'}
                                  </button>
                                </div>
                              </div>
                            ))}

                            {paginatedArticles.length === 0 && (
                              <p>No articles found for {topic} on this page.</p>
                            )}
                          </div>
                        )}

                        {/* Pagination */}
                        {topicArticles.length > articlesPerPage && (
                          <div className="admin-pagination">
                            {Array.from({ length: Math.ceil(topicArticles.length / articlesPerPage) }, (_, i) => i + 1).map(pageNumber => (
                              <button
                                key={pageNumber}
                                className={`admin-page-button ${currentPage === pageNumber ? 'active' : ''}`}
                                onClick={() => handlePageChange(pageNumber)}
                              >
                                {pageNumber}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}

                  <h3>General Articles</h3>
                  {(() => {
                    const generalSortedArticles = sortArticles(articles.general_articles || []);
                    const generalPaginatedArticles = paginateArticles(generalSortedArticles);

                    return (
                      <>
                        <div className="admin-articles-grid">
                          {generalPaginatedArticles.map(article => (
                            <div
                              key={article.id}
                              className={`admin-article-card ${isArticleSelected(article) ? 'selected' : ''}`}
                            >
                              <h5>{article.title}</h5>
                              <p><small>Source: {article.source}</small></p>
                              <p className="admin-article-summary">{article.summary}</p>
                              <div className="admin-article-card-footer">
                                <a href={article.link} target="_blank" rel="noopener noreferrer">
                                  Read More
                                </a>
                                <button
                                  className="admin-button small"
                                  onClick={() => handleArticleSelect(article)}
                                >
                                  {isArticleSelected(article) ? 'Deselect' : 'Select'}
                                </button>
                              </div>
                            </div>
                          ))}

                          {generalPaginatedArticles.length === 0 && (
                            <p>No general articles found on this page</p>
                          )}
                        </div>

                        {/* Pagination for General Articles */}
                        {(articles.general_articles || []).length > articlesPerPage && (
                          <div className="admin-pagination">
                            {Array.from({ length: Math.ceil((articles.general_articles || []).length / articlesPerPage) }, (_, i) => i + 1).map(pageNumber => (
                              <button
                                key={pageNumber}
                                className={`admin-page-button ${currentPage === pageNumber ? 'active' : ''}`}
                                onClick={() => handlePageChange(pageNumber)}
                              >
                                {pageNumber}
                              </button>
                            ))}
                          </div>
                        )}
                      </>
                    );
                  })()}
                </div>
              ) : (
                <div className="admin-loading">
                  <div className="spinner"></div>
                  <p>Loading articles...</p>
                </div>
              )}

              {/* Display Selected Articles */}
              <div className="admin-selected-articles">
                <h3>Selected Articles</h3>
                {Object.entries(selectedArticles).map(([topic, articles]) => (
                  <div key={topic}>
                    <h4>{topic}</h4>
                    <ul>
                      {articles.map(article => (
                        <li key={article.id}>{article.title}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>

              <div className="admin-finalize-actions">
                <button
                  className="admin-button primary"
                  onClick={handleApprove}
                  disabled={currentBatch?.is_sent}
                >
                  Approve Newsletter
                </button>

                <button
                  className="admin-button primary"
                  onClick={handleSendNewsletter}
                  disabled={!currentBatch?.admin_approved || currentBatch?.is_sent}
                >
                  Send Newsletter
                </button>

                {currentBatch?.is_sent && (
                  <div className="admin-note">
                    This newsletter has already been sent.
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="admin-placeholder">
              <h2>Select a batch from the list</h2>
              <p>Or collect new articles to create a fresh batch.</p>
              <button
                className="admin-button primary"
                onClick={() => navigate('/admin/dashboard')}
              >
                Go to Dashboard
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ArticleManagement;
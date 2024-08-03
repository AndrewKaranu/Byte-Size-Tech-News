import React from 'react';
import './Styles/StartMenu.css';

const StartMenu = ({ isOpen, onClose, onShutDown }) => {
  if (!isOpen) return null;

  return (
    <div className="start-menu-overlay" onClick={onClose}>
      <div className="start-menu" onClick={(e) => e.stopPropagation()}>
        <div className="start-menu-side">
          <span className="start-menu-title">Byte Sized Tech News</span>
        </div>
        <div className="start-menu-items">
          <div className="start-menu-item" onClick={() => window.open('https://github.com/yourusername', '_blank')}>
            <img src="/path/to/github-icon.png" alt="GitHub" />
            <span>GitHub</span>
          </div>
          <div className="start-menu-item" onClick={() => window.open('https://linkedin.com/in/yourusername', '_blank')}>
            <img src="/path/to/linkedin-icon.png" alt="LinkedIn" />
            <span>LinkedIn</span>
          </div>
          <div className="start-menu-item" onClick={() => window.location.href = 'mailto:your@email.com'}>
            <img src="/path/to/email-icon.png" alt="Email" />
            <span>Email</span>
          </div>
          <div className="start-menu-item" onClick={() => window.open('https://instagram.com/yourusername', '_blank')}>
            <img src="/path/to/instagram-icon.png" alt="Instagram" />
            <span>Instagram</span>
          </div>
          <div className="start-menu-separator"></div>
          <div className="start-menu-item" onClick={onShutDown}>
            <img src="/path/to/shutdown-icon.png" alt="Shut Down" />
            <span>Shut Down...</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StartMenu;
import React, { useState, useEffect } from 'react';
import './Styles/SystemAnimations.css';
import startstopBackground from './Styles/startstop_background.png';

const SystemAnimations = ({ isShuttingDown, isStartingUp, onStartupComplete }) => {
  const [showStartButton, setShowStartButton] = useState(false);

  useEffect(() => {
    if (isShuttingDown) {
      setTimeout(() => setShowStartButton(true), 3000);
    }
  }, [isShuttingDown]);

  const handleStartClick = () => {
    setShowStartButton(false);
    onStartupComplete();
  };

  const backgroundStyle = {
    backgroundImage: `url(${startstopBackground})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat'
  };

  if (isShuttingDown) {
    return (
      <div className="system-animation shutdown" style={backgroundStyle}>
        <div className="shutdown-text">It is now safe to turn off your computer.</div>
        {showStartButton && (
          <button className="start-button" onClick={handleStartClick}>
            Start
          </button>
        )}
      </div>
    );
  }

  if (isStartingUp) {
    return (
      <div className="system-animation startup" style={backgroundStyle}>
        <div className="startup-logo">Windows 95</div>
        <div className="startup-progress"></div>
      </div>
    );
  }

  return null;
};

export default SystemAnimations;
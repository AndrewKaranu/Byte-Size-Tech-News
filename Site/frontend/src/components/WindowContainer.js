import React, { useState, useEffect } from 'react';
import Desktop from './Desktop';
import Articles from './Articles';
import Terminal from './Terminal';
import Support from './Support';
import SystemAnimations from './SystemAnimations';
import './Styles/WindowContainer.css';

const WindowContainer = () => {
  const [isShuttingDown, setIsShuttingDown] = useState(false);
  const [isStartingUp, setIsStartingUp] = useState(true);
  const [openWindows, setOpenWindows] = useState([]);

  useEffect(() => {
    // Simulate initial startup
    setTimeout(() => setIsStartingUp(false), 3000);
  }, []);

  const handleShutDown = () => {
    setIsShuttingDown(true);
  };

  const handleStartup = () => {
    setIsShuttingDown(false);
    setIsStartingUp(true);
    setTimeout(() => {
      setIsStartingUp(false);
    }, 3000);
  };

  const openProgram = (program) => {
    if (!openWindows.includes(program)) {
      setOpenWindows([...openWindows, program]);
    }
  };

  const closeProgram = (program) => {
    setOpenWindows(openWindows.filter(win => win !== program));
  };

  if (isShuttingDown || isStartingUp) {
    return (
      <SystemAnimations 
        isShuttingDown={isShuttingDown} 
        isStartingUp={isStartingUp} 
        onStartupComplete={handleStartup}
      />
    );
  }

  return (
    <div className="window-container">
      <div className="window">
        <div className="window-title-bar">
          <div className="window-title">Byte Sized Tech News</div>
          <div className="window-controls">
            <button className="window-control minimize">_</button>
            <button className="window-control maximize">□</button>
            <button className="window-control close">X</button>
          </div>
        </div>
        <div className="window-content">
          <Desktop openProgram={openProgram} onShutDown={handleShutDown} />
          {openWindows.includes('terminal') && <Terminal onClose={() => closeProgram('terminal')} />}
          {openWindows.includes('articles') && <Articles onClose={() => closeProgram('articles')} />}
          {openWindows.includes('support') && <Support onClose={() => closeProgram('support')} />}
        </div>
      </div>
    </div>
  );
};

export default WindowContainer;
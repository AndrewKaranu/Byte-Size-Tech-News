import React, { useState } from 'react';
import './Styles/Desktop.css';
import Program from './Program';
import SignUp from './SignupIcon';
import StartMenu from './StartMenu';
import TimeDisplay from './TimeDisplay';
import desktopBackground from './Styles/background.png';
import startButtonIcon from './Styles/start-button-icon.png';

const Desktop = ({ openProgram, onShutDown }) => {
  const [isStartMenuOpen, setIsStartMenuOpen] = useState(false);

  const toggleStartMenu = () => {
    setIsStartMenuOpen(!isStartMenuOpen);
  };

  return (
    <div className="desktop">
      <div className="background" style={{ backgroundImage: `url(${desktopBackground})` }}>
        <div className="icons-container">
          <SignUp name="Sign Up" openProgram={() => openProgram('terminal')} />
          <Program name="View Articles" openProgram={() => openProgram('articles')}/>
          <Program name="Support/FAQ" openProgram={() => openProgram('support')}/>
        </div>
      </div>
      <div className="taskbar">
        <div className="start-button" onClick={toggleStartMenu}>
          <img src={startButtonIcon} alt="Start" />
        </div>
        <div className="taskbar-right">
          <TimeDisplay />
        </div>
      </div>
      <StartMenu 
        isOpen={isStartMenuOpen} 
        onClose={() => setIsStartMenuOpen(false)} 
        onShutDown={onShutDown}
        openProgram={openProgram}
      />
    </div>
  );
};

export default Desktop;
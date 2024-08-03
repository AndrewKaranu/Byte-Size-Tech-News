import React from 'react';
import './Styles/Window.css';

const Articles = ({ onClose }) => {
    return (
        <div className="window articles-window">
            <div className="title-bar">
                <div className="title-bar-text">Today's Articles</div>
                <div className="title-bar-controls">
                    <button aria-label="Close" onClick={onClose}></button>
                </div>
            </div>
            <div className="window-body">
                {/* Add your articles content here */}
            </div>
        </div>
    );
};

export default Articles;
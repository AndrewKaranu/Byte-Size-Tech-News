import React from 'react';
import './Styles/Window.css';

const Support = ({ onClose }) => {
    return (
        <div className="window support-window">
            <div className="title-bar">
                <div className="title-bar-text">Support/FAQ</div>
                <div className="title-bar-controls">
                    <button aria-label="Close" onClick={onClose}></button>
                </div>
            </div>
            <div className="window-body">
                <h1>Frequently Asked Questions</h1>
                <h2>Q: How often will I receive news updates?</h2>
                <p>A: We send out weekly updates every Monday morning.</p>
                <h2>Q: How do I unsubscribe?</h2>
                <p>A: You can unsubscribe at any time by clicking the unsubscribe link at the bottom of any email.</p>
                {/* Add more FAQ items as needed */}
            </div>
        </div>
    );
};

export default Support;
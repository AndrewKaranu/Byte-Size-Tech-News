import React from 'react';
import './Styles/Program.css';

const Program = ({ name, openProgram }) => {
    return (
        <div className="program" onClick={openProgram}>
            <img src="/view_articles.png" alt="program icon" />
            <p>{name}</p>
        </div>
    );
};

export default Program;

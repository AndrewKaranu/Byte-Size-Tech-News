import React from 'react';
import './Styles/Program.css';

const SignUp = ({ name, openProgram }) => {
    return (
        <div className="program" onClick={() => openProgram('terminal')}>
            <img src="/view_signup.png" alt="program icon" />
            <p>{name}</p>
        </div>
    );
};

export default SignUp;
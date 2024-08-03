import React, { useState } from 'react';
import axios from 'axios';

const SignupForm = () => {
  const [email, setEmail] = useState('');
  const [language, setLanguage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
        const response = await axios.post('http://localhost:5000/signup', { email, language });
        console.log(response); // Add this line
        if (response && response.data) {
            alert(response.data.message);
        } else {
            alert('An unexpected error occurred.');
        }
    } catch (error) {
        console.error(error); 
        if (error.response && error.response.data) {
            alert(error.response.data.message);
        } else {
            alert('An unexpected error occurred.');
        }
    }
};


  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="email" 
        placeholder="Email" 
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required 
      />
      <select 
        value={language} 
        onChange={(e) => setLanguage(e.target.value)}
        required
      >
        <option value="" disabled>Select language</option>
        <option value="en">English</option>
        <option value="es">Spanish</option>
        {/* <!-- Add more languages as needed --> */}
      </select>
      <button type="submit">Sign Up</button>
    </form>
  );
};

export default SignupForm;

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import WindowContainer from './components/WindowContainer';
import AdminPanel from './components/admin/AdminPanel'; // This will be your admin panel component

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/admin/*" element={<AdminPanel />} />
          <Route path="*" element={<WindowContainer />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
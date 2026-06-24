import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import DoctorDashboard from './pages/DoctorDashboard';
import AdminDashboard from './pages/AdminDashboard';
import PatientChat from './pages/PatientChat';

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Patient Chatbot is the main interface at the root URL */}
        <Route path="/" element={<PatientChat />} />
        
        {/* Portals for Doctor and Admin login */}
        <Route path="/login" element={<Login />} />
        <Route path="/portal" element={<Login />} />
        
        {/* Authenticated dashboards */}
        <Route path="/dashboard" element={<DoctorDashboard />} />
        <Route path="/admin" element={<AdminDashboard />} />
        
        {/* Redirect any unknown routes back to the chatbot home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;

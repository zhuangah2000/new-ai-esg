import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './components/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Login } from './components/Login';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { EmissionFactors } from './components/EmissionFactors';
import { Measurements } from './components/Measurements';
import { Suppliers } from './components/Suppliers';
import { Reports } from './components/Reports';
import { Settings } from './components/Settings';
import { Projects } from './components/Projects';
import { Assets } from './components/Assets';
import { ESGTargets } from './components/ESGTargets';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// Main App Layout Component (Protected)
function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className={`flex-1 flex flex-col overflow-hidden transition-all duration-300 ${
        sidebarOpen ? 'ml-64' : 'ml-16'
      }`}>
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard apiBaseUrl={API_BASE_URL} />} />
            <Route path="/emission-factors" element={<EmissionFactors apiBaseUrl={API_BASE_URL} />} />
            <Route path="/measurements" element={<Measurements apiBaseUrl={API_BASE_URL} />} />
            <Route path="/suppliers" element={<Suppliers apiBaseUrl={API_BASE_URL} />} />
            <Route path="/projects" element={<Projects apiBaseUrl={API_BASE_URL} />} />
            <Route path="/assets" element={<Assets apiBaseUrl={API_BASE_URL} />} />
            <Route path="/esg-targets" element={<ESGTargets apiBaseUrl={API_BASE_URL} />} />
            <Route path="/reports" element={<Reports apiBaseUrl={API_BASE_URL} />} />
            <Route path="/settings" element={<Settings apiBaseUrl={API_BASE_URL} />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

// Root App Component with Authentication
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Route - Login Page */}
          <Route path="/login" element={<Login apiBaseUrl={API_BASE_URL} />} />
          
          {/* Protected Routes - Main Application */}
          <Route path="/*" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;


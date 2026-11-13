import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import MobileDashboard from './components/MobileDashboard';
import AdminPanel from './components/AdminPanel';
import GridVisualizer from './components/GridVisualizer';
import AIAnalyzer from './components/AIAnalyzer';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="sidebar">
          <h2>CMG Admin Console</h2>
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/admin">Admin Panel</NavLink>
          <NavLink to="/grid">Grid Visualizer</NavLink>
          <NavLink to="/ai">AI Analyzer</NavLink>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<MobileDashboard />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="/grid" element={<GridVisualizer />} />
            <Route path="/ai" element={<AIAnalyzer />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

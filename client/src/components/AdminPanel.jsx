import React, { useState } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

export default function AdminPanel() {
  const [broadcastMessage, setBroadcastMessage] = useState('');
  const [selectedGrid, setSelectedGrid] = useState('C3');
  const [config, setConfig] = useState(null);
  const [apiToken, setApiToken] = useState('');

  const adminRequest = async (path, options = {}) => {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${apiToken.trim()}`
      }
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || `Request failed (${response.status}).`);
    }
    return data;
  };

  const handleBroadcast = async () => {
    try {
      await adminRequest('/api/broadcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ grid: selectedGrid, message: broadcastMessage })
      });
      alert('Message sent!');
    } catch (error) {
      alert(error.message);
    }
  };

  const handleStartServer = async () => {
    try {
      await adminRequest(`/api/start/${selectedGrid}`, { method: 'POST' });
      alert(`Start signal sent to ${selectedGrid}`);
    } catch (error) {
      alert(error.message);
    }
  };

  const handleStopServer = async () => {
    try {
      await adminRequest(`/api/stop/${selectedGrid}`, { method: 'POST' });
      alert(`Stop signal sent to ${selectedGrid}`);
    } catch (error) {
      alert(error.message);
    }
  };

  const handleLoadConfig = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/config`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || `Request failed (${response.status}).`);
      setConfig(data);
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div>
      <h2>Admin Panel</h2>
      <label htmlFor="admin-api-token">Admin API token:</label>
      <input
        id="admin-api-token"
        type="password"
        autoComplete="off"
        value={apiToken}
        onChange={event => setApiToken(event.target.value)}
      />
      <label>Select Grid:</label>
      <select value={selectedGrid} onChange={event => setSelectedGrid(event.target.value)}>
        {['A1','B1','C1','D1','E1','A2','B2','C2','D2','E2','A3','B3','C3','D3','E3','A4','B4','C4','D4','E4','A5','B5','C5','D5','E5'].map(grid => (
          <option key={grid} value={grid}>{grid}</option>
        ))}
      </select>

      <div>
        <button onClick={handleStartServer}>Start Server</button>
        <button onClick={handleStopServer}>Stop Server</button>
      </div>

      <div>
        <input
          type="text"
          placeholder="Broadcast message"
          value={broadcastMessage}
          onChange={event => setBroadcastMessage(event.target.value)}
        />
        <button onClick={handleBroadcast}>Broadcast</button>
      </div>

      <div>
        <button onClick={handleLoadConfig}>Load Config</button>
        {config && <pre>{JSON.stringify(config, null, 2)}</pre>}
      </div>
    </div>
  );
}

import React, { useEffect, useState } from 'react';
import './MobileDashboard.css';

const API_BASE_URL = process.env.REACT_APP_STATUS_API_URL || 'http://localhost:5050';

export default function MobileDashboard() {
  const [restartTime, setRestartTime] = useState(null);
  const [restartStatus, setRestartStatus] = useState('Not scheduled');
  const [gridStatus, setGridStatus] = useState('');
  const [grids, setGrids] = useState({});
  const [countdown, setCountdown] = useState('Not scheduled');

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/grid-status`)
      .then(response => {
        if (!response.ok) throw new Error(`Grid status request failed (${response.status}).`);
        return response.json();
      })
      .then(setGrids)
      .catch(error => setGridStatus(error.message));

  }, []);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    let timeout;
    const refreshSchedule = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/restart-time`, { signal: controller.signal });
        if (!response.ok) throw new Error(response.status === 404 ? 'Not scheduled' : `Restart schedule request failed (${response.status}).`);
        const data = await response.json();
        const date = new Date(data.restart_time_utc);
        if (Number.isNaN(date.getTime())) throw new Error('Restart schedule contains an invalid date.');
        if (!active) return;
        setRestartTime(date);
        setRestartStatus('');
      } catch (error) {
        if (!active) return;
        setRestartTime(null);
        setRestartStatus(error.message);
      } finally {
        if (active) timeout = setTimeout(refreshSchedule, 30000);
      }
    };

    refreshSchedule();
    return () => {
      active = false;
      clearTimeout(timeout);
      controller.abort();
    };
  }, []);

  useEffect(() => {
    if (!restartTime) return undefined;

    const updateCountdown = () => {
      const diff = Math.floor((restartTime - new Date()) / 1000);
      if (diff <= 0) {
        setCountdown('Restarting now...');
        return;
      }
      const minutes = Math.floor(diff / 60);
      const seconds = diff % 60;
      setCountdown(`${minutes}m ${seconds < 10 ? '0' : ''}${seconds}s`);
    };

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
    return () => clearInterval(interval);
  }, [restartTime]);

  return (
    <div className="mobile-dashboard">
      <h2>Chaotic ATLAS Dashboard</h2>
      <div className="countdown" role="status">⏳ Restart in: {restartTime ? countdown : restartStatus}</div>
      {gridStatus && <p role="alert">{gridStatus}</p>}
      <div className="grid-summary">
        {Object.entries(grids).map(([id, info]) => (
          <div key={id} className={`grid-card ${info.status}`}>
            <strong>{id}</strong>
            <div>{info.type}</div>
            <div>{info.players} players</div>
          </div>
        ))}
      </div>
    </div>
  );
}

import React, { useState } from 'react';

export default function AIAnalyzer() {
  const [logText, setLogText] = useState('');
  const [summary, setSummary] = useState('');

  const analyze = () => {
    const issues = [];
    if (logText.includes('Fatal error')) issues.push('Fatal error detected. Server likely crashed immediately.');
    if (logText.includes('Out of memory')) issues.push('Server ran out of memory. Consider reducing entity load or increasing RAM.');
    if (logText.toLowerCase().includes('assert')) issues.push('Assertion failed. This usually indicates a bug in the game server code.');
    if (logText.includes('Unhandled Exception')) issues.push('Unhandled exception occurred. Check mods or corrupt save data.');
    setSummary(issues.length ? issues.map(issue => `- ${issue}`).join('\n') : 'No known issue patterns detected. This may be a normal shutdown or log.');
  };

  return (
    <section>
      <h2>Log Analyzer</h2>
      <p>Rule-based checks run locally in your browser; the log text is not uploaded.</p>
      <label htmlFor="log-text">Paste a server log</label>
      <textarea
        id="log-text"
        rows="12"
        value={logText}
        onChange={event => setLogText(event.target.value)}
      />
      <button type="button" onClick={analyze} disabled={!logText.trim()}>Analyze log</button>
      {summary && <pre role="status">{summary}</pre>}
    </section>
  );
}

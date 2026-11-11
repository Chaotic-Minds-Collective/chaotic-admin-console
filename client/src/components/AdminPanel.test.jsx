import React from 'react';
import { createRoot } from 'react-dom/client';
import { act } from 'react-dom/test-utils';
import AdminPanel from './AdminPanel';

global.IS_REACT_ACT_ENVIRONMENT = true;

test('admin actions and config preserve HTTP errors when the response is not JSON', async () => {
  const container = document.createElement('div');
  const root = createRoot(container);
  global.alert = jest.fn();
  global.fetch = jest.fn();
  act(() => root.render(<AdminPanel />));
  try {
    for (const label of ['Start Server', 'Stop Server', 'Broadcast', 'Load Config']) {
      for (const [json, expected] of [
        [() => Promise.reject(new SyntaxError('HTML response')), 'Request failed (502).'],
        [() => Promise.resolve({ error: 'Specific error' }), 'Specific error'],
      ]) {
        fetch.mockResolvedValue({ ok: false, status: 502, json });
        const button = [...container.querySelectorAll('button')].find(node => node.textContent === label);
        await act(async () => button.click());
        expect(alert).toHaveBeenLastCalledWith(expected);
      }
    }
  } finally {
    act(() => root.unmount());
    delete global.fetch;
  }
});


test('config loading reports invalid successful JSON and preserves the last valid config', async () => {
  const container = document.createElement('div');
  const root = createRoot(container);
  global.alert = jest.fn();
  global.fetch = jest.fn();
  act(() => root.render(<AdminPanel />));
  try {
    const button = [...container.querySelectorAll('button')].find(node => node.textContent === 'Load Config');
    const invalidResponse = { ok: true, json: () => Promise.reject(new SyntaxError('HTML response')) };
    fetch.mockResolvedValue(invalidResponse);
    await act(async () => button.click());
    expect(alert).toHaveBeenLastCalledWith('Config response contains invalid JSON.');
    expect(container.querySelector('pre')).toBeNull();

    const config = { server_ip: '127.0.0.1', rcon_port_start: 35710 };
    fetch.mockResolvedValue({ ok: true, json: async () => config });
    alert.mockClear();
    await act(async () => button.click());
    expect(alert).not.toHaveBeenCalled();
    expect(JSON.parse(container.querySelector('pre').textContent)).toEqual(config);

    fetch.mockResolvedValue(invalidResponse);
    await act(async () => button.click());
    expect(alert).toHaveBeenLastCalledWith('Config response contains invalid JSON.');
    expect(JSON.parse(container.querySelector('pre').textContent)).toEqual(config);
  } finally {
    act(() => root.unmount());
    delete global.fetch;
  }
});

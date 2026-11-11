import React from 'react';
import { createRoot } from 'react-dom/client';
import { act } from 'react-dom/test-utils';
import MobileDashboard from './MobileDashboard';

global.IS_REACT_ACT_ENVIRONMENT = true;

test('refreshes missing and changed schedules, clears removed schedules and stops on unmount', async () => {
  jest.useFakeTimers();
  jest.setSystemTime(new Date('2030-01-01T00:00:00Z'));
  const container = document.createElement('div');
  const root = createRoot(container);
  let schedule = { ok: false, status: 404 };
  let signal;
  global.fetch = jest.fn((url, options) => {
    if (url.endsWith('/api/grid-status')) return Promise.resolve({ ok: true, json: async () => ({}) });
    signal = options.signal;
    return Promise.resolve(schedule);
  });
  try {
    await act(async () => root.render(<MobileDashboard />));
    expect(container.textContent).toContain('Not scheduled');
    schedule = { ok: true, json: async () => ({ restart_time_utc: '2030-01-01T00:02:00Z' }) };
    await act(async () => jest.advanceTimersByTime(30000));
    expect(container.textContent).toContain('1m 30s');
    schedule = { ok: true, json: async () => ({ restart_time_utc: '2030-01-01T00:05:00Z' }) };
    await act(async () => jest.advanceTimersByTime(30000));
    expect(container.textContent).toContain('4m 00s');
    schedule = { ok: false, status: 404 };
    await act(async () => jest.advanceTimersByTime(30000));
    expect(container.textContent).toContain('Not scheduled');
    act(() => root.unmount());
    expect(signal.aborted).toBe(true);
    const calls = fetch.mock.calls.length;
    await act(async () => jest.advanceTimersByTime(60000));
    expect(fetch).toHaveBeenCalledTimes(calls);
    expect(jest.getTimerCount()).toBe(0);
  } finally {
    jest.useRealTimers();
    delete global.fetch;
  }
});

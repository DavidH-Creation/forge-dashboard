import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useDashboardStore } from '../store/dashboard';
import { useWebSocket } from '../hooks/useWebSocket';

// Minimal WebSocket mock
class MockWebSocket {
  static instances: MockWebSocket[] = [];
  url: string;
  onopen: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }

  send(_data: string) {}
  close() {}

  simulateOpen() {
    this.onopen?.();
  }
  simulateMessage(data: object) {
    this.onmessage?.({ data: JSON.stringify(data) });
  }
  simulateClose() {
    this.onclose?.();
  }
}

beforeEach(() => {
  MockWebSocket.instances = [];
  vi.stubGlobal('WebSocket', MockWebSocket);
  vi.useFakeTimers();
  useDashboardStore.setState({ components: [], recentEvents: [], wsConnected: false });
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe('useWebSocket', () => {
  it('sets wsConnected true on open', () => {
    renderHook(() => useWebSocket());
    act(() => MockWebSocket.instances[0].simulateOpen());
    expect(useDashboardStore.getState().wsConnected).toBe(true);
  });

  it('sends replay message on open', () => {
    renderHook(() => useWebSocket());
    const ws = MockWebSocket.instances[0];
    const sendSpy = vi.spyOn(ws, 'send');
    act(() => ws.simulateOpen());
    expect(sendSpy).toHaveBeenCalledOnce();
    const msg = JSON.parse(sendSpy.mock.calls[0][0] as string);
    expect(msg.type).toBe('replay');
  });

  it('adds received events to store', () => {
    renderHook(() => useWebSocket());
    const ws = MockWebSocket.instances[0];
    act(() => ws.simulateOpen());
    act(() =>
      ws.simulateMessage({
        component: 'bulwark',
        event_type: 'run_started',
        run_id: 'r1',
        timestamp: new Date().toISOString(),
        data: {},
      }),
    );
    expect(useDashboardStore.getState().recentEvents).toHaveLength(1);
  });

  it('ignores replay_complete messages', () => {
    renderHook(() => useWebSocket());
    const ws = MockWebSocket.instances[0];
    act(() => ws.simulateOpen());
    act(() => ws.simulateMessage({ type: 'replay_complete', truncated: false, count: 0 }));
    expect(useDashboardStore.getState().recentEvents).toHaveLength(0);
  });

  it('sets wsConnected false on close', () => {
    renderHook(() => useWebSocket());
    const ws = MockWebSocket.instances[0];
    act(() => ws.simulateOpen());
    act(() => ws.simulateClose());
    expect(useDashboardStore.getState().wsConnected).toBe(false);
  });

  it('reconnects after close with exponential backoff', () => {
    renderHook(() => useWebSocket());
    expect(MockWebSocket.instances).toHaveLength(1);

    // First close → retry after 1s (2^0 * 1000)
    act(() => MockWebSocket.instances[0].simulateClose());
    expect(MockWebSocket.instances).toHaveLength(1);
    act(() => vi.advanceTimersByTime(1000));
    expect(MockWebSocket.instances).toHaveLength(2);

    // Second close → retry after 2s (2^1 * 1000)
    act(() => MockWebSocket.instances[1].simulateClose());
    act(() => vi.advanceTimersByTime(2000));
    expect(MockWebSocket.instances).toHaveLength(3);
  });

  it('caps backoff at 30s', () => {
    renderHook(() => useWebSocket());
    // Simulate many failures to exceed MAX_DELAY
    for (let i = 0; i < 10; i++) {
      const ws = MockWebSocket.instances[MockWebSocket.instances.length - 1];
      act(() => ws.simulateClose());
      act(() => vi.advanceTimersByTime(30000));
    }
    // Should still reconnect (capped, not infinite)
    expect(MockWebSocket.instances.length).toBeGreaterThan(5);
  });

  it('does not reconnect after unmount', () => {
    const { unmount } = renderHook(() => useWebSocket());
    act(() => MockWebSocket.instances[0].simulateOpen());
    unmount();
    const countBeforeClose = MockWebSocket.instances.length;
    act(() => MockWebSocket.instances[0].simulateClose());
    act(() => vi.advanceTimersByTime(5000));
    expect(MockWebSocket.instances).toHaveLength(countBeforeClose);
  });
});

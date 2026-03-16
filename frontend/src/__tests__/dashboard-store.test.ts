import { describe, it, expect, beforeEach } from 'vitest';
import { useDashboardStore } from '../store/dashboard';
import type { ComponentHealth, DashboardEvent } from '../store/dashboard';

beforeEach(() => {
  useDashboardStore.setState({
    components: [],
    recentEvents: [],
    wsConnected: false,
  });
});

describe('useDashboardStore', () => {
  it('starts with empty state', () => {
    const state = useDashboardStore.getState();
    expect(state.components).toEqual([]);
    expect(state.recentEvents).toEqual([]);
    expect(state.wsConnected).toBe(false);
  });

  it('setComponents replaces component list', () => {
    const comps: ComponentHealth[] = [
      {
        name: 'Bulwark',
        status: 'healthy',
        health: { component: 'Bulwark', status: 'healthy', version: '4.0.0' },
        recent_runs: 3,
        latest_runs: [],
      },
    ];

    useDashboardStore.getState().setComponents(comps);
    expect(useDashboardStore.getState().components).toEqual(comps);
  });

  it('addEvent prepends event and caps at 100', () => {
    const store = useDashboardStore.getState();

    const event: DashboardEvent = {
      component: 'Crucible',
      event_type: 'run_started',
      run_id: 'abc-123',
      timestamp: new Date().toISOString(),
      data: {},
    };

    store.addEvent(event);
    expect(useDashboardStore.getState().recentEvents).toHaveLength(1);
    expect(useDashboardStore.getState().recentEvents[0]).toEqual(event);
  });

  it('caps recentEvents at 100', () => {
    const store = useDashboardStore.getState();

    for (let i = 0; i < 105; i++) {
      store.addEvent({
        component: 'Bulwark',
        event_type: 'tick',
        run_id: `run-${i}`,
        timestamp: new Date().toISOString(),
        data: { i },
      });
    }

    expect(useDashboardStore.getState().recentEvents).toHaveLength(100);
  });

  it('setWsConnected updates connection state', () => {
    useDashboardStore.getState().setWsConnected(true);
    expect(useDashboardStore.getState().wsConnected).toBe(true);

    useDashboardStore.getState().setWsConnected(false);
    expect(useDashboardStore.getState().wsConnected).toBe(false);
  });
});

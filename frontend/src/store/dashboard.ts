import { create } from 'zustand';

export interface ComponentHealth {
  name: string;
  status: string;
  health: { component: string; status: string; version: string };
  recent_runs: number;
  latest_runs: Array<{
    run_id: string;
    status: string;
    component: string;
    progress: number;
  }>;
}

export interface DashboardEvent {
  component: string;
  event_type: string;
  run_id: string;
  timestamp: string;
  data: Record<string, unknown>;
  is_retroactive?: boolean;
}

interface DashboardState {
  components: ComponentHealth[];
  recentEvents: DashboardEvent[];
  wsConnected: boolean;
  setComponents: (c: ComponentHealth[]) => void;
  addEvent: (e: DashboardEvent) => void;
  setWsConnected: (connected: boolean) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  components: [],
  recentEvents: [],
  wsConnected: false,
  setComponents: (components) => set({ components }),
  addEvent: (event) =>
    set((state) => ({
      recentEvents: [event, ...state.recentEvents].slice(0, 100),
    })),
  setWsConnected: (connected) => set({ wsConnected: connected }),
}));

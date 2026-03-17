import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { Overview } from '../pages/Overview';
import { useDashboardStore } from '../store/dashboard';

const MOCK_OVERVIEW = {
  components: [
    {
      name: 'Crucible',
      status: 'healthy',
      health: { component: 'Crucible', status: 'healthy', version: '1.0.0' },
      recent_runs: 5,
      latest_runs: [],
    },
    {
      name: 'Cartographer',
      status: 'healthy',
      health: { component: 'Cartographer', status: 'healthy', version: '0.1.0' },
      recent_runs: 3,
      latest_runs: [],
    },
    {
      name: 'Crossfire',
      status: 'degraded',
      health: { component: 'Crossfire', status: 'degraded', version: '2.0.0' },
      recent_runs: 1,
      latest_runs: [],
    },
    {
      name: 'Bulwark',
      status: 'healthy',
      health: { component: 'Bulwark', status: 'healthy', version: '4.0.0' },
      recent_runs: 12,
      latest_runs: [],
    },
  ],
};

beforeEach(() => {
  useDashboardStore.setState({
    components: [],
    recentEvents: [],
    wsConnected: false,
  });
});

describe('Overview', () => {
  it('renders loading state initially', () => {
    // Mock fetch to never resolve
    vi.spyOn(globalThis, 'fetch').mockImplementation(
      () => new Promise(() => {}),
    );

    render(
      <MemoryRouter>
        <Overview />
      </MemoryRouter>,
    );

    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
  });

  it('renders component health cards after loading', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      json: () => Promise.resolve(MOCK_OVERVIEW),
    } as Response);

    render(
      <MemoryRouter>
        <Overview />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getAllByText('Crucible').length).toBeGreaterThanOrEqual(1);
    });

    expect(screen.getAllByText('Cartographer').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Crossfire').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Bulwark').length).toBeGreaterThanOrEqual(1);
  });

  it('renders error state on fetch failure', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(
      new Error('Network error'),
    );

    render(
      <MemoryRouter>
        <Overview />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('Error: Network error')).toBeInTheDocument();
    });
  });

  it('displays quick action buttons', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      json: () => Promise.resolve(MOCK_OVERVIEW),
    } as Response);

    render(
      <MemoryRouter>
        <Overview />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    });

    expect(screen.getByText('View Pipeline')).toBeInTheDocument();
    expect(screen.getByText('Retry Failed')).toBeInTheDocument();
    expect(screen.getByText('Flow History')).toBeInTheDocument();
  });
});

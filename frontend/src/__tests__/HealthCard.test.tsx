import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { HealthCard } from '../components/HealthCard';
import type { ComponentHealth } from '../store/dashboard';

const MOCK_COMPONENT: ComponentHealth = {
  name: 'Bulwark',
  status: 'healthy',
  health: { component: 'Bulwark', status: 'healthy', version: '4.0.0' },
  recent_runs: 7,
  latest_runs: [],
};

describe('HealthCard', () => {
  it('renders component name and status', () => {
    render(
      <MemoryRouter>
        <HealthCard component={MOCK_COMPONENT} />
      </MemoryRouter>,
    );

    expect(screen.getByText('Bulwark')).toBeInTheDocument();
    expect(screen.getByText('healthy')).toBeInTheDocument();
  });

  it('shows version and run count', () => {
    render(
      <MemoryRouter>
        <HealthCard component={MOCK_COMPONENT} />
      </MemoryRouter>,
    );

    expect(screen.getByText('v4.0.0')).toBeInTheDocument();
    expect(screen.getByText('7 runs')).toBeInTheDocument();
  });

  it('links to component detail page', () => {
    render(
      <MemoryRouter>
        <HealthCard component={MOCK_COMPONENT} />
      </MemoryRouter>,
    );

    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/components/Bulwark');
  });
});

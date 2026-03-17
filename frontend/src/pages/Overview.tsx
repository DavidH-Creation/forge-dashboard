import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchOverview } from '../hooks/useApi';
import { useDashboardStore } from '../store/dashboard';
import type { ComponentHealth } from '../store/dashboard';
import { HealthCard } from '../components/HealthCard';
import { PipelineGraph } from '../components/PipelineGraph';
import { EventFeed } from '../components/EventFeed';

export function Overview() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const components = useDashboardStore((s) => s.components);
  const setComponents = useDashboardStore((s) => s.setComponents);
  const wsConnected = useDashboardStore((s) => s.wsConnected);

  useEffect(() => {
    fetchOverview()
      .then((data) => {
        setComponents(data.components ?? []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [setComponents]);

  if (loading) {
    return <div className="page-loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="page-error">Error: {error}</div>;
  }

  // Stats
  const totalRuns = components.reduce((sum, c) => sum + (c.recent_runs ?? 0), 0);
  const healthyCount = components.filter(
    (c) => c.health?.status === 'healthy',
  ).length;
  const activeRuns = components.reduce(
    (sum, c) =>
      sum +
      (c.latest_runs?.filter((r) => r.status?.toLowerCase() === 'running')
        .length ?? 0),
    0,
  );

  return (
    <div className="overview">
      <header className="overview__header">
        <div className="overview__title-row">
          <h1>Forge Dashboard</h1>
          <span
            className={`ws-indicator ${wsConnected ? 'ws-indicator--connected' : 'ws-indicator--disconnected'}`}
          >
            {wsConnected ? 'Live' : 'Disconnected'}
          </span>
        </div>
        <div className="overview__stats">
          <div className="stat-chip">
            <span className="stat-chip__value">{components.length}</span>
            <span className="stat-chip__label">Components</span>
          </div>
          <div className="stat-chip stat-chip--healthy">
            <span className="stat-chip__value">{healthyCount}</span>
            <span className="stat-chip__label">Healthy</span>
          </div>
          <div className="stat-chip">
            <span className="stat-chip__value">{totalRuns}</span>
            <span className="stat-chip__label">Total Runs</span>
          </div>
          {activeRuns > 0 && (
            <div className="stat-chip stat-chip--active">
              <span className="stat-chip__value">{activeRuns}</span>
              <span className="stat-chip__label">Active</span>
            </div>
          )}
        </div>
      </header>

      <section className="overview__health">
        <h2>Components</h2>
        <div className="health-grid">
          {components.map((c: ComponentHealth) => (
            <HealthCard key={c.name} component={c} />
          ))}
          {components.length === 0 && (
            <p className="overview__empty">
              No components configured. Set environment variables like{' '}
              <code>FORGE_DASHBOARD_BULWARK_ROOT</code> to point to your
              repositories.
            </p>
          )}
        </div>
      </section>

      {components.length > 1 && (
        <section className="overview__pipeline">
          <h2>Pipeline</h2>
          <PipelineGraph components={components} compact />
        </section>
      )}

      <section className="overview__events">
        <EventFeed limit={20} />
      </section>

      <section className="overview__actions">
        <h2>Quick Actions</h2>
        <div className="action-bar">
          <Link to="/pipeline" className="action-btn">
            View Pipeline
          </Link>
          <button type="button" className="action-btn action-btn--secondary">
            Retry Failed
          </button>
          <Link to="/pipeline" className="action-btn action-btn--secondary">
            Flow History
          </Link>
        </div>
      </section>
    </div>
  );
}

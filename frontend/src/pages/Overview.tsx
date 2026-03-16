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

  return (
    <div className="overview">
      <header className="overview__header">
        <h1>Forge Dashboard</h1>
        <span
          className={`ws-indicator ${wsConnected ? 'ws-indicator--connected' : 'ws-indicator--disconnected'}`}
        >
          {wsConnected ? 'Live' : 'Disconnected'}
        </span>
      </header>

      <section className="overview__health">
        <h2>Components</h2>
        <div className="health-grid">
          {components.map((c: ComponentHealth) => (
            <HealthCard key={c.name} component={c} />
          ))}
        </div>
      </section>

      <section className="overview__pipeline">
        <h2>Pipeline</h2>
        <PipelineGraph components={components} compact />
      </section>

      <section className="overview__events">
        <EventFeed limit={20} />
      </section>

      <section className="overview__actions">
        <h2>Quick Actions</h2>
        <div className="action-bar">
          <Link to="/pipeline" className="action-btn">
            New Pipeline
          </Link>
          <button type="button" className="action-btn action-btn--secondary">
            Retry Failed
          </button>
          <Link to="/pipeline" className="action-btn action-btn--secondary">
            View History
          </Link>
        </div>
      </section>
    </div>
  );
}

import { Link } from 'react-router-dom';
import type { ComponentHealth } from '../store/dashboard';

const COMPONENT_COLORS: Record<string, string> = {
  crucible: '#74c0fc',
  cartographer: '#b197fc',
  crossfire: '#ffa94d',
  bulwark: '#69db7c',
};

function statusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'healthy':
      return '#69db7c';
    case 'degraded':
      return '#ffd43b';
    case 'down':
    case 'error':
      return '#ff6b6b';
    default:
      return '#868e96';
  }
}

export function HealthCard({ component }: { component: ComponentHealth }) {
  const accent = COMPONENT_COLORS[component.name.toLowerCase()] ?? '#868e96';

  return (
    <Link
      to={`/components/${component.name}`}
      className="health-card"
      style={{ borderColor: accent }}
    >
      <div className="health-card__header">
        <span className="health-card__name" style={{ color: accent }}>
          {component.name}
        </span>
        <span
          className="health-card__badge"
          style={{ backgroundColor: statusColor(component.health.status) }}
        >
          {component.health.status}
        </span>
      </div>
      <div className="health-card__meta">
        <span>v{component.health.version}</span>
        <span>{component.recent_runs} recent runs</span>
      </div>
    </Link>
  );
}

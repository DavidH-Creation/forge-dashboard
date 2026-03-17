import { Link } from 'react-router-dom';
import type { ComponentHealth } from '../store/dashboard';

const DISPLAY_NAMES: Record<string, string> = {
  crucible: 'Crucible',
  cartographer: 'Cartographer',
  crossfire: 'Crossfire',
  bulwark: 'Bulwark',
};

const COMPONENT_COLORS: Record<string, string> = {
  crucible: '#74c0fc',
  cartographer: '#b197fc',
  crossfire: '#ffa94d',
  bulwark: '#69db7c',
};

function statusColor(status: string): string {
  switch (status?.toLowerCase()) {
    case 'healthy':
      return '#69db7c';
    case 'degraded':
      return '#ffd43b';
    case 'down':
    case 'error':
    case 'unavailable':
      return '#ff6b6b';
    default:
      return '#868e96';
  }
}

function runStatusIcon(status: string): string {
  switch (status?.toLowerCase()) {
    case 'complete':
    case 'completed':
    case 'passed':
      return '\u2713';
    case 'running':
    case 'active':
      return '\u25B6';
    case 'failed':
    case 'error':
      return '\u2717';
    default:
      return '\u2022';
  }
}

export function HealthCard({ component }: { component: ComponentHealth }) {
  const key = component.name.toLowerCase();
  const accent = COMPONENT_COLORS[key] ?? '#868e96';
  const displayName = DISPLAY_NAMES[key] ?? component.name;
  const latestRun = component.latest_runs?.[0];

  return (
    <Link
      to={`/components/${component.name}`}
      className="health-card"
      style={{ borderColor: accent }}
    >
      <div className="health-card__header">
        <span className="health-card__name" style={{ color: accent }}>
          {displayName}
        </span>
        <span
          className="health-card__badge"
          style={{ backgroundColor: statusColor(component.health?.status) }}
        >
          {component.health?.status ?? 'unknown'}
        </span>
      </div>

      {latestRun && (
        <div className="health-card__latest">
          <span className={`health-card__run-status health-card__run-status--${latestRun.status?.toLowerCase()}`}>
            {runStatusIcon(latestRun.status)} {latestRun.status}
          </span>
          <div className="health-card__mini-progress">
            <div
              className="health-card__mini-progress-fill"
              style={{
                width: `${Math.round(latestRun.progress * 100)}%`,
                backgroundColor: accent,
              }}
            />
          </div>
        </div>
      )}

      <div className="health-card__meta">
        <span>v{component.health?.version ?? '?'}</span>
        <span>
          {component.recent_runs} {component.recent_runs === 1 ? 'run' : 'runs'}
        </span>
      </div>
    </Link>
  );
}

import { Link } from 'react-router-dom';
import type { ComponentHealth } from '../store/dashboard';

/** Preferred display order when all components are present. */
const PREFERRED_ORDER = ['crucible', 'cartographer', 'crossfire', 'bulwark'];

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

function statusDot(status: string): string {
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

interface PipelineGraphProps {
  components: ComponentHealth[];
  compact?: boolean;
}

export function PipelineGraph({
  components,
  compact = false,
}: PipelineGraphProps) {
  // Sort by preferred order, then alphabetically for unknown components
  const sorted = [...components].sort((a, b) => {
    const ai = PREFERRED_ORDER.indexOf(a.name.toLowerCase());
    const bi = PREFERRED_ORDER.indexOf(b.name.toLowerCase());
    const aIdx = ai >= 0 ? ai : 100;
    const bIdx = bi >= 0 ? bi : 100;
    if (aIdx !== bIdx) return aIdx - bIdx;
    return a.name.localeCompare(b.name);
  });

  if (sorted.length === 0) {
    return (
      <div className="pipeline-graph pipeline-graph--empty">
        <span className="pipeline-graph__empty-text">No components configured</span>
      </div>
    );
  }

  return (
    <div className={`pipeline-graph ${compact ? 'pipeline-graph--compact' : ''}`}>
      {sorted.map((comp, i) => {
        const key = comp.name.toLowerCase();
        const color = COMPONENT_COLORS[key] ?? '#868e96';
        const displayName = DISPLAY_NAMES[key] ?? comp.name;
        const status = comp.health?.status ?? 'unknown';
        const latestRun = comp.latest_runs?.[0];

        return (
          <div key={comp.name} className="pipeline-graph__segment">
            <Link
              to={`/components/${comp.name}`}
              className="pipeline-graph__node"
              style={{ borderColor: color }}
            >
              <span
                className="pipeline-graph__status-dot"
                style={{ backgroundColor: statusDot(status) }}
              />
              <span className="pipeline-graph__label" style={{ color }}>
                {displayName}
              </span>
              {!compact && (
                <span className="pipeline-graph__status-text">
                  {latestRun
                    ? `${latestRun.status} (${Math.round(latestRun.progress * 100)}%)`
                    : status}
                </span>
              )}
            </Link>
            {i < sorted.length - 1 && (
              <span className="pipeline-graph__arrow">&rarr;</span>
            )}
          </div>
        );
      })}
    </div>
  );
}

import type { ComponentHealth } from '../store/dashboard';

const PIPELINE_ORDER = ['Crucible', 'Cartographer', 'Crossfire', 'Bulwark'];

const COMPONENT_COLORS: Record<string, string> = {
  Crucible: '#74c0fc',
  Cartographer: '#b197fc',
  Crossfire: '#ffa94d',
  Bulwark: '#69db7c',
};

function statusDot(status: string): string {
  switch (status?.toLowerCase()) {
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

interface PipelineGraphProps {
  components: ComponentHealth[];
  compact?: boolean;
}

export function PipelineGraph({
  components,
  compact = false,
}: PipelineGraphProps) {
  const lookup = Object.fromEntries(components.map((c) => [c.name, c]));

  return (
    <div className={`pipeline-graph ${compact ? 'pipeline-graph--compact' : ''}`}>
      {PIPELINE_ORDER.map((name, i) => {
        const comp = lookup[name];
        const color = COMPONENT_COLORS[name];
        const status = comp?.health?.status ?? 'unknown';

        return (
          <div key={name} className="pipeline-graph__segment">
            <div
              className="pipeline-graph__node"
              style={{ borderColor: color }}
            >
              <span
                className="pipeline-graph__status-dot"
                style={{ backgroundColor: statusDot(status) }}
              />
              <span className="pipeline-graph__label" style={{ color }}>
                {name}
              </span>
              {!compact && (
                <span className="pipeline-graph__status-text">{status}</span>
              )}
            </div>
            {i < PIPELINE_ORDER.length - 1 && (
              <span className="pipeline-graph__arrow">&rarr;</span>
            )}
          </div>
        );
      })}
    </div>
  );
}

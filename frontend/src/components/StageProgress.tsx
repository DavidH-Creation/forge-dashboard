interface Stage {
  name: string;
  status: string;
  started_at?: string;
  finished_at?: string;
}

interface StageProgressProps {
  stages: Stage[];
  currentStage: string;
}

export function StageProgress({ stages, currentStage }: StageProgressProps) {
  return (
    <div className="stage-progress">
      {stages.map((stage, i) => {
        let state: 'completed' | 'active' | 'pending' = 'pending';
        const s = stage.status?.toLowerCase() ?? '';
        if (s === 'completed' || s === 'complete' || s === 'passed') {
          state = 'completed';
        } else if (s === 'running' || s === 'active' || stage.name === currentStage) {
          state = 'active';
        }

        return (
          <div key={stage.name} className="stage-progress__item">
            <div className={`stage-progress__dot stage-progress__dot--${state}`} />
            <span className="stage-progress__label">{stage.name}</span>
            {stage.started_at && stage.finished_at && (
              <span className="stage-progress__time">
                {formatDuration(stage.started_at, stage.finished_at)}
              </span>
            )}
            {i < stages.length - 1 && (
              <div
                className={`stage-progress__connector ${
                  state === 'completed' ? 'stage-progress__connector--done' : ''
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

function formatDuration(start: string, end: string): string {
  if (!start || !end) return '';
  const ms = new Date(end).getTime() - new Date(start).getTime();
  const secs = Math.floor(ms / 1000);
  if (secs < 60) return `${secs}s`;
  const mins = Math.floor(secs / 60);
  const rem = secs % 60;
  return `${mins}m ${rem}s`;
}

interface StageProgressProps {
  stages: string[];
  currentStage: string;
}

export function StageProgress({ stages, currentStage }: StageProgressProps) {
  const currentIndex = stages.indexOf(currentStage);

  return (
    <div className="stage-progress">
      {stages.map((stage, i) => {
        let state: 'completed' | 'active' | 'pending' = 'pending';
        if (i < currentIndex) state = 'completed';
        else if (i === currentIndex) state = 'active';

        return (
          <div key={stage} className="stage-progress__item">
            <div className={`stage-progress__dot stage-progress__dot--${state}`} />
            <span className="stage-progress__label">{stage}</span>
            {i < stages.length - 1 && (
              <div
                className={`stage-progress__connector ${
                  i < currentIndex ? 'stage-progress__connector--done' : ''
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

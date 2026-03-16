import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchRunDetail, fetchArtifacts } from '../hooks/useApi';
import { StageProgress } from '../components/StageProgress';
import { ArtifactViewer } from '../components/ArtifactViewer';

interface RunInfo {
  run_id: string;
  component: string;
  status: string;
  progress: number;
  current_stage: string;
  stages: string[];
  started_at: string;
  completed_at?: string;
  error?: string;
}

interface Artifact {
  name: string;
  format: string;
  content: string;
}

export function RunDetail() {
  const { name, id } = useParams<{ name: string; id: string }>();
  const [run, setRun] = useState<RunInfo | null>(null);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!name || !id) return;
    Promise.all([fetchRunDetail(name, id), fetchArtifacts(name, id)])
      .then(([runData, artData]) => {
        setRun(runData);
        setArtifacts(artData.artifacts ?? []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [name, id]);

  if (!name || !id) {
    return <div className="page-error">Missing parameters</div>;
  }

  if (loading) {
    return <div className="page-loading">Loading run details...</div>;
  }

  if (error) {
    return <div className="page-error">Error: {error}</div>;
  }

  if (!run) {
    return <div className="page-error">Run not found</div>;
  }

  return (
    <div className="run-detail">
      <header className="run-detail__header">
        <Link to={`/components/${name}`} className="back-link">
          &larr; Back to {name}
        </Link>
        <h1>
          Run {run.run_id.slice(0, 8)}
        </h1>
        <span className={`status-badge status-badge--${run.status.toLowerCase()}`}>
          {run.status}
        </span>
      </header>

      <section className="run-detail__info">
        <dl className="detail-grid">
          <dt>Component</dt>
          <dd>{run.component}</dd>
          <dt>Progress</dt>
          <dd>{run.progress}%</dd>
          <dt>Started</dt>
          <dd>{new Date(run.started_at).toLocaleString()}</dd>
          <dt>Completed</dt>
          <dd>
            {run.completed_at
              ? new Date(run.completed_at).toLocaleString()
              : 'In progress'}
          </dd>
          {run.error && (
            <>
              <dt>Error</dt>
              <dd className="run-detail__error">{run.error}</dd>
            </>
          )}
        </dl>
      </section>

      <section className="run-detail__stages">
        <h2>Stage Timeline</h2>
        <StageProgress
          stages={run.stages ?? []}
          currentStage={run.current_stage}
        />
      </section>

      {artifacts.length > 0 && (
        <section className="run-detail__artifacts">
          <h2>Artifacts</h2>
          {artifacts.map((art) => (
            <ArtifactViewer
              key={art.name}
              name={art.name}
              content={art.content}
              format={art.format}
            />
          ))}
        </section>
      )}
    </div>
  );
}

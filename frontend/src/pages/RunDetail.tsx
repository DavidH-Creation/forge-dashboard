import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchRunDetail, fetchArtifacts } from '../hooks/useApi';
import { StageProgress } from '../components/StageProgress';
import { ArtifactViewer } from '../components/ArtifactViewer';

interface StageRecord {
  name: string;
  status: string;
  started_at?: string;
  finished_at?: string;
}

interface RunInfo {
  run_id: string;
  component: string;
  status: string;
  progress: number;
  current_stage: string;
  stages: StageRecord[];
  started_at: string;
  finished_at?: string;
  metadata?: Record<string, string>;
  error?: string | null;
}

interface Artifact {
  name: string;
  artifact_type: string;
  content_or_path: string;
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
        setArtifacts(Array.isArray(artData) ? artData : []);
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
          Run {run.run_id}
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
          <dd>{Math.round(run.progress * 100)}%</dd>
          <dt>Started</dt>
          <dd>{new Date(run.started_at).toLocaleString()}</dd>
          <dt>Completed</dt>
          <dd>
            {run.finished_at
              ? new Date(run.finished_at).toLocaleString()
              : 'In progress'}
          </dd>
          {run.metadata?.task_contract_name && (
            <>
              <dt>Task</dt>
              <dd>{run.metadata.task_contract_name}</dd>
            </>
          )}
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
              content={art.content_or_path}
              format={art.artifact_type}
            />
          ))}
        </section>
      )}
    </div>
  );
}

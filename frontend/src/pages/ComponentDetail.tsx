import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchRuns } from '../hooks/useApi';

interface Run {
  run_id: string;
  status: string;
  progress: number;
  current_stage: string;
  started_at: string;
  finished_at?: string;
}

export function ComponentDetail() {
  const { name } = useParams<{ name: string }>();
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!name) return;
    fetchRuns(name)
      .then((data) => {
        setRuns(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [name]);

  if (!name) {
    return <div className="page-error">Component not specified</div>;
  }

  return (
    <div className="component-detail">
      <header className="component-detail__header">
        <Link to="/" className="back-link">
          &larr; Back
        </Link>
        <h1>{name}</h1>
      </header>

      <section className="component-detail__runs">
        <h2>Run History</h2>
        {loading && <p className="page-loading">Loading runs...</p>}
        {error && <p className="page-error">Error: {error}</p>}
        {!loading && !error && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Run ID</th>
                <th>Status</th>
                <th>Stage</th>
                <th>Progress</th>
                <th>Started</th>
                <th>Completed</th>
              </tr>
            </thead>
            <tbody>
              {runs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="data-table__empty">
                    No runs found
                  </td>
                </tr>
              ) : (
                runs.map((run) => (
                  <tr key={run.run_id}>
                    <td>
                      <Link
                        to={`/components/${name}/runs/${run.run_id}`}
                        className="data-table__link"
                      >
                        {run.run_id.slice(0, 8)}
                      </Link>
                    </td>
                    <td>
                      <span
                        className={`status-badge status-badge--${run.status.toLowerCase()}`}
                      >
                        {run.status}
                      </span>
                    </td>
                    <td>{run.current_stage}</td>
                    <td>
                      <div className="progress-bar">
                        <div
                          className="progress-bar__fill"
                          style={{ width: `${Math.round(run.progress * 100)}%` }}
                        />
                        <span className="progress-bar__text">
                          {Math.round(run.progress * 100)}%
                        </span>
                      </div>
                    </td>
                    <td>{new Date(run.started_at).toLocaleString()}</td>
                    <td>
                      {run.finished_at
                        ? new Date(run.finished_at).toLocaleString()
                        : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}

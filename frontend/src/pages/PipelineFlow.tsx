import { useEffect, useState } from 'react';
import { fetchFlows } from '../hooks/useApi';
import { useDashboardStore } from '../store/dashboard';
import { PipelineGraph } from '../components/PipelineGraph';

interface Flow {
  flow_id: string;
  status: string;
  started_at: string;
  completed_at?: string;
  stages_completed: number;
  total_stages: number;
}

export function PipelineFlow() {
  const components = useDashboardStore((s) => s.components);
  const [flows, setFlows] = useState<Flow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFlows()
      .then((data) => {
        setFlows(data.flows ?? []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="pipeline-flow-page">
      <h1>Pipeline Flows</h1>

      <section className="pipeline-flow-page__graph">
        <h2>Pipeline Overview</h2>
        <PipelineGraph components={components} />
      </section>

      <section className="pipeline-flow-page__table">
        <h2>Flow History</h2>
        {loading && <p className="page-loading">Loading flows...</p>}
        {error && <p className="page-error">Error: {error}</p>}
        {!loading && !error && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Flow ID</th>
                <th>Status</th>
                <th>Progress</th>
                <th>Started</th>
                <th>Completed</th>
              </tr>
            </thead>
            <tbody>
              {flows.length === 0 ? (
                <tr>
                  <td colSpan={5} className="data-table__empty">
                    No flows found
                  </td>
                </tr>
              ) : (
                flows.map((flow) => (
                  <tr key={flow.flow_id}>
                    <td className="data-table__mono">
                      {flow.flow_id.slice(0, 8)}
                    </td>
                    <td>
                      <span className={`status-badge status-badge--${flow.status.toLowerCase()}`}>
                        {flow.status}
                      </span>
                    </td>
                    <td>
                      {flow.stages_completed}/{flow.total_stages}
                    </td>
                    <td>{new Date(flow.started_at).toLocaleString()}</td>
                    <td>
                      {flow.completed_at
                        ? new Date(flow.completed_at).toLocaleString()
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

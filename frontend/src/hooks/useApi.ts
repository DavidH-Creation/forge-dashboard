const API_KEY = import.meta.env.VITE_FORGE_DASHBOARD_API_KEY as string | undefined;

function authHeaders(): HeadersInit {
  return API_KEY ? { Authorization: `Bearer ${API_KEY}` } : {};
}

export async function fetchOverview() {
  const resp = await fetch('/api/overview', { headers: authHeaders() });
  return resp.json();
}

export async function fetchRuns(component: string) {
  const resp = await fetch(`/api/components/${component}/runs`, {
    headers: authHeaders(),
  });
  return resp.json();
}

export async function fetchRunDetail(component: string, runId: string) {
  const resp = await fetch(`/api/components/${component}/runs/${runId}`, {
    headers: authHeaders(),
  });
  return resp.json();
}

export async function fetchArtifacts(component: string, runId: string) {
  const resp = await fetch(
    `/api/components/${component}/runs/${runId}/artifacts`,
    { headers: authHeaders() },
  );
  return resp.json();
}

export async function fetchFlows() {
  const resp = await fetch('/api/pipeline/flows', { headers: authHeaders() });
  return resp.json();
}

export async function fetchEvents(since?: string) {
  const url = since
    ? `/api/events?since=${encodeURIComponent(since)}`
    : '/api/events';
  const resp = await fetch(url, { headers: authHeaders() });
  return resp.json();
}

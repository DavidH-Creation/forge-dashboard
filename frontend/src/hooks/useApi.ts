export async function fetchOverview() {
  const resp = await fetch('/api/overview');
  return resp.json();
}

export async function fetchRuns(component: string) {
  const resp = await fetch(`/api/components/${component}/runs`);
  return resp.json();
}

export async function fetchRunDetail(component: string, runId: string) {
  const resp = await fetch(`/api/components/${component}/runs/${runId}`);
  return resp.json();
}

export async function fetchArtifacts(component: string, runId: string) {
  const resp = await fetch(
    `/api/components/${component}/runs/${runId}/artifacts`,
  );
  return resp.json();
}

export async function fetchFlows() {
  const resp = await fetch('/api/pipeline/flows');
  return resp.json();
}

export async function fetchEvents(since?: string) {
  const url = since
    ? `/api/events?since=${encodeURIComponent(since)}`
    : '/api/events';
  const resp = await fetch(url);
  return resp.json();
}

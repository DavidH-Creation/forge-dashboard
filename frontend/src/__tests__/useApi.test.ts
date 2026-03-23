import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Helper to set VITE env var inside the module under test
async function importApi(apiKey?: string) {
  vi.resetModules();
  vi.stubEnv('VITE_FORGE_DASHBOARD_API_KEY', apiKey ?? '');
  const mod = await import('../hooks/useApi');
  return mod;
}

beforeEach(() => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue({
    json: () => Promise.resolve({}),
  } as Response);
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllEnvs();
});

describe('useApi — no API key', () => {
  it('fetchOverview sends no Authorization header', async () => {
    const { fetchOverview } = await importApi();
    await fetchOverview();
    const [, init] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [
      string,
      RequestInit,
    ];
    expect((init?.headers as Record<string, string>)?.Authorization).toBeUndefined();
  });
});

describe('useApi — with API key', () => {
  it('fetchOverview sends Authorization: Bearer header', async () => {
    const { fetchOverview } = await importApi('my-secret');
    await fetchOverview();
    const [, init] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [
      string,
      RequestInit,
    ];
    expect((init?.headers as Record<string, string>).Authorization).toBe(
      'Bearer my-secret',
    );
  });

  it('fetchRuns sends Authorization header', async () => {
    const { fetchRuns } = await importApi('my-secret');
    await fetchRuns('bulwark');
    const [, init] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [
      string,
      RequestInit,
    ];
    expect((init?.headers as Record<string, string>).Authorization).toBe(
      'Bearer my-secret',
    );
  });

  it('fetchEvents sends Authorization header', async () => {
    const { fetchEvents } = await importApi('my-secret');
    await fetchEvents();
    const [, init] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [
      string,
      RequestInit,
    ];
    expect((init?.headers as Record<string, string>).Authorization).toBe(
      'Bearer my-secret',
    );
  });
});

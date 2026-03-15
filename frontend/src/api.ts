const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function fetchApi(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function listArchitectures(skip = 0, limit = 50) {
  return fetchApi(`/architectures?skip=${skip}&limit=${limit}`);
}

export async function getArchitecture(id: string) {
  return fetchApi(`/architectures/${id}`);
}

export async function triggerScrape() {
  return fetchApi('/architectures/scrape', { method: 'POST' });
}

export interface RecommendRequest {
  use_case: string;
  scale: string;
  traffic_pattern: string;
  latency_sensitivity: string;
  processing_style: string;
  data_intensity: string;
  availability_requirement: string;
  ops_preference: string;
  budget_sensitivity: string;
}

export async function recommend(req: RecommendRequest) {
  return fetchApi('/recommend', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

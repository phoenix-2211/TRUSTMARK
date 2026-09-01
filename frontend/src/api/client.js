const API_BASE = '/api';

export async function fetchDisputes() {
  const res = await fetch(`${API_BASE}/disputes`);
  if (!res.ok) throw new Error('Failed to fetch disputes');
  return res.json();
}

export async function fetchDisputeDetail(id) {
  const res = await fetch(`${API_BASE}/disputes/${id}`);
  if (!res.ok) throw new Error('Failed to fetch dispute detail');
  return res.json();
}

export async function fetchEvalReport() {
  const res = await fetch(`${API_BASE}/eval/report`);
  if (!res.ok) throw new Error('Failed to fetch evaluation report');
  return res.json();
}

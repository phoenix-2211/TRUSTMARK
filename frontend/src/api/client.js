/**
 * MerchantGuard Frontend API Client.
 * Communicates with FastAPI backend endpoints (/api/disputes, /api/webhooks, /api/eval/report).
 * Configurable via import.meta.env.VITE_API_BASE_URL.
 */

const ENV_API_BASE = import.meta.env.VITE_API_BASE_URL ? import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '') : '';
const API_BASE = ENV_API_BASE ? `${ENV_API_BASE}/api` : '/api';
const DIRECT_API_BASE = 'http://127.0.0.1:8000/api';

async function safeFetch(endpoint) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn(`Primary fetch to ${API_BASE}${endpoint} failed, attempting direct fallback...`, err);
  }

  // Fallback to direct backend URL if primary relative/env fetch failed
  const resDirect = await fetch(`${DIRECT_API_BASE}${endpoint}`);
  if (!resDirect.ok) {
    throw new Error(`API Error: ${resDirect.status} ${resDirect.statusText}`);
  }
  return await resDirect.json();
}

export async function fetchDisputes(skip = 0, limit = 50) {
  return await safeFetch(`/disputes?skip=${skip}&limit=${limit}`);
}

export async function fetchDisputeDetail(disputeId) {
  return await safeFetch(`/disputes/${disputeId}`);
}

export async function recheckDispute(disputeId) {
  try {
    const res = await fetch(`${API_BASE}/disputes/${disputeId}/recheck`, { method: 'POST' });
    if (res.ok) return await res.json();
  } catch (e) {}

  const resDirect = await fetch(`${DIRECT_API_BASE}/disputes/${disputeId}/recheck`, { method: 'POST' });
  if (!resDirect.ok) {
    throw new Error(`API Error: ${resDirect.status} ${resDirect.statusText}`);
  }
  return await resDirect.json();
}

export async function fetchEvalReport() {
  return await safeFetch('/eval/report');
}
